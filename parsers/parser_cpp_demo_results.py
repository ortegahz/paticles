import argparse
import logging

import numpy as np

import matplotlib.pyplot as plt
from data.data import DataTextV0A
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/home/manu/tmp/alarm.txt')
    return parser.parse_args()


def run(args):
    logging.info(args)
    with open(args.path_in, 'r') as f:
        lines = f.readlines()
    forward_lst, alarm_lst = [], []
    for line in lines:
        logging.info(line.strip())
        forward, alarm = line.strip().split(',')
        forward_lst.append(forward)
        alarm_lst.append(alarm)

    plt.ion()
    time_idxs = range(len(forward_lst))
    plt.plot(np.array(time_idxs), np.array(forward_lst).astype(float), label='forward')
    plt.plot(np.array(time_idxs), np.array(alarm_lst).astype(float) * 256, label='alarm')
    plt.legend()
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()
    plt.pause(256)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
