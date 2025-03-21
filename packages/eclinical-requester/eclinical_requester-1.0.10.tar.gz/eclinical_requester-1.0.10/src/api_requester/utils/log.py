# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/18/2024 4:59 PM
@Description: Description
@File: log.py
"""
import logging
import os
import re
import time

from api_requester.utils.path import root
from api_requester.utils.time_utils import now_yyyy_mm_dd


class Logger:
    """
   define log
    """

    def __init__(self, path=None, c_level=logging.INFO, f_level=logging.DEBUG):
        if path is None:
            path = os.path.join(root(), "logs", f"{now_yyyy_mm_dd(time.time())}.log")
        self.path = path
        self.sh = None
        self.fh = None
        # create log file in case of no file
        if not os.path.exists(path):
            path_dir = os.path.dirname(path)
            if not os.path.exists(path_dir):
                os.makedirs(path_dir)
            file = open(path, "w", encoding="utf-8")
            file.close()
        # create logger
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        # in case of creating multi-logger object
        if not self.logger.handlers:
            # set log format
            fmt = logging.Formatter("[%(asctime)s.%(msecs)03d] [thread:%(thread)d] [threadName:%(threadName)s] "
                                    "[%(levelname)s %(message)s]", datefmt=r"%Y-%m-%d %H:%M:%S")
            # %(filename)s [line:%(lineno)d]
            # set CMD log
            self.sh = logging.StreamHandler()
            self.sh.setFormatter(fmt)
            self.sh.setLevel(c_level)
            # set log in file
            self.fh = logging.FileHandler(path, encoding="utf-8")
            self.fh.setFormatter(fmt)
            self.fh.setLevel(f_level)
            self.logger.addHandler(self.sh)
            self.logger.addHandler(self.fh)

    def __del__(self):
        try:
            if self.sh is not None:
                self.logger.removeHandler(self.sh)
            if self.fh is not None:
                self.logger.removeHandler(self.fh)
        finally:
            pass

    def debug(self, message):
        self.logger.debug(self._msg(message))

    def info(self, message):
        self.logger.info(self._msg(message))

    def warn(self, message):
        self.logger.warning(self._msg(message))

    def error(self, message):
        self.logger.error(self._msg(message))

    def cri(self, message):
        self.logger.critical(self._msg(message))

    @staticmethod
    def _msg(message):
        try:
            if "SQL>>>" in message:
                b = re.compile(r"\s{2,}")
                message = b.sub(" ", message)
                return message
            elif re.search(r"\n\n", message):
                message = re.sub(r"\n\n", r"\n", message)
                return message
        finally:
            return message
