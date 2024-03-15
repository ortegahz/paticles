import argparse
import logging

from parsers.parser import ParserV2
from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', default='/media/manu/data/docs/particles/热解粒子实验数据/涿鹿交付')
    parser.add_argument('--db_type', default='DataTextV3')
    parser.add_argument('--suffix', default='txt')
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/demo_parser_save')
    return parser.parse_args()


def run(args):
    logging.info(args)
    parser = ParserV2(db_type=args.db_type, suffix=args.suffix, dir_plot_save=args.dir_plot_save, dir_in=args.addr)
    parser.parse()


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
