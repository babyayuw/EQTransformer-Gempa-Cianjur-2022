import os
import matplotlib
matplotlib.use('Agg')

import matplotlib.figure
_original_savefig = matplotlib.figure.Figure.savefig
def _patched_savefig(self, fname, *args, **kwargs):
    if isinstance(fname, str):
        dirname  = os.path.dirname(fname)
        basename = os.path.basename(fname)
        basename = basename.replace(":", "-")
        fname    = os.path.join(dirname, basename)
    return _original_savefig(self, fname, *args, **kwargs)
matplotlib.figure.Figure.savefig = _patched_savefig

from EQTransformer.core import predictor

predictor(
    input_dir=r"D:\BMKG\EQTransformer\preprocessed_eqt_processed_hdfs",
    input_model=r"D:\BMKG\EQTransformer\EqT_original_model.h5",
    output_dir=r"D:\BMKG\EQTransformer\detections_cianjur",
    detection_threshold=0.3,
    P_threshold=0.1,
    S_threshold=0.1,
    number_of_plots=10,
    plot_mode='time',
    batch_size=100,
    number_of_cpus=1,
    use_multiprocessing=False
)