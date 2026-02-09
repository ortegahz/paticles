import argparse
from glob import glob

from cores.particles_detector import ParticlesDetector
from data.data import *
from utils.utils import set_logging, make_dirs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_in', default='/home/manu/tmp/2026-02-06-15_03_13/')
    parser.add_argument('--dir_plot_save', default='/home/manu/tmp/demo_save_v1')
    parser.add_argument('--offline_db_type', default='DataTextV7P')
    # parser.add_argument('--keys_plot', default=['humid', 'backward_red'])
    parser.add_argument('--keys_plot', default=['humid', 'voc', 'pm2.5', 'backward_red'])
    # parser.add_argument('--keys_plot', default=None)
    parser.add_argument('--suffix', default='txt')
    return parser.parse_args()


def run(args):
    logging.info(args)
    make_dirs(args.dir_plot_save)
    paths_in = glob(os.path.join(args.dir_in, f'*.{args.suffix}'))
    logging.info(paths_in)
    for path_in in paths_in:
        logging.info(path_in)
        # if "ID_4" not in path_in:
        #     continue
        file_name = os.path.basename(path_in).split('.')[0]
        db_offline = eval(args.offline_db_type)(path_in)
        db_offline.update()
        particles_detector = ParticlesDetector()
        for i in range(db_offline.seq_len):
            cur_data_dict = dict()
            for key in db_offline.db.keys():
                cur_data_dict[key] = db_offline.db[key][i]
            particles_detector.db.update(**cur_data_dict)
            particles_detector.infer_particle()
            # particles_detector.infer_smoke()
        # particles_detector.db.timestamps = db_offline.timestamps
        particles_detector.db.plot(pause_time_s=4096, keys_plot=args.keys_plot,
                                   dir_save=args.dir_plot_save, save_name=file_name, show=True)


def main():
    set_logging()
    args = parse_args()
    run(args)


if __name__ == '__main__':
    main()
