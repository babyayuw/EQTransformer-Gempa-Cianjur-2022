import pandas as pd
import glob, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from obspy import read, UTCDateTime

mseed_dir      = r"D:\BMKG\EQTransformer\preprocessed_cianjur"
detections_dir = r"D:\BMKG\EQTransformer\detections_cianjur"
output_dir     = r"D:\BMKG\EQTransformer\plots_eqt_style"
os.makedirs(output_dir, exist_ok=True)

ORIGIN_UTC = UTCDateTime("2022-11-21T06:21:10")
EQ_TIME    = pd.Timestamp("2022-11-21 06:21:10")

valid = [
    "ACJM","BBJI","BKJI","CBJI","CGJI","CIJI","CIJM","CMJI","CNJI",
    "CSJI","CSJM","CTJI","CWJM","DBJI","JBJI","JPJI","JTJM","KPJI",
    "LEM","PBJI","PKJM","PSLI","PTJI","SCJI","TNGI","TSJM","WSJM"
]

C_P   = '#00BFFF'
C_S   = '#FF00FF'
C_DET = '#00CC44'

for sta in valid:
    mseed_file = os.path.join(mseed_dir, f"IA.{sta}.preprocessed.mseed")
    csv_files  = glob.glob(os.path.join(detections_dir, f"{sta}_outputs",
                                        "*_prediction_results.csv"))

    if not os.path.exists(mseed_file):
        print(f"  Skip {sta}: mseed tidak ada")
        continue
    if not csv_files:
        print(f"  Skip {sta}: CSV tidak ada")
        continue

    try:
        df = pd.read_csv(csv_files[0])
        df['station']          = df['station'].str.strip()
        df['event_start_time'] = pd.to_datetime(df['event_start_time'])
        df['p_arrival_time']   = pd.to_datetime(df['p_arrival_time'], errors='coerce')
        df['s_arrival_time']   = pd.to_datetime(df['s_arrival_time'], errors='coerce')

        df_valid = df[df['detection_probability'] >= 0.5].copy()
        df_valid['dist_to_eq'] = (
            df_valid['event_start_time'] - EQ_TIME
        ).abs().dt.total_seconds()

        if len(df_valid) == 0:
            print(f"  Skip {sta}: tidak ada deteksi valid")
            continue

        best       = df_valid.loc[df_valid['dist_to_eq'].idxmin()]
        p_time_utc = best['p_arrival_time'] if pd.notna(best['p_arrival_time']) else None
        s_time_utc = best['s_arrival_time'] if pd.notna(best['s_arrival_time']) else None
        det_prob   = float(best['detection_probability'])
        p_prob     = float(best['p_probability']) if pd.notna(best['p_probability']) else 0
        s_prob     = float(best['s_probability']) if pd.notna(best['s_probability']) else 0

        # ── Tentukan window berdasarkan pick yang tersedia ──────────────
        if p_time_utc is not None:
            win_start = UTCDateTime(p_time_utc.to_pydatetime()) - 10
            win_end   = UTCDateTime(p_time_utc.to_pydatetime()) + 150
        elif s_time_utc is not None:
            print(f"  Warning {sta}: p_arrival_time None, pakai s_arrival_time sebagai acuan")
            win_start = UTCDateTime(s_time_utc.to_pydatetime()) - 30
            win_end   = UTCDateTime(s_time_utc.to_pydatetime()) + 130
        else:
            print(f"  Warning {sta}: p_arrival_time dan s_arrival_time None, pakai origin time")
            win_start = ORIGIN_UTC - 10
            win_end   = ORIGIN_UTC + 150

        st   = read(mseed_file)
        tr_e = st.select(channel="*E")[0].slice(win_start, win_end)
        tr_n = st.select(channel="*N")[0].slice(win_start, win_end)
        tr_z = st.select(channel="*Z")[0].slice(win_start, win_end)

        if len(tr_z.data) == 0:
            print(f"  Skip {sta}: data kosong di window")
            continue

        sr = tr_z.stats.sampling_rate  # sampling rate (100 Hz)

        trace_name = (f"{tr_e.stats.network}.{tr_e.stats.station}."
                      f"{tr_e.stats.location}.{tr_e.stats.channel}_"
                      f"{tr_e.stats.starttime.strftime('%Y-%m-%dT%H:%M:%S.%f')}Z")

        win_start_dt = win_start.datetime

        # ── Sumbu X dalam SAMPLE ────────────────────────────────────────
        def get_samples(tr):
            n = len(tr.data)
            offset_sec = (tr.stats.starttime.datetime - win_start_dt).total_seconds()
            offset_smp = offset_sec * sr
            return np.arange(n) + offset_smp

        smp_e = get_samples(tr_e)
        smp_n = get_samples(tr_n)
        smp_z = get_samples(tr_z)
        s_min = 0
        s_max = max(smp_z)
        s_range = np.linspace(s_min, s_max, 2000)

        # ── Posisi picks dalam sample ───────────────────────────────────
        def to_sample(t_utc):
            if t_utc is None:
                return None
            return (t_utc.to_pydatetime() - win_start_dt).total_seconds() * sr

        p_smp      = to_sample(p_time_utc)
        s_smp      = to_sample(s_time_utc)
        origin_smp = (ORIGIN_UTC.datetime - win_start_dt).total_seconds() * sr

        # ── Plot ────────────────────────────────────────────────────────
        fig = plt.figure(figsize=(12, 8))
        fig.patch.set_facecolor('white')

        gs   = gridspec.GridSpec(4, 1, hspace=0.08, figure=fig,
                                 top=0.93, bottom=0.08, left=0.10, right=0.88)
        axes = [fig.add_subplot(gs[i]) for i in range(4)]

        fig.text(0.5, 0.97, f"Trace Name: {trace_name}",
                 ha='center', va='top', fontsize=8.5,
                 fontfamily='monospace', color='#333333')

        comp_data = [
            (smp_e, tr_e.data, 'E'),
            (smp_n, tr_n.data, 'N'),
            (smp_z, tr_z.data, 'Z'),
        ]

        for idx, (smp, data, comp) in enumerate(comp_data):
            ax = axes[idx]
            ax.plot(smp, data, 'k-', linewidth=0.5)
            ax.set_ylabel(f'Amplitude\ncounts ({comp})', fontsize=8)
            ax.set_xlim(s_min, s_max)
            ax.tick_params(labelbottom=False, labelsize=7)
            ax.yaxis.get_major_formatter().set_useOffset(False)
            ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 2))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            if p_smp is not None:
                ax.axvline(p_smp, color=C_P, linewidth=2.0, alpha=0.95,
                           label='Picked P' if idx == 0 else "")
            if s_smp is not None:
                ax.axvline(s_smp, color=C_S, linewidth=2.0, alpha=0.95,
                           label='Picked S' if idx == 0 else "")

            if idx == 0:
                ax.legend(loc='upper right', fontsize=8.5,
                          framealpha=0.85, handlelength=1.5)

        # ── Panel probabilitas ──────────────────────────────────────────
        ax4 = axes[3]

        det_curve = np.zeros_like(s_range)
        if p_smp is not None and s_smp is not None:
            mask = (s_range >= p_smp - 100) & (s_range <= s_smp + 500)
            det_curve[mask] = det_prob
        elif p_smp is not None:
            mask = (s_range >= p_smp - 100) & (s_range <= p_smp + 1000)
            det_curve[mask] = det_prob
        elif s_smp is not None:
            mask = (s_range >= s_smp - 600) & (s_range <= s_smp + 500)
            det_curve[mask] = det_prob
        else:
            # Tidak ada pick sama sekali, tampilkan deteksi saja di tengah window
            mid = (s_min + s_max) / 2
            mask = (s_range >= mid - 500) & (s_range <= mid + 500)
            det_curve[mask] = det_prob

        ax4.plot(s_range, det_curve, color=C_DET, linewidth=1.5,
                 linestyle='--', label=f'Earthquake ({det_prob:.2f})')

        if p_smp is not None:
            p_curve = p_prob * np.exp(-0.5 * ((s_range - p_smp) / 80)**2)
            ax4.plot(s_range, p_curve, color=C_P, linewidth=1.5,
                     linestyle='--', label=f'P arrival ({p_prob:.2f})')

        if s_smp is not None:
            s_curve = s_prob * np.exp(-0.5 * ((s_range - s_smp) / 80)**2)
            ax4.plot(s_range, s_curve, color=C_S, linewidth=1.5,
                     linestyle='--', label=f'S arrival ({s_prob:.2f})')

        ax4.set_ylim(0, 1.05)
        ax4.set_xlim(s_min, s_max)
        ax4.set_ylabel('Probabilitas', fontsize=8)
        ax4.set_xlabel('Sample', fontsize=9)
        ax4.tick_params(labelsize=7)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.legend(loc='upper right', fontsize=8.5,
                   framealpha=0.85, handlelength=2.5)

        out = os.path.join(output_dir, f"{sta}_eqt_style.png")
        plt.savefig(out, dpi=150, bbox_inches='tight')
        plt.close()

        # ── Print log (aman untuk None) ─────────────────────────────────
        p_str = f"{p_smp:.0f}" if p_smp is not None else "N/A"
        s_str = f"{s_smp:.0f}" if s_smp is not None else "N/A"
        print(f"  OK: {sta} | P={p_str} smp  S={s_str} smp  origin={origin_smp:.0f} smp")

    except Exception as e:
        print(f"  Error {sta}: {e}")

print("\nSelesai!")