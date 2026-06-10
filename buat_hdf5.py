from EQTransformer.utils.hdf5_maker import preprocessor

preprocessor(
    preproc_dir=r"D:\BMKG\EQTransformer\preprocessed_eqt_processed_hdfs",
    mseed_dir=r"D:\BMKG\EQTransformer\preprocessed_eqt",
    stations_json=r"D:\BMKG\EQTransformer\station_list.json",
    overlap=0.3,
    n_processor=1  #coba dulu 1, buat menghindari masalah multiprocessing di windows
)
