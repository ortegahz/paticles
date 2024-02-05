import logging
import os
import shutil


def set_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


def make_dirs(dir_root):
    if os.path.exists(dir_root):
        shutil.rmtree(dir_root)
    os.makedirs(os.path.join(dir_root), exist_ok=True)
