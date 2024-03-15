import argparse
import glob
import logging
import os

from data.data import DataTextV3
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_in', default='/media/manu/data/docs/particles/热解粒子实验数据/涿鹿交付')
    parser.add_argument('--suffix', default='txt')
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/parser_save_v2')
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save, reset=True)
    dirs_case = glob.glob(os.path.join(args.dir_in, '*'))
    for dir_case in dirs_case:
        logging.info(dir_case)
        case_name = os.path.basename(dir_case)
        paths_in = glob.glob(os.path.join(dir_case, '*'))
        for path_in in paths_in:
            logging.info(path_in)
            db_obj = DataTextV3(path_in)
            db_obj.update()
            path_save = os.path.join(args.dir_plot_save, case_name + '_' + os.path.basename(path_in))
            path_save = path_save.replace(args.suffix, 'png')
            db_obj.plot(pause_time_s=0.001, path_save=path_save)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
