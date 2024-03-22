import glob

from data.data import *


class ParserBase:
    def __init__(self, db_type, suffix, dir_plot_save, keys_plot=None):
        self.db_type = db_type
        self.suffix = suffix
        self.dir_plot_save = dir_plot_save
        self.keys_plot = keys_plot

        make_dirs(self.dir_plot_save, reset=False)

    def parse(self):
        raise NotImplementedError


class ParserV0(ParserBase):
    """
    format: file_name.suffix
    """

    def __init__(self, db_type, suffix, dir_plot_save, addr_in, keys_plot=None):
        super().__init__(db_type, suffix, dir_plot_save, keys_plot)
        self.path_in = addr_in

    def parse(self):
        logging.info(self.path_in)
        db_obj = eval(self.db_type)(self.path_in)
        db_obj.update()
        path_save = os.path.join(self.dir_plot_save, os.path.basename(self.path_in))
        path_save = path_save.replace(self.suffix, 'png')
        db_obj.plot(pause_time_s=0.001, path_save=path_save)


class ParserV1(ParserBase):
    """
    format: dir_in/file_name.suffix
    """

    def __init__(self, db_type, suffix, dir_plot_save, addr_in, keys_plot=None):
        super().__init__(db_type, suffix, dir_plot_save, keys_plot)
        self.dir_in = addr_in

    def parse(self):
        paths_in = glob.glob(os.path.join(self.dir_in, '*'))
        for path_in in paths_in:
            logging.info(path_in)
            db_obj = eval(self.db_type)(path_in)
            db_obj.update()
            path_save = os.path.join(self.dir_plot_save, os.path.basename(path_in))
            path_save = path_save.replace(self.suffix, 'png')
            db_obj.plot(pause_time_s=0.001, path_save=path_save, keys_plot=self.keys_plot)


class ParserV2(ParserBase):
    """
    format: dir_in/case_name/file_name.suffix
    """

    def __init__(self, db_type, suffix, dir_plot_save, addr_in):
        super().__init__(db_type, suffix, dir_plot_save)
        self.dir_in = addr_in

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
