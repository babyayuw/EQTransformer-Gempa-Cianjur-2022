from obspy import read

f = r"D:\BMKG\EQTransformer\Dataset gempa utama cianjur\IA.LEM..SHZ.D.2022.325"
st = read(f)
print(st)
print("\nDetail trace pertama:")
tr = st[0]
print(f"  Stasiun   : {tr.stats.network}.{tr.stats.station}")
print(f"  Channel   : {tr.stats.channel}")
print(f"  Sampling  : {tr.stats.sampling_rate} Hz")
print(f"  Mulai     : {tr.stats.starttime}")
print(f"  Selesai   : {tr.stats.endtime}")
print(f"  Durasi    : {tr.stats.endtime - tr.stats.starttime:.1f} detik")