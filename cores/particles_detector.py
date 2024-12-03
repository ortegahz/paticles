import numpy as np

from data.data import DataRT
from utils.macros import *


class ParticlesDetector:
    def __init__(self):
        self.db = DataRT()
        self.pm025_bg = -1
        self.backward_bg = -1
        self.voc_bg = -1
        self.humid_bg = -1
        self.humid_suppression = 0

    def infer_particle(self):
        if self.db.seq_len < ALARM_NAIVE_SEQ_LEN:
            return

        _voc_alarm, _pm025_alarm, _humid_alarm = False, False, False

        seq_humid = np.array(self.db.db['humid'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.humid_bg = np.average(seq_humid) if self.humid_bg < 0 else \
            self.humid_bg * (1 - ALARM_NAIVE_BG_LR) + seq_humid[-1] * ALARM_NAIVE_BG_LR
        humid_calibrate = np.abs(seq_humid - self.humid_bg)
        if np.all(humid_calibrate > ALARM_NAIVE_PARTICLES_HUMIDITY_TH):
            _humid_alarm = True

        self.humid_suppression = HUMIDITY_SUPPRESSION if _humid_alarm > 0 else self.humid_suppression
        self.humid_suppression = self.humid_suppression - 1 if self.humid_suppression > 0 else 0

        seq_voc = np.array(self.db.db['voc'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.voc_bg = np.average(seq_voc) if self.voc_bg < 0 else \
            self.voc_bg * (1 - ALARM_NAIVE_BG_LR) + seq_voc[-1] * ALARM_NAIVE_BG_LR
        voc_calibrate = seq_voc - self.voc_bg
        if np.all(voc_calibrate > ALARM_NAIVE_THRESHOLD_VOC):
            _voc_alarm = True

        seq_pm025 = np.array(self.db.db['pm2.5'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.pm025_bg = np.average(seq_pm025) if self.pm025_bg < 0 else \
            self.pm025_bg * (1 - ALARM_NAIVE_BG_LR) + seq_pm025[-1] * ALARM_NAIVE_BG_LR
        seq_pm025_calibrate = seq_pm025 - self.pm025_bg
        if np.all(seq_pm025_calibrate > ALARM_NAIVE_THRESHOLD_PM025):
            _pm025_alarm = True

        # if _humid_alarm:
        #     self.db.db['alarm'][-1] = ALARM_INDICATE_VAL / 2

        if _voc_alarm and _pm025_alarm and self.humid_suppression == 0:
        # if _pm025_alarm:
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL

    def infer_smoke(self):
        if self.db.seq_len < ALARM_NAIVE_SEQ_LEN:
            return

        _humid_alarm, _smoke_alarm = False, False

        seq_humid = np.array(self.db.db['humid'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.humid_bg = np.average(seq_humid) if self.humid_bg < 0 else \
            self.humid_bg * (1 - ALARM_NAIVE_BG_LR) + seq_humid[-1] * ALARM_NAIVE_BG_LR
        humid_calibrate = seq_humid - self.humid_bg
        if np.all(humid_calibrate > ALARM_NAIVE_THRESHOLD_HUMID):
            _humid_alarm = True
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL / 2

        self.humid_suppression = HUMIDITY_SUPPRESSION if _humid_alarm > 0 else self.humid_suppression
        self.humid_suppression = self.humid_suppression - 1 if self.humid_suppression > 0 else 0

        seq_backward = np.array(self.db.db['backward_red'][-ALARM_NAIVE_SEQ_LEN:]).astype(float)
        self.backward_bg = np.average(seq_backward) if self.backward_bg < 0 else \
            self.backward_bg * (1 - ALARM_NAIVE_BG_LR) + seq_backward[-1] * ALARM_NAIVE_BG_LR
        seq_backward_calibrate = seq_backward - self.backward_bg
        if np.all(seq_backward_calibrate > ALARM_NAIVE_THRESHOLD_SMOKE) and self.humid_suppression == 0:
            _smoke_alarm = True
            self.db.db['alarm'][-1] = ALARM_INDICATE_VAL / 100 * 99
