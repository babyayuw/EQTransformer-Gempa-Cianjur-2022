import pandas as pd
import glob, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from obspy import read, UTCDateTime

# ── Setup ──────────────────────────────────────────────
detections_dir = r"D:\BMKG\EQTransformer\detections_cianjur"
mseed_dir      = r"D:\BMKG\EQTransformer\preprocessed_cianjur"
output_plot    = r"D:\BMKG\EQTransformer\plots_gempa_utama"
output_excel   = r"D:\BMKG\EQTransformer\hasil_eqt_cianjur.xlsx"
os.makedirs(output_plot, exist_ok=True)

csv_files = glob.glob(os.path.join(detections_dir, "*_outputs", "*_prediction_results.csv"))
skip = ["PCJM","PSJM","SADLY","SBJI","SKJI","TOJI","WLJI","CBJM"]

# Gempa utama: 13:21:10 WIB = 06:21:10 UTC
# Window filter: 06:00–07:00 UTC
# Window plot  : 06:00–07:00 UTC
T1_UTC = UTCDateTime("2022-11-21T06:00:00")
T2_UTC = UTCDateTime("2022-11-21T07:00:00")

# ── Export tabel gabungan ──────────────────────────────
print("Membuat tabel Excel...")
all_dfs = []
for f in sorted(csv_files):
    df = pd.read_csv(f)
    df['event_start_time'] = pd.to_datetime(df['event_start_time'])
    df['p_arrival_time']   = pd.to_datetime(df['p_arrival_time'])
    df['s_arrival_time']   = pd.to_datetime(df['s_arrival_time'])

    df_clean = df[['station','event_start_time','event_end_time',
                   'detection_probability',
                   'p_arrival_time','p_probability','p_snr',
                   's_arrival_time','s_probability','s_snr']].copy()
    all_dfs.append(df_clean)

df_all = pd.concat(all_dfs, ignore_index=True)

# Tambah kolom waktu WIB untuk kemudahan baca
df_all['event_start_WIB'] = df_all['event_start_time'] + pd.Timedelta(hours=7)
df_all['p_arrival_WIB']   = df_all['p_arrival_time']   + pd.Timedelta(hours=7)
df_all['s_arrival_WIB']   = df_all['s_arrival_time']   + pd.Timedelta(hours=7)

df_all.to_excel(output_excel, index=False)
print(f"Tabel disimpan: {output_excel} ({len(df_all)} baris)\n")

# ── Plot sekitar gempa utama per stasiun ───────────────
print("Membuat plot gempa utama (06:00–07:00 UTC / 13:00–14:00 WIB)...")

for f in sorted(csv_files):
    sta = os.path.basename(os.path.dirname(f)).replace("_outputs","")

    if sta in skip:
        print(f"  Skip {sta} (data 2023 atau timestamp bermasalah)")
        continue

    df = pd.read_csv(f)
    df['event_start_time'] = pd.to_datetime(df['event_start_time'])
    df['p_arrival_time']   = pd.to_datetime(df['p_arrival_time'])
    df['s_arrival_time']   = pd.to_datetime(df['s_arrival_time'])

    # Filter deteksi 06:00–07:00 UTC
    event = df[(df['event_start_time'].dt.hour == 6) &
               (df['event_start_time'].dt.hour < 7)]

    if len(event) == 0:
        print(f"  {sta}: tidak ada deteksi 06:00-07:00 UTC")
        continue

    mseed_file = os.path.join(mseed_dir, f"IA.{sta}.preprocessed.mseed")
    if not os.path.exists(mseed_file):
        print(f"  {sta}: file mseed tidak ditemukan")
        continue

    try:
        st = read(mseed_file)
        tr_z = st.select(channel="*Z")[0]
        tr_z = tr_z.slice(T1_UTC, T2_UTC)

        if tr_z is None or len(tr_z.data) == 0:
            print(f"  {sta}: data kosong di window 06:00-07:00 UTC")
            continue

        times = tr_z.times("matplotlib")
        data  = tr_z.data

        fig, ax = plt.subplots(figsize=(14, 4))
        ax.plot(times, data, 'k-', linewidth=0.4, label='Waveform Z')

        # Tandai gempa utama
        eq_time = mdates.date2num(
            pd.Timestamp("2022-11-21 06:21:10").to_pydatetime()
        )
        ax.axvline(eq_time, color='green', linewidth=1.5,
                   linestyle='--', label='Gempa utama (06:21:10 UTC)')

        # Plot P dan S picks
        p_plotted, s_plotted = False, False
        for _, row in event.iterrows():
            if pd.notna(row['p_arrival_time']):
                pt = mdates.date2num(row['p_arrival_time'].to_pydatetime())
                ax.axvline(pt, color='blue', linewidth=1.0, alpha=0.6,
                           label='P pick' if not p_plotted else "")
                p_plotted = True
            if pd.notna(row['s_arrival_time']):
                st2 = mdates.date2num(row['s_arrival_time'].to_pydatetime())
                ax.axvline(st2, color='red', linewidth=1.0, alpha=0.6,
                           label='S pick' if not s_plotted else "")
                s_plotted = True

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate(rotation=45)
        ax.legend(fontsize=8)
        ax.set_title(f"Stasiun {sta} — 21 Nov 2022, 06:00–07:00 UTC (13:00–14:00 WIB) | Komponen Z")
        ax.set_xlabel("Waktu (UTC)")
        ax.set_ylabel("Amplitudo")
        plt.tight_layout()

        out_png = os.path.join(output_plot, f"{sta}_gempa_utama.png")
        plt.savefig(out_png, dpi=150)
        plt.close()
        print(f"  {sta}: {len(event)} picks → saved")

    except Exception as e:
        print(f"  {sta}: Error — {e}")

print("\nSelesai!")