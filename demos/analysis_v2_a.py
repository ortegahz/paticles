import argparse
import os
import sys
from glob import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cores.particles_detector import ParticlesDetector
from data.data import *
from utils.utils import set_logging, make_dirs
from pathlib import Path

from mplfonts import use_font

use_font("Noto Sans CJK SC")

import numpy as np

import matplotlib

matplotlib.use("TkAgg")


class Analysis:
    def __init__(self, sensors, window_size=10, inte_actual_len=120, sampling_rate=1.0):
        self.window_size = window_size
        self.sensors = sensors
        self.len = len(self.sensors['pm10'])
        assert self.len > window_size

        self.pm10_base_record = []
        self.pm10_smoothed_record = []
        self.deriv_pm10_record = []
        self.smoothed_alpha = 0.85
        self.pm10_base_alpha = 0.999
        self.inte_actual_len = inte_actual_len
        self.zone_dyn_time = 100
        self.sampling_rate = sampling_rate

        self.slope_record = []
        self.slope_signal_record = []
        self.vib_values, self.vib_record = [], []
        self.state_record = []

        self.activate_idx = -1
        self.count_back_to_zero = 0
        self.count_back_to_zero_thresh = 30
        self.count_zone = 0
        self.zone_len = 100  # dynamic
        self.zone_clock = -1
        self.zone_in_thresh_min = 50
        self.zone_in_thresh_max = 1850
        self.zone_activate_thresh = 20
        self.device_pre_alarm_flag = False
        self.p_signal = False

        self.pm10_smoothed_record.append(self.sensors['pm10'][0])
        self.pm10_base_record.append(min(110, self.sensors['pm10'][0]))
        self.deriv_pm10_record.append(0)
        self.slope_record.append(0)
        self.slope_signal_record.append(0)
        self.vib_values.append(0)
        # self.vib_record.append(0)
        self.state_record.append(0)

    def init_zone_len(self, time_stamp):
        self.zone_clock = time_stamp
        self.update_zone_len(time_stamp)
        pass

    def update_zone_len(self, time_stamp):
        temper = self.sensors['temper'][time_stamp]
        fred = self.sensors['forward_red'][time_stamp]
        fR = min(255, max(100, fred))
        tP = min(45, max(36, temper))
        # self.zone_dyn_time = (0.001667 * fR + 0.633333) * (-10 * tP + 510)
        # y = 0.000016196*(x-100)^2 + 0.79875
        self.zone_dyn_time = min(180.0, max(60.0, (0.000016196 * (fR - 100) * (fR - 100) + 0.79875) * (-10 * tP + 510)))
        self.zone_len = int(self.zone_dyn_time * self.sampling_rate)
        # self.zone_len = self.inte_actual_len#120###

    def device_pre_alarm(self, time_stamp=None):
        print('pre-alarm!', time_stamp)

    def viberation_detection(self, activate_flag, eps=0.1):
        y_win = np.array(self.deriv_pm10_record[- self.window_size:])
        ws = len(y_win)
        max_d = max(y_win)
        min_d = min(y_win)
        if not activate_flag:
            self.vib_values.append(0)
        else:
            if (max_d - eps) * (eps + min_d) >= 0 or abs(max_d) < 2 * eps or abs(min_d) < 2 * eps or ws < 5:
                self.vib_values.append(0)
            else:
                self.vib_values.append(min(50, abs(max_d), abs(min_d)))

        if len(self.vib_values) > self.window_size:
            self.vib_record.append(np.sum(self.vib_values[-self.window_size:]))
        else:
            self.vib_record.append(np.sum(self.vib_values))
        return self.vib_record[-1]  ###
        pass

    # def calculate_derivative(self, data_y, timer_x=None):
    #     if timer_x is not None:
    #         d_data_y = [(data_y[i + 1] - data_y[i]) / (timer_x[i + 1] - timer_x[i]) for i in range(len(data_y) - 1)]
    #     else:
    #         d_data_y = [(data_y[i + 1] - data_y[i]) for i in range(len(data_y) - 1)]
    #     d_data_y.append(0)
    #     return np.array(d_data_y)
    # def smooth(self, y, alpha=0.85, max_value=None):
    #     smoothed = [y[0]]
    #     assert len(y) > 1
    #     for i in range(len(y)):
    #         if max_value is None:
    #             smoothed.append(smoothed[-1] * alpha + y[i] * (1 - alpha))
    #         else:
    #             smoothed.append(min(max_value, smoothed[-1] * alpha + y[i] * (1 - alpha)))
    #     return smoothed[1:]
    #     pass
    def state_transition(self, p_alert, slope_signal, zero_flag, time_stamp):
        state = self.state_record[-1]
        if state in [0]:
            if zero_flag:
                self.state_record.append(0)
                self.zone_clock = -1
            else:
                self.init_zone_len(time_stamp)
                print('0->1: ', time_stamp, ", pm10:", self.sensors['pm10'][time_stamp], ', temper:',
                      self.sensors['temper'][time_stamp], ', fred: ', self.sensors['forward_red'][time_stamp],
                      "zone_len:", self.zone_len, "zone time:", self.zone_dyn_time)
                self.state_record.append(1)
        elif state in [2, -2, -1]:
            if state == -1 and (slope_signal or p_alert):
                if slope_signal:
                    self.state_record.append(-2)
                    print(f"shield!(slope {self.slope_record[-1]:.1f}) at ", time_stamp)
                    self.count_back_to_zero = 0
                elif p_alert:
                    self.state_record.append(2)
                    self.device_pre_alarm_flag = True
                    self.device_pre_alarm(time_stamp)
                    self.count_back_to_zero = 0
            else:
                if zero_flag:
                    self.count_back_to_zero += 1
                    if self.count_back_to_zero >= self.count_back_to_zero_thresh:
                        self.state_record.append(0)
                        self.device_pre_alarm_flag = False
                        self.count_back_to_zero = 0
                    else:
                        self.state_record.append(self.state_record[-1])
                else:
                    self.count_back_to_zero = 0
                    self.state_record.append(self.state_record[-1])
        pass

    def run(self):

        for i in range(1, self.len):
            self.pm10_base_record.append(min(110, self.pm10_base_record[-1] *
                                             self.pm10_base_alpha + self.sensors['pm10'][i] * (
                                                     1 - self.pm10_base_alpha)))
            self.zone_in_thresh_min = self.pm10_base_record[-1] + 22  ###
            self.deriv_pm10_record.append((1 - self.smoothed_alpha) * (
                    self.sensors['pm10'][i] - self.pm10_smoothed_record[-1]))
            self.pm10_smoothed_record.append(self.pm10_smoothed_record[-1] *
                                             self.smoothed_alpha + self.sensors['pm10'][i] * (1 - self.smoothed_alpha))
            # pm10_smoothed_win can be replaced here by self.pm10_smoothed in real time analysis
            pm10_smoothed_win = np.array(self.pm10_smoothed_record[-self.window_size:])
            self.slope_record.append(max(0, pm10_smoothed_win[-1] - pm10_smoothed_win[0]))
            slope_signal = True if self.slope_record[-1] > 600 else False
            self.slope_signal_record.append(slope_signal)
            p_signal = True if self.sensors['alarm'][i] > 0 else False
            ws = len(pm10_smoothed_win)
            zero_flag = np.sum(pm10_smoothed_win <= self.zone_in_thresh_min) >= 0.7 * ws

            activate_flag = np.sum(pm10_smoothed_win >= self.zone_in_thresh_min + self.zone_activate_thresh) >= \
                            0.7 * ws and np.sum(pm10_smoothed_win <= self.zone_in_thresh_max) >= 0.7 * ws  ###
            self.viberation_detection(activate_flag)  ###

            self.state_transition(p_signal, slope_signal, zero_flag, i)
            if self.state_record[-1] == 1:
                if activate_flag and self.activate_idx == -1:
                    self.activate_idx = min(self.zone_clock + 100, i)

                # state transition for state_1
                self.p_signal = self.p_signal or p_signal
                self.update_zone_len(i)
                clock_flag = True if self.zone_clock + self.zone_len <= i else False
                # transition priority: to state_-2 > to state_2 > to state_0 > to state_-1 > stay at state_1
                if slope_signal:
                    self.state_record.append(-2)
                    print(f"shield!(slope {self.slope_record[-1]:.1f}) at ", i)
                    self.p_signal = False
                    self.zone_clock = -1
                    self.count_back_to_zero = 0
                    self.activate_idx = -1
                else:
                    if clock_flag:
                        vib_result = np.mean(
                            np.array(self.vib_record)[self.activate_idx:self.zone_clock + self.zone_len])
                        print('Clock: (', self.activate_idx, ")->", i, ", pm10:", self.sensors['pm10'][i], ', temper:',
                              self.sensors['temper'][i], ', fred: ', self.sensors['forward_red'][i],
                              "zone_len:", self.zone_len, "zone time:", self.zone_dyn_time, ', vib_result:', vib_result)
                        shield_signal = vib_result >= 1.5
                        if shield_signal:
                            self.state_record.append(-2)
                            print(f"shield!(vib {vib_result:.1f}) at ", i)
                            self.p_signal = False
                            self.zone_clock = -1
                            self.count_back_to_zero = 0
                            self.activate_idx = -1
                        else:
                            if self.p_signal:
                                self.state_record.append(2)
                                self.p_signal = False
                                self.device_pre_alarm_flag = True
                                self.device_pre_alarm(i)
                                self.zone_clock = -1
                                self.count_back_to_zero = 0
                                self.activate_idx = -1
                                pass
                            else:
                                if zero_flag:
                                    self.count_back_to_zero += 1
                                    if self.count_back_to_zero >= self.count_back_to_zero_thresh:
                                        self.state_record.append(0)
                                        self.p_signal = False
                                        self.zone_clock = -1
                                        self.count_back_to_zero = 0
                                        self.activate_idx = -1
                                    else:
                                        self.state_record.append(-1)
                                        self.p_signal = False
                                        self.zone_clock = -1
                                        self.activate_idx = -1
                                else:
                                    self.state_record.append(-1)
                                    self.p_signal = False
                                    self.zone_clock = -1
                                    self.count_back_to_zero = 0
                                    self.activate_idx = -1
                    else:
                        if zero_flag:
                            self.count_back_to_zero += 1
                            if self.count_back_to_zero >= self.count_back_to_zero_thresh:
                                self.state_record.append(0)
                                self.p_signal = False
                                self.zone_clock = -1
                                self.count_back_to_zero = 0
                                self.activate_idx = -1
                            else:
                                self.state_record.append(1)
                        else:
                            self.state_record.append(1)
                            self.count_back_to_zero = 0
        pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_in', default="")
    parser.add_argument('--dir_plot_save', default="1")
    parser.add_argument('--offline_db_type', default='DataTextV7P')
    parser.add_argument('--keys_plot',
                        default=[
                            'pm2.5', 'pm1.0', 'pm10',
                            'voc', 'forward_red', 'temper',
                        ]
                        )
    parser.add_argument('--suffix', default='txt')
    return parser.parse_args()


