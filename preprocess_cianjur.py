from obspy import read, Stream
import os
import glob

def preprocess_station_sds(folder_path, station_code):
    pattern = os.path.join(folder_path, f"IA.{station_code}*")
    files = sorted(glob.glob(pattern))

    if not files:
        return None

    st = Stream()
    for f in files:
        try:
            st += read(f)
        except Exception as e:
            print(f"  Error baca {os.path.basename(f)}: {e}")

    if len(st) == 0:
        return None

    sr = st[0].stats.sampling_rate
    nyquist = sr / 2
    freqmax = min(45.0, nyquist * 0.9)

    try:
        st.merge(method=1, fill_value='interpolate', interpolation_samples=-1)
        st.detrend('demean')
        st.detrend('linear')
        st.taper(max_percentage=0.05, type='cosine')
        st.filter('bandpass', freqmin=1.0, freqmax=freqmax, corners=4, zerophase=True)
        for tr in st:
            if tr.stats.sampling_rate != 100.0:
                tr.resample(100.0)
    except Exception as e:
        print(f"  Error proses {station_code}: {e}")
        return None

    return st

# ── Setup ──────────────────────────────────────────────
folder  = r"D:\BMKG\EQTransformer\Dataset gempa utama cianjur"
out_dir = r"D:\BMKG\EQTransformer\preprocessed_cianjur"
os.makedirs(out_dir, exist_ok=True)

# Ambil daftar stasiun unik dari nama file
all_files = glob.glob(os.path.join(folder, "IA.*"))
stations  = sorted(set(os.path.basename(f).split(".")[1] for f in all_files))
print(f"Total stasiun ditemukan: {len(stations)}")
print(f"Output folder: {out_dir}\n")

# ── Proses semua stasiun ───────────────────────────────
berhasil, gagal = [], []

for sta in stations:
    print(f"Memproses {sta}...", end=" ")
    st = preprocess_station_sds(folder, sta)
    if st is None:
        print("GAGAL")
        gagal.append(sta)
        continue

    # Simpan ke satu file .mseed per stasiun
    out_file = os.path.join(out_dir, f"IA.{sta}.preprocessed.mseed")
    st.write(out_file, format="MSEED")
    print(f"OK ({len(st)} trace) → {os.path.basename(out_file)}")
    berhasil.append(sta)

# ── Ringkasan ──────────────────────────────────────────
print(f"\n{'='*50}")
print(f"Selesai! Berhasil: {len(berhasil)}, Gagal: {len(gagal)}")
if gagal:
    print(f"Stasiun gagal: {', '.join(gagal)}")