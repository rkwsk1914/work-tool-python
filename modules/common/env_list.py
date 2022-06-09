import os
import pprint
import re

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
        for env_item in self.envlist:
            if check_env == env_item:
                return True

        for env_item in self.envlist:
            isEnv = re.search(env_item, check_env)
            if isEnv is not None:
                return True

        return False

    def getExistEnvironmentFromString(self, check_env):
        for env_item in self.envlist:
            isEnv = re.search(env_item, check_env)
            if isEnv is not None:
                return env_item
        return None