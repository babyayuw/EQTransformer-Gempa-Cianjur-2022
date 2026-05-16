import pandas as pd
import glob, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from obspy import read, UTCDateTime
import math
import datetime

EP_LAT = -6.853
EP_LON = 107.095

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

# ── Origin time & window ───────────────────────────────────────────────────────
ORIGIN_UTC = datetime.datetime(2022, 11, 21, 6, 21, 10)   # 06:21:10 UTC

# -20 s sebelum origin  →  +100 s setelah origin
XMIN = ORIGIN_UTC - datetime.timedelta(seconds=20)   # 06:20:50
XMAX = ORIGIN_UTC + datetime.timedelta(seconds=100)  # 06:22:50

T1 = UTCDateTime(XMIN)
T2 = UTCDateTime(XMAX)

station_data = []

for sta, coords in station_coords.items():
    if sta in skip:
        continue

    lat, lon = coords
    dist = haversine(EP_LAT, EP_LON, lat, lon)

    mseed_file = os.path.join(mseed_dir, f"IA.{sta}.preprocessed.mseed")
    if not os.path.exists(mseed_file):
        continue

    try:
        st = read(mseed_file)
        tr = st.select(channel="*Z")[0].slice(T1, T2)
        if tr is None or len(tr.data) == 0:
            continue

        data = tr.data.astype(float)
        maxval = np.max(np.abs(data))
        if maxval > 0:
            data = data / maxval

        t0 = tr.stats.starttime.datetime
        dt = 1.0 / tr.stats.sampling_rate
        times_dt = [t0 + datetime.timedelta(seconds=i * dt) for i in range(len(data))]

        station_data.append({
            'sta': sta, 'dist': dist,
            'times': times_dt, 'data': data,
        })
        print(f"  OK: {sta} — {dist:.1f} km")

    except Exception as e:
        print(f"  Error {sta}: {e}")

station_data.sort(key=lambda x: x['dist'])

# ── Parameter plot ─────────────────────────────────────────────────────────────
scale   = 2.5
spacing = 3.0
clip    = 0.85

n_sta  = len(station_data)
fig_h  = max(8, n_sta * 0.23 + 1.8)
fig_w  = 14

fig, ax = plt.subplots(figsize=(fig_w, fig_h))

for i, sd in enumerate(station_data):
    offset = i * spacing

    wave = np.clip(
        np.array(sd['data']) * scale,
        -spacing * clip / 2,
         spacing * clip / 2
    ) + offset

    ax.plot(sd['times'], wave, 'k-', linewidth=0.4, alpha=0.9)

    # Label stasiun di dalam plot, sisi kiri, sejajar waveform
    ax.text(
        XMIN, offset,
        f"{sd['sta']} ({sd['dist']:.2f} km)",
        fontsize=7.5,
        fontweight='bold',
        va='center',
        ha='left',
        color='#111111',
        bbox=dict(
            boxstyle='round,pad=0.25',
            facecolor='#FFF9C4',
            edgecolor='#F9A825',
            linewidth=0.6,
            alpha=0.95
        ),
        zorder=5,
        clip_on=False
    )

# ── Garis origin time ──────────────────────────────────────────────────────────
origin_line = ax.axvline(
    ORIGIN_UTC,
    color='#D32F2F',
    linewidth=1.3,
    linestyle='--',
    zorder=4,
    label='Origin time (06:21:10 UTC)'
)

# ── Legend ─────────────────────────────────────────────────────────────────────
ax.legend(
    handles=[origin_line],
    loc='upper right',
    fontsize=9,
    framealpha=0.92,
    edgecolor='#BBBBBB'
)

# ── Sumbu X: label tiap 10 detik, format HH:MM:SS ─────────────────────────────
ax.xaxis.set_major_locator(mdates.SecondLocator(bysecond=range(0, 60, 10)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=8.5)

ax.set_xlim(XMIN, XMAX)

# ── Sumbu Y ────────────────────────────────────────────────────────────────────
ax.set_yticks([])
ax.set_yticklabels([])

ax.set_xlabel("Waktu (UTC)", fontsize=11, labelpad=6)
ax.set_title(
    "Waveform Plot — Gempa Cianjur Mw 5.6\n"
    "21 November 2022, 06:21:10 UTC (13:21:10 WIB)",
    fontsize=12, fontweight='bold', pad=8
)

ax.grid(axis='x', linestyle=':', alpha=0.35)
plt.tight_layout()

out = os.path.join(output_dir, "waveform_plot_cianjur.png")
plt.savefig(out, dpi=250, bbox_inches='tight')
plt.close()
print(f"\nSaved: {out}")
