import argparse
import logging

from data.data import DataTextV0A
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particles/sorted_v0/聚氨酯（6个）_样机.log')
    parser.add_argument('--keys_plot', default=('temper', 'humid', 'forward', 'backward'))
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/parser_save')
    parser.add_argument('--times_pick', default=[('19:48', 'start', 'y'), ('20:16', 'alarm', 'b')])
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save)
    db_obj = DataTextV0A(args.path_in)
    db_obj.update()
    db_obj.plot_v0(pause_time_s=256)
    db_obj.save()


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
