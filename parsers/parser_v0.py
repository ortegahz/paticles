import argparse
import logging

from data.data import DataCSVV0
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particles/MPY22GN2D0012490P_20240201_194742.xls')
    parser.add_argument('--keys_plot', default=('temper', 'humid', 'forward', 'backward'))
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/parser_save')
    parser.add_argument('--times_pick', default=[('19:48', 'start', 'y'), ('20:10', 'alarm', 'b')])
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save)
    db_obj = DataCSVV0(args.path_in)
    db_obj.update()
    db_obj.plot(pause_time_s=1, dir_save=args.dir_plot_save, times_pick=args.times_pick)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
