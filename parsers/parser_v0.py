import argparse
import logging

from data.data import DataTextV2
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particles/热解粒子实验数据/目前支持的五种材料_v1/电路板.log')
    parser.add_argument('--keys_plot', default=('temper', 'humid', 'forward', 'backward'))
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/parser_save')
    parser.add_argument('--times_pick', default=[('19:48', 'start', 'y'), ('20:16', 'alarm', 'b')])
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save)
    db_obj = DataTextV2(args.path_in)
    db_obj.update()
    # db_obj.plot_v0(pause_time_s=256)
    # db_obj.save()


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
