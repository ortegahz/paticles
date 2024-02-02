import argparse
import logging

from data.data import DataTextV0
from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particle/MPY22GN2D0012490P_20240131_140535.txt')
    parser.add_argument('--keys_plot', default=('temper', 'humid', 'forward', 'backward'))
    return parser.parse_args()


def run(args):
    logging.info(args)
    db_obj = DataTextV0(args.path_in)
    db_obj.update()
    # db_obj.plot(pause_time_s=64, keys_plot=args.keys_plot)
    db_obj.plot(pause_time_s=64)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
