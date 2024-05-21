import logging
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlrd

from utils.macros import ALARM_NAIVE_THRESHOLD_PM025, ALARM_INDICATE_VAL
from utils.utils import make_dirs


class DataBase:
    def __init__(self):
        self.db = dict()
        self.seq_len = 0

    def save(self, path_out='/home/manu/tmp/db.txt', key='forward'):
        data_save = self.db[key]
        with open(path_out, 'w') as f:
            for data in data_save:
                f.write(f'{data}\n')


class DataTextV3(DataBase):
    """
    format:
    222,30,7,0,622,13,213,225,1,9,4,2369,178
    219,30,6,0,623,13,205,217,1,9,4,2370,179
    219,30,6,0,623,13,205,217,1,9,4,2370,179
    215,30,7,0,621,13,198,209,1,10,4,2368,178
    ...
    """

    def __init__(self, path_in):
        super().__init__()
        self.path_in = path_in
        self.keys = \
            ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
             'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        for key in self.keys:
            self.db[key] = list()

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        for line in lines[1:]:
            line_lst = line.strip().split(',')
            for i, key in enumerate(self.keys):
                self.db[key].append(float(line_lst[i]))
            self.seq_len += 1

    def plot(self, pause_time_s=0.01, keys_plot=None, show=False, path_save=None):
        plt.ion()
        time_idxs = range(self.seq_len)
        plt.title(self.path_in)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        plt.ylim(0, 4096)
        if show:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
            plt.show()
            plt.pause(pause_time_s)
        if path_save is not None:
            plt.savefig(path_save)
        plt.clf()


class DataTextV3P(DataTextV3):
    """
    format:
    0x0：2000,82,0,0,633,8,2000,2000,0,37,11,2432,91
    0x0：2000,82,0,0,633,8,2000,2000,0,37,11,2432,91
    0x0：2000,82,0,0,633,8,2000,2000,0,37,11,2432,91
    0x0：2000,82,0,0,635,8,2000,2000,1,37,12,2432,91
    0x0：2000,82,0,0,635,8,2000,2000,1,37,12,2432,91
    0x0：2000,82,0,0,635,8,2000,2000,1,37,12,2432,91
    """

    def __init__(self, path_in):
        super().__init__(path_in)

    def update(self):
        with open(self.path_in, 'r', encoding='ISO-8859-1') as f:
            lines = f.readlines()
        for line in lines:
            _, line = line.strip().split('£º')
            line_lst = line.strip().split(',')
            for i, key in enumerate(self.keys):
                self.db[key].append(float(line_lst[i]))
            self.seq_len += 1


class DataTextV3E(DataTextV3):
    """
    format:
    2024-04-11_14-00-14103,73,12,0,2936,48,136,147,1,9,3,2358,193
    2024-04-11_14-00-15103,73,9,0,2913,48,136,147,1,9,3,2364,194
    2024-04-11_14-00-16103,73,9,0,2913,48,140,152,1,9,3,2364,194
    2024-04-11_14-00-17104,73,10,0,2893,48,139,151,1,9,4,2363,194
    2024-04-11_14-00-18103,73,9,0,2876,48,138,150,1,9,3,2365,195
    2024-04-11_14-00-19103,73,9,0,2850,48,140,152,1,9,3,2366,195
    2024-04-11_14-00-20109,73,8,0,2832,48,147,160,1,9,3,2367,195
    2024-04-11_14-00-21111,73,7,0,2807,48,148,161,1,9,3,2368,195
    """

    def __init__(self, path_in):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        del self.db['pm1.0']

    def update(self):
        with open(self.path_in, 'r', encoding='ISO-8859-1') as f:
            lines = f.readlines()
        for line in lines:
            line_lst = line.strip().split(',')
            line_lst_valid = line_lst[1:]
            for i, key in enumerate(self.db.keys()):
                self.db[key].append(float(line_lst_valid[i]))
            self.seq_len += 1


