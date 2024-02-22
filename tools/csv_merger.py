import argparse
import logging

import pandas as pd

from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in_a', default='/media/manu/data/docs/particles/反例实验/1/样机.csv')
    parser.add_argument('--path_in_b', default='/media/manu/data/docs/particles/反例实验/1/GP41.csv')
    parser.add_argument('--path_out', default='/media/manu/data/docs/particles/反例实验/1/merge.csv')
    return parser.parse_args()


def run(args):
    logging.info(args)
    data_a = pd.read_csv(args.path_in_a, header=None)
    data_b = pd.read_csv(args.path_in_b, header=None)

    dict_time2val_voc = dict()
    for i in range(0, data_b.shape[0]):
        dict_time2val_voc[data_b.iat[i, 0]] = data_b.iat[i, 5]

    data_a.insert(data_a.shape[1], 'voc', 0)
    for i in range(0, data_a.shape[0]):
        time_ref = data_a.iat[i, 1]
        logging.info(f'time_ref: {time_ref}')
        if time_ref in dict_time2val_voc:
            data_a.iat[i, -1] = dict_time2val_voc[time_ref]
        elif i > 0:
            data_a.iat[i, -1] = data_a.iat[i - 1, -1]
        else:
            data_a.iat[i, -1] = 0

    # save data_a to path_out
    data_a.to_csv(args.path_out, header=False, index=False)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
