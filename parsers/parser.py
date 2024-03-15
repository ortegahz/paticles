import glob

from data.data import *


class ParserBase:
    def __init__(self, db_type, suffix, dir_plot_save):
        self.db_type = db_type
        self.suffix = suffix
        self.dir_plot_save = dir_plot_save

    def parse(self):
        raise NotImplementedError


class ParserV2(ParserBase):
    """
    format: dir_in/case_name/file_name.suffix
    """

    def __init__(self, db_type, suffix, dir_plot_save, dir_in):
        super().__init__(db_type, suffix, dir_plot_save)
        self.dir_in = dir_in
        make_dirs(self.dir_plot_save, reset=True)

    def parse(self):
        dirs_case = glob.glob(os.path.join(self.dir_in, '*'))
        for dir_case in dirs_case:
            logging.info(dir_case)
            case_name = os.path.basename(dir_case)
            paths_in = glob.glob(os.path.join(dir_case, '*'))
            for path_in in paths_in:
                logging.info(path_in)
                db_obj = eval(self.db_type)(path_in)
                db_obj.update()
                path_save = os.path.join(self.dir_plot_save, case_name + '_' + os.path.basename(path_in))
                path_save = path_save.replace(self.suffix, 'png')
                db_obj.plot(pause_time_s=0.001, path_save=path_save)
