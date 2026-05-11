import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

valid = {
    "ACJM": [-6.8033, 108.6151], "BBJI": [-7.5557, 107.815],
    "BKJI": [-7.3633, 108.5322], "CBJI": [-6.6981, 106.9349],
    "CGJI": [-6.6134, 105.6929], "CIJI": [-7.31741, 108.19589],
    "CIJM": [-6.4926, 108.1853], "CMJI": [-7.7837, 108.4486],
    "CNJI": [-7.3091, 107.1296], "CSJI": [-7.3301, 106.52107],
    "CSJM": [-6.7405, 108.0099], "CTJI": [-7.0075, 109.1835],
    "CWJM": [-6.7423, 107.4448], "DBJI": [-6.5542, 106.7436],
    "JBJI": [-6.483735, 106.4698517], "JPJI": [-6.5306, 107.41757],
    "JTJM": [-7.0573, 106.8015], "KPJI": [-7.3332, 108.9312],
    "LEM":  [-6.8266, 107.6175], "PBJI": [-7.0874, 107.4757],
    "PKJM": [-6.7988, 108.445],  "PSLI": [-5.93732, 105.51004],
    "PTJI": [-6.255535, 106.748825], "SCJI": [-7.681, 109.1689],
    "TNGI": [-6.172, 106.647],   "TSJM": [-6.7319, 107.8109],
    "WSJM": [-6.9748, 106.7249],
}
data_2023 = {
    "PCJM": [-6.913,  108.7192], "PSJM": [-6.9853, 106.5604],
    "SADLY":[-6.5737854, 106.074132], "SBJI": [-6.1117, 106.1318],
    "SKJI": [-7.0053, 106.5563], "TOJI": [-6.7621, 108.1344],
    "WLJI": [-6.8310983, 105.8909467],
}
cbjm = {"CBJM": [-6.93085, 107.35624]}
ccjm = {"CCJM": [-7.0166, 107.1401]}

EP_LAT, EP_LON = -6.862, 107.059

# Batas peta utama (Jawa Barat & sekitarnya)
MAP_EXTENT = [104.8, 109.8, -8.3, -5.3]  # [lon_min, lon_max, lat_min, lat_max]

# Offset label manual untuk stasiun yang saling tiban
label_offsets = {
    "ACJM":  ( 0.04,  0.04, 'left'),
    "BBJI":  ( 0.04,  0.04, 'left'),
    "BKJI":  ( 0.04,  0.04, 'left'),
    "CBJI":  ( 0.04,  0.04, 'left'),
    "CGJI":  (-0.04,  0.04, 'right'),
    "CIJI":  ( 0.04, -0.08, 'left'),
    "CIJM":  ( 0.04,  0.04, 'left'),
    "CMJI":  ( 0.04,  0.04, 'left'),
    "CNJI":  ( 0.04, -0.08, 'left'),
    "CSJI":  (-0.04,  0.04, 'right'),
    "CSJM":  ( 0.04,  0.04, 'left'),
    "CTJI":  ( 0.04,  0.04, 'left'),
    "CWJM":  ( 0.04,  0.04, 'left'),
    "DBJI":  (-0.04,  0.04, 'right'),
    "JBJI":  (-0.04,  0.04, 'right'),
    "JPJI":  ( 0.04,  0.04, 'left'),
    "JTJM":  (-0.04,  0.04, 'right'),
    "KPJI":  ( 0.04,  0.04, 'left'),
    "LEM":   ( 0.04,  0.04, 'left'),
    "PBJI":  ( 0.04, -0.08, 'left'),
    "PKJM":  ( 0.04,  0.04, 'left'),
    "PSLI":  ( 0.04,  0.04, 'left'),
    "PTJI":  (-0.04,  0.04, 'right'),
    "SCJI":  ( 0.04,  0.04, 'left'),
    "TNGI":  ( 0.04,  0.04, 'left'),
    "TSJM":  ( 0.04,  0.04, 'left'),
    "WSJM":  (-0.04,  0.04, 'right'),
    "PCJM":  ( 0.04,  0.04, 'left'),
    "PSJM":  (-0.04,  0.04, 'right'),
    "SADLY": (-0.06,  0.04, 'right'),
    "SBJI":  ( 0.04,  0.04, 'left'),
    "SKJI":  (-0.04, -0.08, 'right'),
    "TOJI":  ( 0.04,  0.04, 'left'),
    "WLJI":  (-0.04,  0.04, 'right'),
    "CBJM":  ( 0.04, -0.08, 'left'),
    "CCJM":  ( 0.04,  0.04, 'left'),
}

# ============================================================
# BUAT FIGURE DENGAN INSET DI BAWAH (SEJAJAR LEGENDA)
# ============================================================
fig = plt.figure(figsize=(15, 10))

# --- PETA UTAMA ---
ax_main = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax_main.set_extent(MAP_EXTENT, crs=ccrs.PlateCarree())

ax_main.add_feature(cfeature.LAND.with_scale('10m'),      facecolor='#F0EDE4', zorder=0)
ax_main.add_feature(cfeature.OCEAN.with_scale('10m'),     facecolor='#D6EAF8', zorder=0)
ax_main.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=0.8, edgecolor='#555555', zorder=1)
ax_main.add_feature(cfeature.BORDERS.with_scale('10m'),   linewidth=0.5, edgecolor='#888888',
                     linestyle='--', zorder=1)
