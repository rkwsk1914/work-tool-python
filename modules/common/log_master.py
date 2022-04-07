import datetime
import os

import logging
from logging import StreamHandler, FileHandler, Formatter
from logging import INFO, DEBUG, NOTSET
from rich.logging import RichHandler

from modules.common.file_controller import FileController

class LogMater(FileController):

    def __init__(self, app_name):
        #ログファイルの生成
        self.log_file = self.createNewLog(app_name)

        # ストリームハンドラの設定
        stream_handler = StreamHandler()
        stream_handler.setLevel(INFO)
        stream_handler.setFormatter(Formatter('%(levelname)s - %(message)s'))

        # リッチストリームハンドラの設定
        rich_handler: RichHandler = RichHandler(rich_tracebacks=True)
        rich_handler.setLevel(INFO)
        rich_handler.setFormatter(Formatter('%(levelname)s - %(message)s'))

        # ファイルハンドラの設定
        file_handler = FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(Formatter('%(asctime)s  [%(name)s]  %(levelname)s - %(message)s'))

        # ルートロガーの設定
        logging.basicConfig(level=NOTSET, handlers=[stream_handler, file_handler])

        # ロガーの使用開始
        #self.logger = logging.getLogger(module_name)
        return

    def createNewLog(self, module_name):
        current_dir = os.getcwd()
        log_dir = self.creanPath(current_dir + '/log')

        check = os.path.isdir(log_dir)
        if check == False:
            os.mkdir(log_dir)

        log_file = self.createLogFileName(module_name)
        return log_file

    def createLogFileName(self, module_name):
        current_dir = os.getcwd()
        dt_now = datetime.datetime.now()
        now_time = dt_now.strftime('%Y-%m-%d_%H-%M')
        path_text = self.creanPath(current_dir + r'/log/log-' + module_name + '_' + now_time + '.txt')
        path_data = os.path.split(path_text)
        log_file = self.creanPath(path_data[0] + '/' + path_data[1])
        return log_file

    def log(self, module_name, text):
        if self.log_file is None:
            return
        self.logger = logging.getLogger(module_name)
        self.logger.info(text)
        return

    def warning(self, module_name, text):
        if self.log_file is None:
            return
        self.logger = logging.getLogger(module_name)
        self.logger.warning(text)
        return

    def error(self, module_name, text):
        if self.log_file is None:
            return
        self.logger = logging.getLogger(module_name)
        self.logger.error(text)
        return