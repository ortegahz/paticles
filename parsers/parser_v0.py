import argparse
import logging

from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particle/MPY22GN2D0012490P_20240131_140535.txt')
    return parser.parse_args()


def run(args):
    logging.info(args)
    with open(args.path_in, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line_lst = line.strip().split(',')
        line_lst_pick = line_lst[2:18]
        logging.info(line_lst_pick)
        voc, _, co, _, temper, humid, pm010, pm025, pm100, _, _, _, _, _, forward, backward = line_lst_pick
        logging.info((voc, co, temper, humid, pm010, pm025, pm100, forward, backward))


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
