import pandas as pd
import glob, os

detections_dir = r"D:\BMKG\EQTransformer\detections_cianjur"
csv_files = glob.glob(os.path.join(detections_dir, "*_outputs", "*_prediction_results.csv"))

print(f"Ditemukan {len(csv_files)} file CSV\n")
print(f"{'Stasiun':<8} {'Total':>6} {'13:00-14:00 UTC':>16} {'P arrival terkuat'}")
print("-"*60)

for f in sorted(csv_files):
    sta = os.path.basename(os.path.dirname(f)).replace("_outputs","")
    df = pd.read_csv(f)
    df['event_start_time'] = pd.to_datetime(df['event_start_time'])

    # Filter 13:00–14:00 UTC (sekitar gempa utama Cianjur)
    event = df[(df['event_start_time'].dt.hour >= 13) &
               (df['event_start_time'].dt.hour < 14)]

    if len(event) > 0:
        # Ambil deteksi dengan probabilitas tertinggi
        best = event.loc[event['detection_probability'].idxmax()]
        print(f"{sta:<8} {len(df):>6} {len(event):>16}   {best['p_arrival_time']} (prob={best['detection_probability']:.2f})")
    else:
        print(f"{sta:<8} {len(df):>6} {len(event):>16}   -")