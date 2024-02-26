import numpy as np

from data.data import DataRT
from utils.macros import ALARM_NAIVE_SEQ_LEN, ALARM_NAIVE_THRESHOLD, ALARM_INDICATE_VAL


class ParticlesDetector:
    def __init__(self):
        self.db = DataRT()

    def infer(self):
        if len(self.db.db['pm025']) < ALARM_NAIVE_SEQ_LEN:
            return
        seq_pm025 = np.array(self.db.db['pm025'][-ALARM_NAIVE_SEQ_LEN]).astype(float)
        if np.average(seq_pm025) > ALARM_NAIVE_THRESHOLD:
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL
