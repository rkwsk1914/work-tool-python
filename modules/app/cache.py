import pprint
import subprocess
import re
import os
import time
import asyncio
import glob
import numpy as np

from modules.common.hearing import Hearing
from modules.common.log_master import LogMater
from modules.common.file_controller import FileController
from modules.common.backlog_api import BacklogApi

#from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.common.config import DEVELOPMENT_ENVIRONMENT

console = LogMater('Cache')

class Message():
    def __init__(self):
        self.app_name = __class__.__name__
        return

    def showList(self, list_title, cache_list):
        print('')
        console.log(self.app_name, f'{list_title}')
        console.log(self.app_name, "=========================================================")

        for item in cache_list:
            console.log(self.app_name, item)

        console.log(self.app_name, "=========================================================")
        console.log(self.app_name, f'                       Number of target: {len(cache_list)}')
        print('')
        return


class CacheSVN():
    def __init__(self, env):
        self.app_name = __class__.__name__
        self.env = env
        self.fc = FileController()

        self.envPath = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '\\' + self.env)
        return

    def setSVNCommand(self):
        cmd = 'svn st ' + self.envPath
        return cmd

    def doCheckSvn(self, cmd):
        file_list = []

        cp = subprocess.run(cmd, capture_output=True)
        stdout = cp.stdout
        data = stdout.decode('utf-8')

        data_list = re.split(r'\n', data)

        file_list = []
        i = 0
        while i < len(data_list):
            check_M = re.search(r'M\s{7}', data_list[i])

            if not check_M is None:
                item_path = re.sub(r'M\s{7}', '', data_list[i])
                check_asset_item = self.fc.checkAssetFile(self.fc.creanPath(item_path))
                if check_asset_item == False:
                    i += 1
                    continue

                data_item = re.sub(r'\\', '/', data_list[i])
                reg_env_path = re.sub(r'\\', '/', self.envPath)
                regExpData = r'M\s{7}' + reg_env_path + r'|\s'
                regExp = re.compile(regExpData)

                relative_path = re.sub(regExpData, '', data_item)
                file_path = re.sub(r'\\', '/', relative_path)
                file_list.append(file_path)

            i += 1
        return file_list

    def start(self):
        cmd = self.setSVNCommand()
        console.log(self.app_name, f'do command "{cmd}"')
        file_list = self.doCheckSvn(cmd)
        return file_list


class FileListMaker():
    def __init__(self, env):
        self.app_name = __class__.__name__
        self.env = env
        self.fc = FileController()
        self.file_list = []
        self.file_list2 = []
        return

    def walkTree(self):
        start = time.time()
        dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env)
        console.log(self.app_name, f'get directory tree. : {dir}')

        for curDir, dirs, files in os.walk(dir):
            check_ignore = re.search(r'node_modules|\.git|\.svn', curDir)
            #check_ignore = re.search(r'node_modules|\.git|\.svn|_lab', curDir)

            if check_ignore is None:
                self.getFileList(curDir)

        end = time.time()
        delta = end - start
        console.log(self.app_name, f'get directory tree.  processing time (seconds) : {format(round(delta,3))}')
        return self.file_list

    def getFileList(self, path):
        for item in os.listdir(path):
            item_path = self.fc.creanPath(path + '/' + item)
            check_file = os.path.isfile(item_path)

            if check_file == True:
                check_text = self.fc.checkTextFile(item_path)

                if check_text == True:
                    self.file_list.append(item_path)
        return

    def getGlob(self):
        dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env) + "\**\*"
        glob_list = glob.glob(dir, recursive=True)

        for glob_item in glob_list:
            check_ignore = re.search(r'node_modules|\.git|\.svn', glob_item)

            if check_ignore is None:
                item_path = self.fc.creanPath(glob_item)
                check_file = os.path.isfile(item_path)

                if check_file == True:
                    check_text = self.fc.checkTextFile(item_path)

                    if check_text == True:
                        self.file_list2.append(item_path)
        return self.file_list2


