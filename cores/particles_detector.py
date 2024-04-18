import numpy as np

from data.data import DataRT
from utils.macros import *


class ParticlesDetector:
    def __init__(self):
        self.db = DataRT()
        self.pm025_bg = -1
        self.backward_bg = -1

    def infer(self):
        if self.db.seq_len < ALARM_NAIVE_SEQ_LEN:
            return

        seq_pm025 = np.array(self.db.db['pm2.5'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.pm025_bg = np.average(seq_pm025) if self.pm025_bg < 0 else \
            self.pm025_bg * (1 - ALARM_NAIVE_BG_LR) + seq_pm025[-1] * ALARM_NAIVE_BG_LR
        seq_pm025_calibrate = seq_pm025 - self.pm025_bg
        if np.all(seq_pm025_calibrate > ALARM_NAIVE_THRESHOLD_PM025):
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL

        seq_backward = np.array(self.db.db['backward_red'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.backward_bg = np.average(seq_backward) if self.backward_bg < 0 else \
            self.backward_bg * (1 - ALARM_NAIVE_BG_LR) + seq_backward[-1] * ALARM_NAIVE_BG_LR
        seq_backward_calibrate = seq_backward - self.backward_bg
        if np.all(seq_backward_calibrate > ALARM_NAIVE_THRESHOLD_SMOKE):
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL / 2
