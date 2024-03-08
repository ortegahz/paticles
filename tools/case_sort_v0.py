import argparse
import logging
import os
import shutil
from glob import glob

from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_in', default='/media/manu/data/docs/particles/涿鹿测试')
    parser.add_argument('--dir_out', default='/media/manu/data/docs/particles/sorted_v0')
    parser.add_argument('--dir_pad', default='')
    parser.add_argument('--key', default='样机')
    parser.add_argument('--suffix', default='log')
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_out, reset=True)
    sub_dirs = glob(os.path.join(args.dir_in, '*'))
    for sub_dir in sub_dirs:
        logging.info(sub_dir)
        path = glob(os.path.join(sub_dir, args.dir_pad, f'*{args.key}*.{args.suffix}'))
        logging.info(path)
        assert len(path) == 1
        file_name = os.path.basename(path[0]).split('.')[0]
        case_name = os.path.basename(sub_dir)
        logging.info(case_name)
        file_name_out = f'{case_name}_{file_name}.{args.suffix}'
        path_out = os.path.join(args.dir_out, file_name_out)
        shutil.copy(path[0], path_out)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
