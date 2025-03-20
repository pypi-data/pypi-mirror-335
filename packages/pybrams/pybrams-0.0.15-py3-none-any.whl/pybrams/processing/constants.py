import numpy as np
from scipy.special import erfcinv

SHORT_TO_FLOAT_FACTOR = 1 << 15
BEACON_MIN_FREQUENCY = 900
BEACON_MAX_FREQUENCY = 1400


MAD_SCALE = -1 / (np.sqrt(2) * erfcinv(3 / 2))
MAD_FACTOR = 3
