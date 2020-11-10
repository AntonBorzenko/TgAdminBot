import sys
import logging


def update_logger(log_name=__name__):
    log = logging.getLogger(log_name)
    log.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    log.addHandler(stdout_handler)
