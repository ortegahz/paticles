import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlrd


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
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        plt.pause(pause_time_s)
        plt.clf()


class DataXLSV0(DataBase):
    def __init__(self, path_in):
        super().__init__()
        self.path_in = path_in
        # self.db = dict()

    def update(self):
        obj_xlrd = xlrd.open_workbook(self.path_in)

        sheet_names = obj_xlrd.sheet_names()
        logging.info(sheet_names)

        obj_sheet_pick = None
        for sheet_name in sheet_names:
            obj_sheet = obj_xlrd.sheet_by_name(sheet_name)
            logging.info(obj_sheet)
            nrows = obj_sheet.nrows
            ncols = obj_sheet.ncols
            logging.info((nrows, ncols))
            if nrows * ncols > 0:
                obj_sheet_pick = obj_sheet

        keys = obj_sheet_pick.row_values(0)
        logging.info(keys)

        # # TODO
        # if obj_sheet_pick.cell(0, 1).ctype == 1:
        #     self.db['time'] = list()
        #     for i in range(1, obj_sheet_pick.nrows):
        #         time_tuple = xlrd.xldate_as_tuple(obj_sheet_pick.col_values(0)[i], datemode=0)
        #         _time_tuple = (1978, 10, 19, *time_tuple[-3:])
        #         time_str = datetime.datetime(*_time_tuple).strftime('%Y/%m/%d %H:%M:%S')
        #         self.db['time'].append(time_str)

        self.db['time'] = obj_sheet_pick.col_values(0)[1:]
        self.db['voc_raw'] = obj_sheet_pick.col_values(1)[1:]
        self.db['voc_rs'] = obj_sheet_pick.col_values(2)[1:]
        self.db['pm010'] = obj_sheet_pick.col_values(7)[1:]
        self.db['pm025'] = obj_sheet_pick.col_values(8)[1:]
        self.db['pm100'] = obj_sheet_pick.col_values(9)[1:]

        for key in self.db.keys():
            self.seq_len = len(self.db[key]) if len(self.db[key]) > self.seq_len else self.seq_len

    def plot(self, pause_time_s=0.01, keys_plot=None, dir_save=None, times_pick=None):
        plt.ion()
        time_idxs = range(self.seq_len)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        time_idxs_slim = range(0, self.seq_len, 1000)
        time_array = np.array(self.db['time'])[time_idxs_slim]
        times_pick_dict = dict()
        for key, desc, color in times_pick:
            times_pick_dict[key] = (self.db['time'].index(key), desc, color)
        for key in keys_plot:
            if key == 'time':
                continue
            f, ax = plt.subplots()
            plt.title(key)
            plt.xticks(time_idxs_slim)
            ax.set_xticklabels(time_array)
            target_array = np.array(self.db[key]).astype(float)
            for _key in times_pick_dict.keys():
                idx, desc, color = times_pick_dict[_key]
                plt.plot([idx, idx], [0, np.max(target_array)], color=color, label=desc)
            plt.plot(np.array(time_idxs), target_array)
            plt.legend()
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
            plt.show()
            plt.pause(pause_time_s)
            if dir_save is not None:
                plt.savefig(os.path.join(dir_save, f'{key}'))
            plt.clf()


class DataCSVV0(DataBase):
    def __init__(self, path_in):
        super().__init__()
        self.path_in = path_in

    def update(self):
        data = pd.read_csv(self.path_in, header=None)
        # data = pd.read_csv(self.path_in)
        self.db['time'] = data.values[:, 1]
        self.db['voc'] = data.values[:, 2]
        self.db['co'] = data.values[:, 4]
        self.db['temper'] = data.values[:, 6]
        self.db['humid'] = data.values[:, 7]
        self.db['pm010'] = data.values[:, 8]
        self.db['pm025'] = data.values[:, 9]
        self.db['pm100'] = data.values[:, 10]
        self.db['forward'] = data.values[:, 16]
        self.db['backward'] = data.values[:, 17]

        for key in self.db.keys():
            self.seq_len = len(self.db[key]) if len(self.db[key]) > self.seq_len else self.seq_len

    def plot(self, pause_time_s=0.01, keys_plot=None):
        plt.ion()
        time_idxes = range(self.seq_len)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        for key in keys_plot:
            if key == 'time':
                continue
            plt.plot(np.array(time_idxes), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        plt.yticks(np.arange(0, 4096, 4096 / 10))
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        plt.pause(pause_time_s)
        plt.clf()


class DataCSVV0S(DataCSVV0):
    def __init__(self, path_in):
        super(DataCSVV0S, self).__init__(path_in)

    def update(self):
        data = pd.read_csv(self.path_in)
        self.db['time'] = data.values[:, 0]
        self.db['voc'] = data.values[:, 5]

        for key in self.db.keys():
            self.seq_len = len(self.db[key]) if len(self.db[key]) > self.seq_len else self.seq_len


class DataCSVV0M(DataCSVV0):
    def __init__(self, path_in):
        super(DataCSVV0M, self).__init__(path_in)

    def update(self):
        data = pd.read_csv(self.path_in, header=None)
        self.db['time'] = data.values[:, 1]
        self.db['voc'] = data.values[:, 2]
        self.db['co'] = data.values[:, 4]
        self.db['temper'] = data.values[:, 6]
        self.db['humid'] = data.values[:, 7]
        self.db['pm010'] = data.values[:, 8]
        self.db['pm025'] = data.values[:, 9]
        self.db['pm100'] = data.values[:, 10]
        self.db['forward'] = data.values[:, 16]
        self.db['backward'] = data.values[:, 17]
        self.db['voc_gp41'] = data.values[:, -1]

        for key in self.db.keys():
            self.seq_len = len(self.db[key]) if len(self.db[key]) > self.seq_len else self.seq_len


class DataRT(DataBase):
    def __init__(self):
        super().__init__()
        self.max_seq_len = 16384
        self.keys = ('voc', 'co', 'temper', 'humid', 'pm010', 'pm025', 'pm100', 'forward', 'backward')
        self.keys_info = ('alarm',)
        for key in self.keys:
            self.db[key] = list()
        for key in self.keys_info:
            self.db[key] = list()
        self.seq_len = 0

    def update(self, **cur_data_dict):
        for key in cur_data_dict.keys():
            if key in self.keys:
                self.db[key].append(cur_data_dict[key])
                self.db[key] = self.db[key][-self.max_seq_len:]
        for key in self.keys_info:
            self.db[key].append(0.0)
            self.db[key] = self.db[key][-self.max_seq_len:]
        self.seq_len = self.seq_len + 1 if self.seq_len < self.max_seq_len else self.max_seq_len

    def plot(self, pause_time_s=0.01, keys_plot=None, dir_save=None):
        plt.ion()
        time_idxs = range(self.seq_len)
        keys_plot = self.keys if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        for key in self.keys_info:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        plt.yticks(np.arange(0, 4096, 4096 / 10))
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        if dir_save is not None:
            plt.savefig(os.path.join(dir_save, 'demo_infer_rst'))
        plt.pause(pause_time_s)
        plt.clf()
