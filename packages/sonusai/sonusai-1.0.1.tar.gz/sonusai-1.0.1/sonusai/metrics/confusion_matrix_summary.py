# ruff: noqa: F821
import numpy as np
import pandas as pd

from ..datatypes import GeneralizedIDs
from ..datatypes import Predict
from ..datatypes import Truth
from ..mixture.mixdb import MixtureDatabase


def confusion_matrix_summary(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs,
    truth_f: Truth,
    predict: Predict,
    class_idx: int,
    predict_thr: float | np.ndarray = 0,
    truth_thr: float = 0.5,
    timesteps: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate confusion matrix for specified class, using truth and prediction
    data [features, num_classes].

    predict_thr sets the decision threshold(s) applied to predict data, thus allowing
    predict to be continuous probabilities.

    Default predict_thr=0 will infer 0.5 for multi-label mode (truth_mutex = False), or
    if single-label mode (truth_mutex == True) then ignore and use argmax mode, and
    the confusion matrix is calculated for all classes.

    Returns pandas dataframes of confusion matrix cmdf and normalized confusion matrix cmndf.
    """
    from ..metrics.one_hot import one_hot

    num_classes = truth_f.shape[1]
    # TODO: re-work for modern mixdb API
    ytrue, ypred = get_mixids_data(mixdb=mixdb, mixids=mixids, truth_f=truth_f, predict=predict)  # type: ignore[name-defined]

    # Check predict_thr array or scalar and return final scalar predict_thr value
    if num_classes > 1:
        if not isinstance(predict_thr, np.ndarray):
            if predict_thr == 0:
                # multi-label predict_thr scalar 0 force to 0.5 default
                predict_thr = np.atleast_1d(0.5)
            else:
                predict_thr = np.atleast_1d(predict_thr)
        else:
            if predict_thr.ndim == 1:
                if predict_thr[0] == 0:
                    # multi-label predict_thr array scalar 0 force to 0.5 default
                    predict_thr = np.atleast_1d(0.5)
                else:
                    # multi-label predict_thr array set to scalar = array[0]
                    predict_thr = predict_thr[0]
            else:
                # multi-label predict_thr array scalar set = array[class_idx]
                predict_thr = predict_thr[class_idx]

    if len(mixdb.class_labels) == num_classes:
        class_names = mixdb.class_labels
    else:
        class_names = [f"Class {i}" for i in range(1, num_classes + 1)]

    _, _, cm, cmn, _, _ = one_hot(ytrue[:, class_idx], ypred[:, class_idx], predict_thr, truth_thr, timesteps)
    cname = class_names[class_idx]
    row_n = ["TrueN", "TrueP"]
    col_n = ["N-" + cname, "P-" + cname]
    cmdf = pd.DataFrame(cm, index=row_n, columns=col_n, dtype=np.int32)  # pyright: ignore [reportArgumentType]
    cmndf = pd.DataFrame(cmn, index=row_n, columns=col_n, dtype=np.float32)  # pyright: ignore [reportArgumentType]
    # add thresholds in 3rd row
    pdnote = pd.DataFrame(np.atleast_2d([predict_thr, truth_thr]), index=["p/t thr:"], columns=col_n)  # pyright: ignore [reportArgumentType, reportCallIssue]
    cmdf = pd.concat([cmdf, pdnote])
    cmndf = pd.concat([cmndf, pdnote])

    return cmdf, cmndf