class Cache():
    count = 0

    def __init__(self, env, param):
        self.app_name = __class__.__name__
        self.env = env
        self.param = param
        self.code_files_list = []
        self.check_files = []

        self.fc = FileController()
        self.ms = Message()
        self.csvn = CacheSVN(env)
        self.flm = FileListMaker(env)

        print('')
        console.log(self.app_name, f'(Init) development environment : {self.env}')
        console.log(self.app_name, f'(Init) Update Cache Parameters : {self.param}')
        return

    def check(self, file):
        is_text = self.fc.checkTextFile(file)
        if is_text == False:
            return

        data = self.fc.reading(file)
        is_exist = False
        for line in data:
            for cache_item in self.cache_list:
                check = re.search(cache_item, line)
                if not check is None:
                    is_exist = True
                    self.check_files.append(file)
                    return True
        return False

    def reWrite(self, file):
        new_data = []

        data = self.fc.reading(file)
        for line in data:
            new_line = line

            for cache in self.cache_list:
                check_cache_line = re.search(cache, line)

                if not check_cache_line is None:
                    new_cache = cache + '?' + self.param

                    regExpData = cache + r'\?(\w|\-|\_)+'
                    RegExp = re.compile(regExpData)
                    check_hasCache = re.search(RegExp, line)

                    if check_hasCache is None:
                        new_line = re.sub(cache, new_cache, line)
                    else:
                        new_line = re.sub(RegExp, new_cache, line)

            new_data.append(new_line)
        self.fc.writing(new_data, file)
        return

    def upDateChahe(self, files):
        for file in files:
            self.reWrite(file)
        return

    def grep(self, code_files):
        console.log(self.app_name, f'grep number of files : {len(code_files)}')
        start = time.time()

        files = []
        for file in code_files:
            check = self.check(file)

            if check == True:
                files.append(file)

        end = time.time()
        delta = end - start
        console.log(self.app_name, f'grep processing time (seconds): {format(round(delta,3))}')
        return files

    def getCodeFileList(self, num):
        self.cache_list = self.csvn.start()

        code_files = self.flm.walkTree()
        self.count = len(code_files)
        result = list(np.array_split(code_files, num))
        return result

    async def start(self):
        console.log(self.app_name, 'start')
        start = time.time()

        self.cache_list = self.csvn.start()

        if len(self.cache_list) < 1:
            print('')
            console.log(self.app_name, 'No cache target.')
            hearinger = Hearing()
            answer = hearinger.select('\n終了しますか？ ', ['y', 'n', 'yes', 'no'], blank_ok=True)
            return

        self.ms.showList('cache target list', self.cache_list)

        code_files = self.flm.walkTree()
        self.count = len(code_files)

        files = self.grep(code_files)

        end = time.time()
        delta = end - start

        self.ms.showList('updata file list', files)
        self.upDateChahe(files)

        console.log(self.app_name, f'processing time: {format(round(delta,3))}')
        console.log(self.app_name, f'Number of files: {self.count}')
        console.log(self.app_name, 'end')

        hearinger = Hearing()
        print('\n必ずコミット前に必ず上記ファイル（↑ updata file list）の差分を確認してください。')
        answer = hearinger.select('Please answer ==> ', ['y', 'n', 'yes', 'no'])
        console.log(self.app_name, f'Confirm recognition of differences before updating SVN. : {answer}')
        return


class CacheBacklog(BacklogApi):
    count = 0

    def __init__(self, comment_url, param):
        super().__init__(comment_url)
        self.app_name = __class__.__name__
        self.cache_list = self.getCacheList()
        self.env = self.getUpDatedEnv()
        self.param = param
        self.fc = FileController()
        self.files = []

        console.log(self.app_name, f'env : {self.env}')
        console.log(self.app_name, f'param : {self.param}')
        return
