import pprint
import subprocess
import re
import os

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.backlog_api import BacklogApi

from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.config.setup import SOFTBANK_DOMAIN

class MovePage():
    def __init__(self, destination_url, previous_url, destination_env, previous_env):
        self.destination_url = destination_url
        self.previous_url = previous_url
        self.destination_env = destination_env
        self.previous_env = previous_env
        self.fc = FileController()
        self.move_fille_list = []
        return

    def getDir(self, url):
        dir = re.sub(SOFTBANK_DOMAIN, '', url)
        return dir

    def getSetData(self, url):
        dir = re.sub(SOFTBANK_DOMAIN, '', url)
        rep_parent_prefox = re.compile(SOFTBANK_DOMAIN + r'\/(\w|\-)+')
        parent_prefox = re.search(rep_parent_prefox, url).group()

        rep = re.compile(SOFTBANK_DOMAIN + r'\/')
        parent = re.sub(rep, '', parent_prefox)
        setData = parent + '/set/data'
        setDir = re.sub(parent, setData, dir)
        return setDir

    def getChildDir(self, path):
        dir_list = []
        for item in os.listdir(path):
            check_dir = os.path.isdir(self.fc.creanPath(path + '/' + item))
            if check_dir == True:
                dir_list.append(item)

        result = list(set(dir_list))
        result.sort()
        return result

    def fileList(self, path):
        file_list = []
        for item in os.listdir(path):
            check_file = os.path.isfile(self.fc.creanPath(path + '/' + item))

            if check_file == True:
                rep = re.compile(self.creanCodingPath(DEVELOPMENT_ENVIRONMENT) + r'/(\w|\-|\_)+/')
                list_item = re.sub(rep, '/', self.creanCodingPath(path + '/' + item))
                file_list.append(list_item)
        return file_list

    def allFileList(self, path, child_list=[]):
        file_list = self.fileList(path)
        for curDir, dirs, files in os.walk(path, topdown=False):

            check_child = False
            for child in child_list:
                child_path = re.sub(self.creanCodingPath(DEVELOPMENT_ENVIRONMENT), '', self.creanCodingPath(path + child))
                is_child = re.search(child_path, self.creanCodingPath(curDir))
                if not is_child is None:
                    check_child = True
            if check_child == True:
                continue
            else:
                dir_file_list = self.fileList(curDir)
                file_list = list(set(file_list + dir_file_list))

        file_list.sort()
        return file_list

    def creanCodingPath(self, path_text):
        crean_path = re.sub(r'\\', '/', path_text)
        return crean_path

    def moveAndReWrite(self, files, previous, destination, previous_setdata_text, destination_setdata_text):
        for file in files:
            origin_path = self.creanCodingPath(DEVELOPMENT_ENVIRONMENT + '/' + self.previous_env + file)
            clone_path = re.sub(self.creanCodingPath(previous), self.creanCodingPath(destination), origin_path)
            origin = self.fc.creanPath(origin_path)
            clone = self.fc.creanPath(clone_path)
            self.fc.copy(origin, clone)

            check_code = self.fc.checkCodeFile(clone)
            if check_code == True:
                self.reWrite(clone, previous_setdata_text, destination_setdata_text)

    def reWrite(self, file, previous_setdata_text, destination_setdata_text):
        new_data = []

        data = self.fc.reading(file)
        for line in data:
            new_line = re.sub(previous_setdata_text, destination_setdata_text, line)
            new_data.append(new_line)
        self.fc.writing(new_data, file)
        return

    def start(self):
        previous = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.previous_env + self.getDir(self.previous_url))
        previous_setdata = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.previous_env  + self.getSetData(self.previous_url))

        child_list = self.getChildDir(previous)

        article_list = self.allFileList(previous, child_list)
        setdata_list = self.allFileList(previous_setdata, child_list)
        self.move_fille_list = list(set(article_list + setdata_list))
        self.move_fille_list.sort()

        destination = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.destination_env + self.getDir(self.destination_url))
        destination_setdata = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.destination_env  + self.getSetData(self.destination_url))

        previous_setdata_text = self.getSetData(self.previous_url)
        destination_setdata_text = self.getSetData(self.destination_url)

        self.moveAndReWrite(article_list, previous, destination, previous_setdata_text, destination_setdata_text)
        self.moveAndReWrite(setdata_list, previous_setdata, destination_setdata, previous_setdata_text, destination_setdata_text)