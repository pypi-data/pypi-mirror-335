# robyn/debug/modeling_rewrite/constants.py
from enum import Enum

class AdstockOptions(Enum):
    GEOMETRIC = "geometric"
    WEIBULL_CDF = "weibull_cdf" 
    WEIBULL_PDF = "weibull_pdf"

HYPS_NAMES = ["thetas", "shapes", "scales", "alphas", "gammas", "penalty"]
HYPS_OTHERS = ["lambda", "train_size"]