import argparse

from parsers.parser import *
from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', default='/home/manu/tmp/沈消所委托实验/湿热.log')
    parser.add_argument('--db_type', default='DataTextV5')
    parser.add_argument('--keys_plot', default=None)
    parser.add_argument('--suffix', default='log')
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/demo_parser_save')
    return parser.parse_args()


def run(args):
    logging.info(args)
    parser = ParserV0(db_type=args.db_type, suffix=args.suffix, keys_plot=args.keys_plot,
                      dir_plot_save=args.dir_plot_save, addr_in=args.addr)
    parser.parse()


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
