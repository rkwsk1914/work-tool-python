import os
import pprint

from modules.config.db import ENVLIST
from modules.config import setup

class EnvList:
    current_directory = ""

    def __init__(self):
        self.current_directory = setup.DEVELOPMENT_ENVIRONMENT
        self.envlist = ENVLIST

    def getEnvironment(self):
        dir_list = os.listdir(self.current_directory)
        pprint.pprint(dir_list)
        return dir_list

    def checkExistEnvironment(self, check_env):
        check = False
        for env_item in self.envlist:
            if check_env == env_item:
                check = True
        return check