from datetime import datetime


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save)
    paths_in = glob(os.path.join(args.dir_in, f'*.{args.suffix}'))
    logging.info(paths_in)
    for path_in in paths_in:
        logging.info(path_in)
        file_name = os.path.basename(path_in).split('.')[0]
        db_offline = eval(args.offline_db_type)(path_in)
        db_offline.update()
        particles_detector = ParticlesDetector()
        for i in range(db_offline.seq_len):
            cur_data_dict = dict()
            for key in db_offline.db.keys():
                cur_data_dict[key] = db_offline.db[key][i]
            particles_detector.db.update(**cur_data_dict)
            particles_detector.infer_particle()
            # particles_detector.infer_smoke()
        # particles_detector.db.timestamps = db_offline.timestamps

        alarms = np.array(particles_detector.db.db['alarm'])  # 0/4000
        pmten = particles_detector.db.db['pm10']
        pmtwo = particles_detector.db.db['pm2.5']
        pmone = particles_detector.db.db['pm1.0']
        temper = particles_detector.db.db['temper']
        timer = particles_detector.db.db['time']
        time_format = '%H:%M:%S'

        dt = datetime.strptime(timer[-1], time_format) - datetime.strptime(timer[0], time_format)
        dt_seconds = max(1.0, dt.seconds / 60)
        avg_sampling = len(timer) / dt_seconds
        inte_length = 90  # 120 # seconds
        inte_actual_len = int(inte_length * avg_sampling / 60 if dt_seconds > 1.0 else inte_length)
        print(f"time: {dt_seconds:.2f} min, avg: {avg_sampling} pts/min")
        fred = np.array(particles_detector.db.db['forward_red'])
        print("diff temper:", np.max(temper) - np.min(temper), np.max(temper), np.min(temper))
        fred2 = np.zeros(fred.shape)
        fred2[fred >= 240] = 1

        plt.figure()
        signal_analysis = Analysis(particles_detector.db.db, inte_actual_len=inte_actual_len,
                                   sampling_rate=avg_sampling / 60)
        signal_analysis.run()
        plt.plot(signal_analysis.pm10_smoothed_record, label='y')
        plt.plot(signal_analysis.pm10_base_record, label='base')
        plt.plot(10 * (np.array(signal_analysis.vib_record)), label='vib_sum')
        plt.plot(-10 * np.array(temper), label='temper')

        plt.plot(-210 * np.array(signal_analysis.slope_signal_record), label='sus_alert')
        plt.plot(100 * (np.array(signal_analysis.state_record)), label='status_list')
        plt.plot(-0.03 * (np.array(alarms)), label='alarms')
        plt.plot(-fred, label='fred')
        # plt.plot(-300*fred2, label='fred_block')
        plt.title(filter_path_to_fifth_subdir(path_in))
        plt.legend()
        plt.show()
        print('')

        # particles_detector.db.plot(pause_time_s=4096, keys_plot=args.keys_plot,
        #                            dir_save=args.dir_plot_save, save_name=file_name, show=True)


