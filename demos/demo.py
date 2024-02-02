import argparse
import logging

from cores.particles_detector import ParticlesDetector
from utils.utils import set_logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_in', default='/media/manu/data/docs/particle/MPY22GN2D0012490P_20240131_140535.txt')
    return parser.parse_args()


def run(args):
    logging.info(args)
    paticles_detector = ParticlesDetector()
    logging.info(paticles_detector)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
