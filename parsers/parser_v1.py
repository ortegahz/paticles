import argparse
import glob
import logging
import os

from data.data import DataTextV0A
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_in', default='/home/manu/tmp/particles_sorted_v1')
    parser.add_argument('--keys_plot', default=('temper', 'humid'))
    parser.add_argument('--suffix', default='log')
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/parser_save_v1')
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save, reset=True)
    paths_in = glob.glob(os.path.join(args.dir_in, '*'))
    for path_in in paths_in:
        db_obj = DataTextV0A(path_in)
        db_obj.update()
        path_save = os.path.join(args.dir_plot_save, os.path.basename(path_in))
        path_save = path_save.replace(args.suffix, 'png')
        db_obj.plot_v0(pause_time_s=0.001, path_save=path_save)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
