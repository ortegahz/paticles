import logging

import matplotlib.pyplot as plt
import numpy as np


class DataBase:
    def __init__(self):
        self.db = dict()
        self.seq_len = 0


class DataTextV0(DataBase):
    def __init__(self, path_in):
        super().__init__()
        self.path_in = path_in
        self.keys = ('voc', 'co', 'temper', 'humid', 'pm010', 'pm025', 'pm100', 'forward', 'backward')
        for key in self.keys:
            self.db[key] = list()

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line_lst = line.strip().split(',')
            line_lst_pick = line_lst[2:18]
            logging.info(line_lst_pick)
            voc, _, co, _, temper, humid, pm010, pm025, pm100, _, _, _, _, _, forward, backward = line_lst_pick
            cur_data_lst = [voc, co, temper, humid, pm010, pm025, pm100, forward, backward]
            logging.info(cur_data_lst)
            for i, key in enumerate(self.keys):
                self.db[key].append(cur_data_lst[i])  # must be same order
            self.seq_len += 1

    def plot(self, pause_time_s=0.01, keys_plot=None):
        plt.ion()
        time_idxs = range(self.seq_len)
        plt.title(self.path_in)
        keys_plot = self.keys if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        plt.pause(pause_time_s)
        plt.clf()


class DataRT(DataBase):
    def __init__(self):
        super().__init__()
        self.keys = ('voc', 'co', 'temper', 'humid', 'pm010', 'pm025', 'pm100', 'forward', 'backward')
        for key in self.keys:
            self.db[key] = list()
        self.seq_len = 0

    def update(self, **cur_data_dict):
        for key in cur_data_dict.keys():
            if key in self.keys:
                self.db[key].append(cur_data_dict[key])
        self.seq_len += 1

    def plot(self, pause_time_s=0.01, keys_plot=None):
        plt.ion()
        time_idxs = range(self.seq_len)
        keys_plot = self.keys if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        plt.pause(pause_time_s)
        plt.clf()
