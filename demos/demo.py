import argparse
import logging

from cores.particles_detector import ParticlesDetector
from data.data import DataTextV0, DataCSVV0, DataCSVV0M
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--path_in', default='/media/manu/data/docs/particles/国标测试/环氧树脂/MPY22GN2D0012490P_20240202_131652.txt')
    parser.add_argument('--path_in', default='/media/manu/data/docs/particles/0205测试数据/环氧树脂_国标/样机/环氧树脂.txt')
    # parser.add_argument('--path_in', default='/media/manu/data/docs/particles/反例实验/1/样机.csv')
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/parser_save')
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save)
    db_offline = DataTextV0(args.path_in)
    # db_offline = DataCSVV0(args.path_in)
    db_offline.update()
    particles_detector = ParticlesDetector()
    for i in range(db_offline.seq_len):
        cur_data_dict = dict()
        for key in db_offline.db.keys():
            cur_data_dict[key] = db_offline.db[key][i]
        particles_detector.db.update(**cur_data_dict)
        particles_detector.infer()
    particles_detector.db.plot(pause_time_s=256, dir_save=args.dir_plot_save)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
