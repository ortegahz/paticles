import argparse
import logging
import os
from glob import glob

from data.data import DataTextV0A
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_in', default='/home/manu/tmp/particles_sorted_v1')
    parser.add_argument('--dir_out', default='/home/manu/tmp/particles_sorted_v1_normalized')
    parser.add_argument('--suffix', default='log')
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_out, reset=True)
    paths_in = glob(os.path.join(args.dir_in, f'*.{args.suffix}'))
    for path_in in paths_in:
        db_obj = DataTextV0A(path_in)
        db_obj.update()
        file_name = os.path.basename(path_in)
        path_out = os.path.join(args.dir_out, file_name)
        with open(path_out, 'w') as f:
            for key in db_obj.db.keys():
                f.write(f'{key},')
            f.write('\n')
            for i in range(db_obj.seq_len):
                for key in db_obj.db.keys():
                    f.write(f'{db_obj.db[key][i]},')
                f.write('\n')


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
