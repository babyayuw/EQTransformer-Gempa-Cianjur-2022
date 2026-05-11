import json

# Koordinat dari web BMKG + cross-check dengan stasiun di dataset
stations = {
    "ACJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.8033, 108.6151, 1]},
    "BBJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.5557, 107.815,  1]},
    "BKJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.3633, 108.5322, 1]},
    "CBJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.6981, 106.9349,  1]},  
    "CBJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.93085,107.35624, 1]},
    "CGJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.6134, 105.6929,  1]},  
    "CIJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.31741, 108.19589, 1]},
    "CIJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.4926, 108.1853,  1]},
    "CMJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.7837, 108.4486,  1]},
    "CNJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.3091, 107.1296,  1]}, 
    "CSJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.3301, 106.52107, 1]},  
    "CSJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.7405, 108.0099,  1]},
    "CTJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.0075, 109.1835,  1]},  
    "CWJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.7423, 107.4448,  1]},
    "DBJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.5542, 106.7436,    1]},  
    "JBJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.483735, 106.4698517, 1]},  
    "JPJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.5306, 107.41757, 1]},
    "JTJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.0573, 106.8015,  1]}, 
    "KPJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.3332, 108.9312,  1]},  
    "LEM" : {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.8266, 107.6175,  1]},
    "PBJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.0874, 107.4757,  1]},
    "PCJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.913,  108.7192,  1]},
    "PKJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.7988, 108.445,   1]},
    "PSJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.9853, 106.5604,  1]},  
    "PSLI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-5.93732, 105.51004, 1]},  
    "PTJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.255535, 106.748825, 1]},  
    "SADLY":{"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.5737854, 106.074132,   1]},  
    "SBJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.1117, 106.1318,  1]}, 
    "SCJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.681, 109.1689,   1]},  
    "SKJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-7.0053, 106.5563,  1]},  
    "TNGI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.172, 106.647,   1]},  
    "TOJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.7621, 108.1344,  1]},
    "TSJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.7319, 107.8109,  1]},
    "WLJI": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.8310983, 105.8909467,  1]},  
    "WSJM": {"network": "IA", "channels": ["SHE","SHN","SHZ"], "coords": [-6.9748, 106.7249,  1]},  
}

# Konversi ke format station_list.json yang dibutuhkan EqT
station_list = {}
for code, info in stations.items():
    station_list[code] = {
        "network": info["network"],
        "channels": info["channels"],
        "coords": info["coords"]
    }

output_path = r"D:\BMKG\EQTransformer\station_list.json"
with open(output_path, "w") as f:
    json.dump(station_list, f, indent=2)

print(f"Tersimpan: {output_path}")
print(f"Total stasiun: {len(station_list)}")