def filter_path_to_fifth_subdir(path, layer=5):
    parts = path.split(os.sep)
    if len(parts) < layer:
        raise ValueError("The path does not contain enough subdirectories.")
    filtered_path = os.sep.join(parts[layer - 1:])
    return filtered_path


def main():
    set_logging()
    # INPS = Path(r"G:\Windows\rjlz\dataset20250605\dataset20250605")
    # INPS = Path(r"G:\Windows\rjlz\dataset20250605\SC")
    # INPS = Path(r"G:\Windows\rjlz\dataset20250605\SC_slow")
    # INPS = Path(r"G:\Windows\rjlz\dataset20250605\set")
    INPS = Path(r"G:\Windows\rjlz\dataset20250605\select")
    # INPS = Path(r"G:\Windows\rjlz\dataset20250605\select2")
    for folder in INPS.iterdir():
        # if os.path.basename(folder) != '聚碳酸酯(10)':
        # if os.path.basename(folder) != '环氧树脂(4)':
        # if os.path.basename(folder) != '聚乙烯(5)':
        # if os.path.basename(folder) != 'ABS(3)':
        # if os.path.basename(folder) != 'fr-4(2)':
        # if os.path.basename(folder) != 'PVC(2)':
        # if os.path.basename(folder) != '':
        # # if os.path.basename(folder) != '2025-05-26-11_15_00SC':
        #     continue
        # if os.path.basename(folder) != '2025-05-30-13_05_13':
        #     continue
        args = parse_args()
        args.dir_in = str(folder)
        # args.dir_plot_save = str(folder)
        run(args)


if __name__ == '__main__':
    main()
    print("done")
