from EQTransformer.utils.hdf5_maker import preprocessor

preprocessor(
    preproc_dir=r"D:\BMKG\EQTransformer\hdf5_crop",
    mseed_dir=r"D:\BMKG\EQTransformer\preprocessed_crop_eqt",
    stations_json=r"D:\BMKG\EQTransformer\station_list.json",
    overlap=0.5,
    n_processor=1
)