ax_main.add_feature(cfeature.RIVERS.with_scale('10m'),    linewidth=0.3, edgecolor='#AED6F1', zorder=1)

gl = ax_main.gridlines(draw_labels=True, linewidth=0.4, color='gray',
                       alpha=0.5, linestyle='--', x_inline=False, y_inline=False)
gl.top_labels   = False
gl.right_labels = False
gl.xlabel_style = {'size': 9}
gl.ylabel_style = {'size': 9}

def plot_sta(sta_dict, color, ax, zorder=4):
    coords = np.array([(lon, lat) for lat, lon in sta_dict.values()])

    for name, (lat, lon) in sta_dict.items():
        ax.scatter(lon, lat, s=140, c=color, marker='^',
                   edgecolors='white', linewidths=0.8,
                   transform=ccrs.PlateCarree(), zorder=zorder)

        dlon, dlat = 0.05, 0.0
        ha = 'left'

        if name == "PSJM":
            dlon, dlat = 0.0, 0.08
            ha = 'center'
        elif name == "SKJI":
            dlon, dlat = 0.0, -0.08
            ha = 'center'
        elif name == "WSJM":
            dlon, dlat = 0.07, 0.02
            ha = 'left'
        elif name == "JTJM":
            dlon, dlat = 0.07, -0.02
            ha = 'left'
        elif name == "CSJM":
            dlon, dlat = 0.0, 0.06
            ha = 'center'

        for lon2, lat2 in coords:
            if (abs(lon - lon2) < 0.15) and (abs(lat - lat2) < 0.15) and (lon != lon2):
                dlon = -0.05
                ha = 'right'
                break

        ax.text(lon + dlon, lat + dlat, name,
                fontsize=7, ha=ha, va='center',
                transform=ccrs.PlateCarree(), zorder=zorder+1,
                color='#111111', fontweight='bold',
                path_effects=[pe.withStroke(linewidth=2, foreground='white')])

plot_sta(valid,     '#27AE60', ax_main)
plot_sta(data_2023, '#95A5A6', ax_main)
plot_sta(cbjm,      '#E67E22', ax_main)
plot_sta(ccjm,      '#8E44AD', ax_main)

ax_main.scatter(EP_LON, EP_LAT, s=250, c='red', marker='*',
                edgecolors='darkred', linewidths=0.8,
                transform=ccrs.PlateCarree(), zorder=6)

ax_main.text(EP_LON, EP_LAT + 0.05, 'Epicenter Cianjur Mw 5.6',
             fontsize=9.5, color='darkred', fontweight='bold',
             ha='center', va='bottom',
             transform=ccrs.PlateCarree(), zorder=6,
             path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])

legend_elements = [
    mpatches.Patch(facecolor='#27AE60', edgecolor='white',
                   label='Stasiun valid — picking berhasil (n=27)'),
    mpatches.Patch(facecolor='#95A5A6', edgecolor='white',
                   label='Stasiun data 2023 — tidak sesuai periode (n=7)'),
    mpatches.Patch(facecolor='#E67E22', edgecolor='white',
                   label='CBJM — timestamp bermasalah (n=1)'),
    mpatches.Patch(facecolor='#8E44AD', edgecolor='white',
                   label='CCJM — data tidak lengkap, 1 channel (n=1)'),
    plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='red',
               markersize=13, markeredgecolor='darkred',
               label='Epicenter Gempa Cianjur Mw 5.6'),
]
ax_main.legend(handles=legend_elements, loc='upper left', fontsize=8,
               framealpha=0.92, edgecolor='gray',
               title='Keterangan', title_fontsize=9)

ax_main.set_title("Peta Persebaran Stasiun Seismik — Gempa Cianjur Mw 5.6\n"
                  "21 November 2022",
                  fontsize=14, fontweight='bold', pad=12)

# --- INSET PETA REGIONAL (BAWAH, SEJAJAR LEGENDA) ---
# Posisi: [left, bottom, width, height] — ditaruh di bawah peta utama
ax_inset = fig.add_axes([0.05, 0.02, 0.30, 0.30], projection=ccrs.PlateCarree())

# Crop ke Asia Tenggara + sekitarnya (Indonesia full terlihat)
ax_inset.set_extent([90, 145, -15, 10], crs=ccrs.PlateCarree())

ax_inset.add_feature(cfeature.LAND.with_scale('50m'), facecolor='#E8E0D5', zorder=0)
ax_inset.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='#C5D9F0', zorder=0)
ax_inset.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5, edgecolor='#444444', zorder=1)
ax_inset.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.4, edgecolor='#666666',
                     linestyle='--', zorder=1)

# --- KOTAK MERAH: area peta utama ---
lon_min, lon_max = MAP_EXTENT[0], MAP_EXTENT[1]
lat_min, lat_max = MAP_EXTENT[2], MAP_EXTENT[3]
rect = mpatches.Rectangle(
    (lon_min, lat_min),
    lon_max - lon_min,
    lat_max - lat_min,
    linewidth=2.5,
    edgecolor='red',
    facecolor='none',
    linestyle='-',
    transform=ccrs.PlateCarree(),
    zorder=10
)
ax_inset.add_patch(rect)

# Outline hitam untuk inset box
ax_inset.spines['geo'].set_edgecolor('black')
ax_inset.spines['geo'].set_linewidth(1.5)

plt.tight_layout()
out = r"D:\BMKG\EQTransformer\plots_gempa_utama\peta_stasiun_cianjur.png"
plt.savefig(out, dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved: {out}")