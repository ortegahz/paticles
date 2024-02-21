import argparse
import logging

from cores.particles_detector import ParticlesDetector
from data.data import DataTextV0
from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particles/国标测试/PVC_2/MPY22GN2D0012490P_20240202_153925.txt')
    # parser.add_argument('--path_in', default='/media/manu/data/docs/particles/0205测试数据/ABS_普通/样机/ABS.txt')
    return parser.parse_args()


def run(args):
    logging.info(args)
    db_text = DataTextV0(args.path_in)
    db_text.update()
    particles_detector = ParticlesDetector()
    for i in range(db_text.seq_len):
        cur_data_dict = dict()
        for key in db_text.db.keys():
            cur_data_dict[key] = db_text.db[key][i]
        particles_detector.db.update(**cur_data_dict)
        particles_detector.infer()
    particles_detector.db.plot(pause_time_s=256)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
