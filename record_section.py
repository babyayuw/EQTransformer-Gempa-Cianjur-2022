import pandas as pd
import glob, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from obspy import read, UTCDateTime
import math

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
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

detections_dir = r"D:\BMKG\EQTransformer\detections_cianjur"
mseed_dir      = r"D:\BMKG\EQTransformer\preprocessed_cianjur"
output_dir     = r"D:\BMKG\EQTransformer\plots_gempa_utama"
os.makedirs(output_dir, exist_ok=True)

# Window waveform: 30 detik sebelum hingga 150 detik sesudah origin time
T1      = UTCDateTime("2022-11-21T06:20:40")  # -30 detik
T2      = UTCDateTime("2022-11-21T06:23:40")  # +150 detik
EQ_TIME = pd.Timestamp("2022-11-21 06:21:10")

csv_files = glob.glob(os.path.join(detections_dir, "*_outputs", "*_prediction_results.csv"))
station_data = []

for f in sorted(csv_files):
    sta = os.path.basename(os.path.dirname(f)).replace("_outputs","")
    if sta in skip or sta not in station_coords:
        continue

    lat, lon = station_coords[sta]
    dist = haversine(EP_LAT, EP_LON, lat, lon)

    df = pd.read_csv(f)
    df['event_start_time'] = pd.to_datetime(df['event_start_time'])
    df['p_arrival_time']   = pd.to_datetime(df['p_arrival_time'])
    df['s_arrival_time']   = pd.to_datetime(df['s_arrival_time'])

    # Window picks: sedikit lebih lebar dari waveform agar tidak ada yang kelewat
    event = df[(df['event_start_time'] >= "2022-11-21 06:19:00") &
               (df['event_start_time'] <= "2022-11-21 06:24:00") &
               (df['detection_probability'] >= 0.7)]

    p_picks, s_picks = [], []
    for _, row in event.iterrows():
        if pd.notna(row['p_arrival_time']):
            p_sec = (row['p_arrival_time'] - EQ_TIME).total_seconds()
            if -30 <= p_sec <= 150:
                p_picks.append(p_sec)
        if pd.notna(row['s_arrival_time']):
            s_sec = (row['s_arrival_time'] - EQ_TIME).total_seconds()
            if -30 <= s_sec <= 150:
                s_picks.append(s_sec)

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

        starttime = tr.stats.starttime.datetime
        times_sec = [(starttime + pd.Timedelta(seconds=i/tr.stats.sampling_rate) - EQ_TIME).total_seconds()
                     for i in range(len(data))]

        station_data.append({
            'sta': sta, 'dist': dist,
            'times': times_sec, 'data': data,
            'p_picks': p_picks, 's_picks': s_picks
        })
        print(f"  OK: {sta} — {dist:.1f} km | {len(p_picks)} P, {len(s_picks)} S")

    except Exception as e:
        print(f"  Error {sta}: {e}")

station_data.sort(key=lambda x: x['dist'])

# ── Plot ───────────────────────────────────────────────
scale   = 7
spacing = 20
clip    = 0.85

fig, ax = plt.subplots(figsize=(12, len(station_data) * 0.7 + 1))

p_label_done = False
s_label_done = False

for i, sd in enumerate(station_data):
    offset = i * spacing

    wave = np.clip(np.array(sd['data']) * scale,
                   -spacing * clip / 2,
                    spacing * clip / 2) + offset

    ax.plot(sd['times'], wave, 'k-', linewidth=0.6, alpha=0.9)

    pick_half = spacing * 0.15

    for p in sd['p_picks']:
        ax.vlines(p, offset - pick_half, offset + pick_half,
                  colors='blue', linewidth=1.0, alpha=0.85,
                  label='P pick' if not p_label_done else "")
        p_label_done = True

    for s in sd['s_picks']:
        ax.vlines(s, offset - pick_half, offset + pick_half,
                  colors='red', linewidth=1.0, alpha=0.85,
                  label='S pick' if not s_label_done else "")
        s_label_done = True

    ax.text(-29, offset + spacing * 0.35,
            f"{sd['sta']} ({sd['dist']:.0f} km)",
            fontsize=6.5, va='bottom', ha='left', color='black',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFF8DC',
                      edgecolor='none', alpha=0.9))

ax.axvline(0, color='green', linewidth=1.5, linestyle='--',
           label='Origin time (06:21:10 UTC)')

yticks      = [i * spacing for i in range(len(station_data))]
yticklabels = [f"{sd['dist']:.0f}" for sd in station_data]
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels, fontsize=7)

ax.set_xlabel("Waktu relatif terhadap origin time (detik)", fontsize=11)
ax.set_ylabel("Jarak epicenter (km)", fontsize=11)
ax.set_title("Record Section — Gempa Cianjur Mw 5.6\n"
             "21 November 2022, 06:21:10 UTC (13:21:10 WIB)", fontsize=12)
ax.legend(loc='upper right', fontsize=9)
ax.set_xlim(-30, 150)
ax.grid(axis='x', linestyle=':', alpha=0.4)
plt.tight_layout()

out = os.path.join(output_dir, "record_section_cianjur.png")
plt.savefig(out, dpi=200, bbox_inches='tight')
plt.close()
print(f"\nSaved: {out}")