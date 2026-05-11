import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from obspy import read, UTCDateTime
import math
import datetime

# ── Konfigurasi ─────────────────────────────────────────────────────────────
EP_LAT = -6.862
EP_LON = 107.059

station_coords = {
    "ACJM": [-6.8033,  108.6151],
    "BBJI": [-7.5557,  107.815],
    "BKJI": [-7.3633,  108.5322],
    "CBJI": [-6.6981,  106.9349],
    "CGJI": [-6.6134,  105.6929],
    "CIJI": [-7.31741, 108.19589],
    "CIJM": [-6.4926,  108.1853],
    "CMJI": [-7.7837,  108.4486],
    "CNJI": [-7.3091,  107.1296],
    "CSJI": [-7.3301,  106.52107],
    "CSJM": [-6.7405,  108.0099],
    "CTJI": [-7.0075,  109.1835],
    "CWJM": [-6.7423,  107.4448],
    "DBJI": [-6.5542,  106.7436],
    "JBJI": [-6.483735,106.4698517],
    "JPJI": [-6.5306,  107.41757],
    "JTJM": [-7.0573,  106.8015],
    "KPJI": [-7.3332,  108.9312],
    "LEM":  [-6.8266,  107.6175],
    "PBJI": [-7.0874,  107.4757],
    "PKJM": [-6.7988,  108.445],
    "PSLI": [-5.93732, 105.51004],
    "PTJI": [-6.255535,106.748825],
    "SCJI": [-7.681,   109.1689],
    "TNGI": [-6.172,   106.647],
    "TSJM": [-6.7319,  107.8109],
    "WSJM": [-6.9748,  106.7249],
}

skip = ["PCJM","PSJM","SADLY","SBJI","SKJI","TOJI","WLJI","CBJM"]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))

mseed_dir  = r"D:\BMKG\EQTransformer\preprocessed_cianjur"
output_dir = r"D:\BMKG\EQTransformer\plots_gempa_utama"
os.makedirs(output_dir, exist_ok=True)

# Window: 30 detik sebelum hingga 150 detik sesudah origin time
ORIGIN = UTCDateTime("2022-11-21T06:21:10")
T1     = ORIGIN - 30
T2     = ORIGIN + 150

# ── Kumpulkan data ───────────────────────────────────────────────────────────
station_data = []

for sta, (lat, lon) in station_coords.items():
    if sta in skip:
        continue

    mseed_file = os.path.join(mseed_dir, f"IA.{sta}.preprocessed.mseed")
    if not os.path.exists(mseed_file):
        print(f"  Skip {sta}: mseed tidak ada")
        continue

    dist = haversine(EP_LAT, EP_LON, lat, lon)

    try:
        st = read(mseed_file)
        sel = st.select(channel="*Z")
        if not sel:
            print(f"  Skip {sta}: channel Z tidak ada")
            continue

        tr = sel[0].slice(T1, T2)
        if tr is None or len(tr.data) == 0:
            print(f"  Skip {sta}: data kosong di window")
            continue

        # Waktu absolut sebagai array datetime
        sr    = tr.stats.sampling_rate
        t0_dt = tr.stats.starttime.datetime.replace(tzinfo=datetime.timezone.utc)
        times = [t0_dt + datetime.timedelta(seconds=i / sr)
                 for i in range(len(tr.data))]

        station_data.append({
            'sta':   sta,
            'dist':  dist,
            'times': times,
            'data':  tr.data.astype(float),
        })
        print(f"  OK: {sta} — {dist:.1f} km")

    except Exception as e:
        print(f"  Error {sta}: {e}")

station_data.sort(key=lambda x: x['dist'])
print(f"\nTotal stasiun: {len(station_data)}")

# ── Plot ─────────────────────────────────────────────────────────────────────
n      = len(station_data)
height = max(n * 1.1, 12)

fig, axes = plt.subplots(
    nrows=n, ncols=1,
    figsize=(13, height),
    sharex=True
)

if n == 1:
    axes = [axes]

origin_dt = ORIGIN.datetime.replace(tzinfo=datetime.timezone.utc)

for ax, sd in zip(axes, station_data):
    data  = sd['data']
    times = sd['times']

    ax.plot(times, data, 'k-', linewidth=0.5)

    # Sumbu Y: raw counts, format ribuan
    maxval = np.max(np.abs(data))
    ax.set_ylim(-maxval * 1.3, maxval * 1.3)

    # Label Y: nama stasiun + jarak di kiri, skala amplitudo di kanan
    ax.set_ylabel(f"{sd['sta']}\n({sd['dist']:.0f} km)",
                  fontsize=6, rotation=0, labelpad=45,
                  va='center', ha='right')

    # Tick Y: hanya min dan max (raw counts)
    ax.set_yticks([-maxval, 0, maxval])
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}k" if abs(x) >= 1000 else f"{x:.0f}")
    )
    ax.tick_params(axis='y', labelsize=5, length=2)

    # Garis origin time
    ax.axvline(origin_dt, color='red', linewidth=0.8, linestyle='--', alpha=0.7)

    # Border minimalis
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.4)
    ax.spines['bottom'].set_linewidth(0.4)
    ax.tick_params(axis='x', labelsize=7, length=2)

# ── Sumbu X: waktu absolut UTC ───────────────────────────────────────────────
axes[-1].xaxis.set_major_formatter(
    mdates.DateFormatter('%H:%M:%S', tz=datetime.timezone.utc)
)
axes[-1].xaxis.set_major_locator(mdates.SecondLocator(interval=30))
axes[-1].set_xlabel("Waktu (UTC)", fontsize=9)

# ── X limits ────────────────────────────────────────────────────────────────
x_start = origin_dt - datetime.timedelta(seconds=30)
x_end   = origin_dt + datetime.timedelta(seconds=150)
axes[-1].set_xlim(x_start, x_end)

# ── Judul ────────────────────────────────────────────────────────────────────
fig.suptitle(
    "Waveform Plot — Gempa Cianjur Mw 5.6\n"
    "21 November 2022, 06:21:10 UTC (13:21:10 WIB)",
    fontsize=11, y=1.001
)

plt.tight_layout()
plt.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.04, hspace=0)

out = os.path.join(output_dir, "waveform_plot_cianjur.png")
plt.savefig(out, dpi=200, bbox_inches='tight')
plt.close()
print(f"\nSaved: {out}")