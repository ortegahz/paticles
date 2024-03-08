import numpy as np

from data.data import DataRT
from utils.macros import ALARM_NAIVE_SEQ_LEN, ALARM_NAIVE_THRESHOLD_PM025, ALARM_NAIVE_THRESHOLD_VOC, ALARM_INDICATE_VAL


class ParticlesDetector:
    def __init__(self):
        self.db = DataRT()

    def infer(self):
        if self.db.seq_len < ALARM_NAIVE_SEQ_LEN:
            return
        seq_pm025 = np.array(self.db.db['pm025'][-1]).astype(float)
        seq_voc = np.array(self.db.db['voc'][-1]).astype(float)
        if np.average(seq_pm025) > ALARM_NAIVE_THRESHOLD_PM025 and np.average(seq_voc) > ALARM_NAIVE_THRESHOLD_VOC:
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL
