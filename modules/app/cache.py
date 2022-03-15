import pprint
import subprocess
import re
import os
import time

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.backlog_api import BacklogApi

from modules.config.setup import DEVELOPMENT_ENVIRONMENT

class Cache(BacklogApi):
    count = 0

    def __init__(self, comment_url, param):
        super().__init__(comment_url)
        self.cache_list = self.getCacheList()
        self.env = self.getUpDatedEnv()
        self.param = param
        self.console = LogMater()
        self.fc = FileController()
        self.files = []

    def check(self, file):
        is_code = self.fc.checkCodeFile(file)
        if is_code == False:
            return

        #print(file)
        data = self.fc.reading(file)
        for line in data:
            for cache_item in self.cache_list:
                check = re.search(cache_item, line)

                if not check is None:
                    self.files.append(file)
        return

    def fileList(self, path):
        file_list = []
        for item in os.listdir(path):
            check_file = os.path.isfile(self.fc.creanPath(path + '/' + item))

            if check_file == True:
                file_list.append(self.fc.creanPath(path + '/' + item))
        return file_list

    def grep(self):
        dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env)

        for curDir, dirs, files in os.walk(dir):
            grep_items = self.fileList(curDir)

            for grep_item in grep_items:
                self.check(grep_item)
                self.count += 1
        return

    def reWrite(self, file):
        new_data = []

        data = self.fc.reading(file)
        for line in data:
            for cache in self.cache_list:
                new_cache = cache + '?' + self.param
                new_line = re.sub(cache, new_cache, line)
            new_data.append(new_line)
        self.fc.writing(new_data, file)
        return

    def upDateChahe():
        for file in self.files:
            self.reWrite(file)
        return

    def start(self):
        self.console.log('\nstart\n')
        start_time = time.perf_counter()

        self.grep()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        self.console.log(f'processing time: {elapsed_time}')
        self.console.log(f'Number of files: {self.count}')

        pprint.pprint(self.files)
        #self.upDateChahe()

        self.console.log('\nend\n')