class DataTextV3G(DataTextV3):
    """
    format:
    2024-04-11 17:40:27,33,78,0,0,728,34,45,47,1,9,3,2414,208
    2024-04-11 17:40:28,33,78,0,0,728,34,45,47,1,9,3,2414,208
    2024-04-11 17:40:29,33,78,0,0,730,35,45,47,1,9,3,2414,208
    2024-04-11 17:40:30,34,78,0,0,731,36,45,47,1,9,4,2414,209
    2024-04-11 17:40:31,33,78,0,0,730,37,46,48,1,8,4,2414,209
    2024-04-11 17:40:33,31,78,0,0,731,37,43,45,1,8,3,2414,209
    2024-04-11 17:40:34,31,78,0,0,731,37,43,45,1,8,3,2414,209
    2024-04-11 17:40:35,31,78,0,0,731,37,45,47,1,9,3,2414,209
    2024-04-11 17:40:36,30,78,0,0,731,37,43,45,1,9,3,2415,209
    """

    def __init__(self, path_in):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        self.timestamps = list()

    def update(self):
        with open(self.path_in, 'r', encoding='ISO-8859-1') as f:
            lines = f.readlines()
        for line in lines:
            if len(line) < 8:
                continue
            line_lst = line.strip().split(',')
            line_lst_valid = line_lst[1:]
            for i, key in enumerate(self.db.keys()):
                self.db[key].append(float(line_lst_valid[i]))
            self.timestamps.append(line_lst[0])
            self.seq_len += 1

    def plot(self, pause_time_s=0.01, keys_plot=None, show=False, path_save=None):
        plt.ion()
        plt.title(self.path_in)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        time_stamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in self.timestamps]
        for key in keys_plot:
            if key == 'timestamps':
                continue
            plt.plot(time_stamps, np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        plt.ylim(0, 4096)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        plt.xticks(rotation=45)
        plt.tight_layout()
        if show:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
            plt.show()
            plt.pause(pause_time_s)
        if path_save is not None:
            plt.savefig(path_save)
        plt.clf()


class DataTextV3GC(DataTextV3):
    """
    format:
    Time,PM1.0,Temperature,CO,H2,VOC,Humidity,PM2.5,PM10,RF,BF,RB
    2024-04-22 16:12:38,30,35,0,0,518,24,45,47,1,8,3
    2024-04-22 16:12:39,33,35,0,0,518,24,47,49,1,8,3
    2024-04-22 16:12:40,33,35,0,0,519,24,46,48,1,8,3
    2024-04-22 16:12:41,33,35,0,0,519,24,46,48,1,8,3
    ...
    """

    def __init__(self, path_in):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        self.timestamps = list()
        del self.db['co_raw']
        del self.db['h2_raw']

    def update(self):
        with open(self.path_in, 'r', encoding='ISO-8859-1') as f:
            lines = f.readlines()
        for line in lines[1:]:
            if len(line) < 8:
                continue
            line_lst = line.strip().split(',')
            line_lst_valid = line_lst[1:]
            for i, key in enumerate(self.db.keys()):
                self.db[key].append(float(line_lst_valid[i]))
            self.timestamps.append(line_lst[0])
            self.seq_len += 1


class DataTextV4(DataTextV3):
    """
    format:
    [2024-03-14 15:28:25.395]# RECV HEX>
    05 03 00 01 00 02 4F 94 05 03 00 04 00 80 00 40 EC 42 05 03 00 05 00 0B ...
    """

    def __init__(self, path_in):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        del self.db['co_raw']
        del self.db['h2_raw']

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        for line in lines:
            head = '03 00 16'
            if head not in line:
                continue
            pos = line.find(head)
            line_pick = line[pos:]
            logging.info(line_pick)
            line_pick_lst = line_pick.split(' ')
            logging.info(line_pick_lst)
            line_pick_lst = line_pick_lst[3:3 + 22]
            logging.info(line_pick_lst)
            assert len(line_pick_lst) == 22
            assert len(self.db.keys()) == 11
            for i, key in enumerate(self.db.keys()):
                hex_str = ''.join(line_pick_lst[i * 2:i * 2 + 2])
                logging.info(hex_str)
                val = int(hex_str, 16)
                logging.info(val)
                self.db[key].append(val)
            self.seq_len += 1


class DataTextV5(DataTextV3):
    """
    format:
    [2024-03-26 18:48:38.046]# RECV HEX>
    03 03 00 01 00 02 29 94 03 03 00 04 00 80 00 40 C6 C2

    [2024-03-26 18:48:38.156]# RECV HEX>
    03 03 00 05 00 0B EE 15 03 03 00 16 00 30 00 50 00 00 00 00 01 15 00 19 00 44 00 48 00 2E 00 0D 00 08 98 EF
    """

    def __init__(self, path_in, addr='03'):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        del self.db['co_raw']
        del self.db['h2_raw']
        self.db['timestamps'] = list()
        self.timestamps = list()
        self.addr = addr

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        data_hex_str = ''
        time_str = ''
        for line in lines:
            if 'RECV HEX' in line:
                time_str, _ = line.strip().split(']')
                _, time_str = time_str.split('[')
                # logging.info(time_str)
            elif len(line) > 1:  # skip \n
                data_hex_str += ' ' + line.strip()
                logging.info(data_hex_str)
            head = f'{self.addr} 03 00 16'
            if head not in data_hex_str:
                continue
            pos = data_hex_str.find(head)
            line_pick = data_hex_str[pos:]
            logging.info(line_pick)
            line_pick_lst = line_pick.split(' ')
            logging.info(line_pick_lst)
            line_pick_lst = line_pick_lst[4:4 + 22]
            logging.info(line_pick_lst)
            # assert len(line_pick_lst) == 22
            if len(line_pick_lst) < 22:
                continue
            assert len(self.db.keys()) == 11 + 1
            for i, key in enumerate(self.db.keys()):
                if key == 'timestamps':
                    continue
                hex_str = ''.join(line_pick_lst[i * 2:i * 2 + 2])
                logging.info(hex_str)
                val = int(hex_str, 16)
                logging.info(val)
                self.db[key].append(val)
            self.db['timestamps'].append(time_str)
            self.timestamps.append(time_str)
            self.seq_len += 1
            data_hex_str = data_hex_str[pos + len(head) + 1:]

    def plot(self, pause_time_s=0.01, keys_plot=('pm2.5', 'humid', 'temper', 'voc'), show=False, path_save=None):
        plt.ion()
        plt.title(self.path_in)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        time_stamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f') for ts in self.db['timestamps']]
        for key in keys_plot:
            if key == 'timestamps':
                continue
            plt.plot(time_stamps, np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        # plt.ylim(0, 256)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        plt.xticks(rotation=45)
        plt.tight_layout()
        if show:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
            plt.show()
            plt.pause(pause_time_s)
        if path_save is not None:
            plt.savefig(path_save)
        plt.clf()


class DataTextV6(DataTextV3):
    """
    format:
    <ch, cl, alarm, <13 sigs>>
    0,39,4096,2000,80,0,10,2847,12,2000,2000,1,152,63,2432,91
    0,40,4096,2000,80,0,10,2776,12,2000,2000,0,151,63,2431,91
    0,41,4096,2000,80,0,10,2709,12,2000,2000,0,172,71,2431,91
    0,42,4096,2000,80,0,10,2634,12,2000,2000,0,165,68,2432,91
    0,43,4096,2000,80,0,10,2557,12,2000,2000,0,153,63,2432,91
    0,44,4096,2000,80,0,10,2473,12,2000,2000,0,161,66,2431,90
    ...
    """

    def __init__(self, path_in):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        self.item_pick = 0  # 0 ~ 2
        self.item_len = 40

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        for i in range(self.item_len):
            idx = self.item_pick * self.item_len + i
            line_lst = lines[idx].strip().split(',')[3:]
            for j, key in enumerate(self.keys):
                self.db[key].append(float(line_lst[j]))
            self.seq_len += 1


class DataDatV0(DataTextV3):
    """
    format:
    [2024-03-14 15:28:25.395]# RECV HEX>
    05 03 00 01 00 02 4F 94 05 03 00 04 00 80 00 40 EC 42 05 03 00 05 00 0B ...
    """

    def __init__(self, path_in):
        super().__init__(path_in)
        # ('pm1.0', 'temper', 'co', 'h2', 'voc', 'humid', 'pm2.5', 'pm10',
        #  'forward_red', 'forward_blue', 'backward_red', 'co_raw', 'h2_raw')
        del self.db['co_raw']
        del self.db['h2_raw']
        self.addr = '04'

    def update(self):
        hex_lst = list()
        with open(self.path_in, 'rb') as f:
            while True:
                byte = f.read(1)
                if not byte:
                    break
                hex_byte = format(ord(byte), '02x')
                hex_lst.append(hex_byte)
        logging.info(hex_lst)
        head = f'{self.addr} 03 00 16'
        for i in range(0, len(hex_lst) - 4):
            head_hat = hex_lst[i] + ' ' + hex_lst[i + 1] + ' ' + hex_lst[i + 2] + ' ' + hex_lst[i + 3]
            if not head_hat == head:
                continue
            data_valid = hex_lst[i + 1:i + 4 + 22]
            if len(data_valid) != 3 + 22:
                continue
            logging.info(data_valid)
            data_valid_pick = data_valid[3:]
            assert len(data_valid_pick) == 22
            assert len(self.db.keys()) == 11
            for i, key in enumerate(self.db.keys()):
                hex_str = ''.join(data_valid_pick[i * 2:i * 2 + 2])
                logging.info(hex_str)
                val = int(hex_str, 16)
                logging.info(val)
                self.db[key].append(val)
            self.seq_len += 1


class DataTextV2(DataBase):
    """
    format:
    [2024-04-16 19:29:05.194]# RECV ASCII>

    temperature: 29.83 humidity:16.28

     temperature, temperature_l, temperature_u --> 29.827955, 20.000000, 30.000000

    ---> H2 raw: 154.73,  ppm = 3.45,  calib = -54.00

     --->T :29.83, CO raw: 2396.63, CO CF: 1.08,  ppm = -7.12   ppm CF: -7.66

    sraw H2: 341.28   H2: 104.33 ppm

    sraw CO: 2396.63   CO: 0.00 ppm

    sraw VOC: 501.75

    cFW2511FetchData : 254   0   9   3   1 250   8   2  64  64 202   1   8   0   0   0   1 237   0   0   0   0   0   0   0   0   0   0   0   0   0   0

    smoke forward: 1,9,3

    cS2000FetchData : 0xa5 0xf2 0x04 0x01 0x00 0x01 0x00 0x01 0x00 0x00 0xf9

    pm1.0 = 1 ug/m3 pm2.5 = 1 ug/m3 pm10 = 1 ug/m3

    1, 1, 1, 1, 0, 0, 341, 2396, 104, 0, 29, 16, 0, 0

     [PARSER] 1, 1, 1, 3, 501, 104, 0, 29, 16 # pm010, pm025, pm100, backward, voc, h2, co, temper, humid
    """

    def __init__(self, path_in):
        super().__init__()
        keys = ('pm010', 'pm025', 'pm100', 'backward', 'voc', 'h2', 'co', 'temper', 'humid')
        for key in keys:
            self.db[key] = list()
        self.path_in = path_in
        self.timestamp_cur = ''
        self.h2_raw_cur = -1
        self.thetas_cur = None
        self.timestamps = list()
        self.h2_raw = list()
        self.thetas_lst = list()

    def update(self):
        with open(self.path_in, 'r', encoding='ISO-8859-1') as f:
            lines = f.readlines()
        line_cache = ''
        for i, line in enumerate(lines):
            logging.info(f'line current --> {line}')
            if '# RECV ASCII' in line:
                line_cache = lines[i - 2] if i > 1 and lines[i - 2] is not '\n' else ''
                time_str, _ = line.strip().split(']')
                self.timestamp_cur = time_str[1:]
                continue
            logging.info(f'line_cache --> {line_cache}')
            line = line_cache.strip() + line
            # logging.info(line)
            if '[PARSER]' not in line and '# RECV ASCII' not in line and \
                    'sraw H2:' not in line and '---> thetas' not in line:
                continue
            if 'sraw H2:' in line:
                _, h2_str, _ = line.strip().split('H2:')
                h2_val = float(h2_str.strip())
                self.h2_raw_cur = h2_val
                continue
            if '---> thetas' in line:
                thetas = [float(num) for num in line.split(':')[1].split(',')]
                self.thetas_cur = thetas
                continue
            if '#' not in line or not line.startswith(' [PARSER]'):
                continue
            logging.info(f'line --> {line}')
            vals, keys = line[9:].strip().split('#')
            vals_lst = vals.split(',')
            # logging.info((vals, keys))
            # logging.info(self.db.keys())
            assert len(self.db.keys()) == len(vals_lst)
            for key, val in zip(self.db.keys(), vals_lst):
                self.db[key].append(float(val))
            self.thetas_lst.append(self.thetas_cur)
            self.h2_raw.append(self.h2_raw_cur)
            self.timestamps.append(self.timestamp_cur)
            self.seq_len += 1
            line_cache = ''

    def plot(self, pause_time_s=0.01, keys_plot=None, show=False, path_save=None):
        plt.ion()
        plt.title(self.path_in)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        time_format = '%Y-%m-%d %H:%M:%S.%f'
        time_stamps = [datetime.strptime(ts, time_format) for ts in self.timestamps]
        for key in keys_plot:
            if key == 'timestamps':
                continue
            plt.plot(time_stamps, np.array(self.db[key]).astype(float), label=key)
        plt.plot(time_stamps, np.array(self.h2_raw).astype(float), label='h2_raw')
        plt.legend()
        plt.ylim(0, 4096)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(time_format))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        plt.xticks(rotation=45)
        plt.tight_layout()
        if show:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
            plt.show()
            plt.pause(pause_time_s)
        if path_save is not None:
            plt.savefig(path_save)
        plt.clf()

    def modify(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        with open('/home/manu/tmp/modify.txt', 'w') as f:
            for line in lines:
                if '[PARSER]' in line:
                    line = line.replace('co', 'co,')
                    line = line.replace('rvoc', 'voc')
                f.write(line)


class DataTextV2C(DataTextV2):
    """
    format:
     ...
     ---> H2 raw: 310.86,  ppm = 0.00,  calib = 0.81

     ---> thetas: 36.06319991483694400000000000000000, -0.22044613967795328000000000000000, ...

     --->T :32.79, CO raw: 2428.76, CO CF: 1.10,  ppm = -24.90   ppm CF: -27.38
     ...
    """

    def __init__(self, path_in):
        super().__init__(path_in)

    def plot(self, pause_time_s=0.01, keys_plot=None, show=False, path_save=None):
        def curve(x, thetas):
            return thetas[0] + thetas[1] * x + thetas[2] * x ** 2 + thetas[3] * x ** 3 + thetas[4] * x ** 4

        humidity_data = self.db['humid'] if 'humid' in self.db else [None] * len(self.thetas_lst)
        # skip = 256
        # thetas_lst_pick = self.thetas_lst[::skip]
        # humidity_data_pick = humidity_data[::skip]

        thetas_lst = self.thetas_lst
        humidity_data = self.db['humid']
        num_strata = 10
        samples_per_stratum = 1
        min_humidity = min(humidity_data)
        max_humidity = max(humidity_data)
        stratum_range = (max_humidity - min_humidity) / num_strata
        thetas_lst_pick = []
        humidity_data_pick = []
        for i in range(num_strata):
            stratum_min = min_humidity + i * stratum_range
            stratum_max = stratum_min + stratum_range
            stratum_indices = [j for j, h in enumerate(humidity_data) if stratum_min <= h < stratum_max]
            if len(stratum_indices) > samples_per_stratum:
                picked_indices = np.random.choice(stratum_indices, samples_per_stratum, replace=False)
            else:
                picked_indices = stratum_indices
            thetas_lst_pick.extend([thetas_lst[j] for j in picked_indices])
            humidity_data_pick.extend([humidity_data[j] for j in picked_indices])

        colormap = plt.cm.get_cmap('hsv', len(thetas_lst_pick))
        for idx, (thetas, humidity) in enumerate(zip(thetas_lst_pick, humidity_data_pick)):
            x = np.linspace(0, 3300, 1000)
            y = curve(x, thetas)
            color = colormap(idx)
            plt.plot(x, y, label=f'Humidity: {humidity:.2f}%', color=color, alpha=0.7)
            max_y = np.max(y)
            max_x = x[np.argmax(y)]
            plt.annotate(f'Humidity: {humidity:.2f}%', xy=(max_x, max_y), xytext=(max_x + 100, max_y),
                         arrowprops=dict(facecolor=color, shrink=0.05), fontsize=9)
        plt.xlabel('h2_raw')
        plt.ylabel('ppm')
        # plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        if show:
            plt.show()
        if path_save is not None:
            plt.savefig(path_save, bbox_inches='tight')
        plt.close()


class DataTextV1(DataBase):
    """
    for normalized data
    format:
    voc,co,temper,humid,pm010,pm025,pm100,forward,backward,
     456,1012,27.95,20.86,  31,  49,  60,27,21,
     457, 998,27.94,20.90,  31,  49,  60,26,21,
     454,1008,27.95,20.88,  31,  49,  60,26,21,
     447,1004,27.96,20.88,  31,  49,  60,26,21,
     450,1007,27.95,20.97,  31,  49,  60,27,21,
    """

    def __init__(self, path_in):
        super().__init__()
        self.path_in = path_in

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        keys = lines[0].strip().split(',')[:-1]
        for key in keys:
            self.db[key] = list()
        for line in lines[1:]:
            line_lst = line.strip().split(',')[:-1]
            for i, key in enumerate(keys):
                self.db[key].append(float(line_lst[i]))
            self.seq_len += 1


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

    def plot_v0(self, pause_time_s=0.01, keys_plot=None, show=False, path_save=None):
        plt.ion()
        time_idxs = range(self.seq_len)
        plt.title(self.path_in)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        if show:
            mng = plt.get_current_fig_manager()
            mng.resize(*mng.window.maxsize())
            plt.show()
            plt.pause(pause_time_s)
        if path_save is not None:
            plt.savefig(path_save)
        plt.clf()

    def plot_v1(self, keys_plot=None, dir_save='/home/manu/tmp/v1_save'):
        if dir_save is not None:
            make_dirs(dir_save, reset=True)
        plt.ion()
        time_idxs = range(self.seq_len)
        plt.title(self.path_in)
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        for key in keys_plot:
            plt.plot(np.array(time_idxs), np.array(self.db[key]).astype(float), label=key)
            plt.legend()
            plt.savefig(os.path.join(dir_save, f'{key}'))
            plt.clf()


class DataTextV0A(DataTextV0):
    def __init__(self, path_in):
        super(DataTextV0A, self).__init__(path_in)

    def update(self):
        with open(self.path_in, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if len(line) < 128:
                continue
            logging.info(line)
            line_lst = line.strip().split(',')
            if not len(line_lst) == 14:
                continue
            line_lst_pick = line_lst[1:]
            logging.info(line_lst_pick)
            voc, _, co, _, temper, humid, pm010, pm025, pm100, _, _, _, smoke = line_lst_pick
            cur_data_lst = [voc, co, temper, humid, pm010, pm025, pm100, smoke]
            logging.info(cur_data_lst)
            smoke_lst = smoke.split()
            logging.info(smoke_lst)
            forward, backward = smoke_lst[2], smoke_lst[3]
            cur_data_lst = [voc, co, temper, humid, pm010, pm025, pm100, forward, backward]
            logging.info(cur_data_lst)
            for i, key in enumerate(self.keys):
                self.db[key].append(cur_data_lst[i])  # must be same order
            self.seq_len += 1


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
        y_lim = 128
        plt.yticks(np.arange(0, y_lim, y_lim / 10))
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
        self.max_seq_len = 1024 * 1024
        self.keys_info = ('alarm',)
        for key in self.keys_info:
            self.db[key] = list()
        self.timestamps = list()
        self.seq_len = 0

    def update(self, **cur_data_dict):
        if len(self.db.keys()) == len(self.keys_info):
            for key in cur_data_dict.keys():
                self.db[key] = list()
        for key in cur_data_dict.keys():
            self.db[key].append(cur_data_dict[key])
            # self.db[key] = self.db[key][-self.max_seq_len:]
        for key in self.keys_info:
            self.db[key].append(0.0)
            # self.db[key] = self.db[key][-self.max_seq_len:]
        # self.seq_len = self.seq_len + 1 if self.seq_len < self.max_seq_len else self.max_seq_len
        self.seq_len = self.seq_len + 1

    def plot(self, pause_time_s=0.01, keys_plot=None, dir_save=None, save_name=None, show=True):
        plt.ion()
        timestamps_format = '%Y-%m-%d %H:%M:%S.%f'
        # timestamps_format = '%Y-%m-%d %H:%M:%S'
        if len(self.timestamps) > 0:
            time_stamps = [datetime.strptime(ts, timestamps_format) for ts in self.timestamps]
        else:
            time_stamps = np.array(range(self.seq_len))
        keys_plot = self.db.keys() if keys_plot is None else keys_plot
        for key in keys_plot:
            if key == 'timestamps':
                continue
            plt.plot(time_stamps, np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        for key in self.keys_info:  # TODO: double-plot when keys_plot is None
            plt.plot(time_stamps, np.array(self.db[key]).astype(float), label=key)
            plt.legend()
        # plt.yticks(np.arange(0, 4096, 4096 / 10))
        plt.ylim(0, ALARM_INDICATE_VAL)
        if len(self.timestamps) > 0:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(timestamps_format))
            plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.gcf().autofmt_xdate()
            indices = np.where(np.array(self.db['alarm']) == ALARM_INDICATE_VAL)
            if len(indices[0]) > 0:
                plt.gca().annotate(time_stamps[indices[0][0]],
                                   xy=(time_stamps[indices[0][0]], ALARM_NAIVE_THRESHOLD_PM025),
                                   xytext=(-50, 50), textcoords='offset points',
                                   arrowprops=dict(color='red', arrowstyle='->'))
            plt.xticks(rotation=45)
            plt.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        if dir_save is not None and save_name is not None:
            plt.savefig(os.path.join(dir_save, save_name))
        if show:
            plt.show()
            plt.pause(pause_time_s)
        plt.clf()
