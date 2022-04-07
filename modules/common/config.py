import os
import pprint
import configparser

from modules.common.file_controller import FileController
from modules.common.check_param import CheckParam

class Config(FileController):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = self.createConfigFile('config')

        self.check_param = CheckParam()
        self.getConfigData()
        return

    def getConfigData(self):
        check_file = os.path.exists(self.config_file)
        if check_file == False:
            self.setConfigData()
        else:
            self.config.read(self.config_file, encoding='utf-8')
        return

    def setConfigData(self):
        self.config['BASE'] = {
            'local-development-environment': ''
        }
        with open(self.config_file, 'w') as file:
            self.config.write(file)
        return

    def createConfigFile(self, name):
        current_dir = os.getcwd()
        log_dir = self.creanPath(current_dir + '/config')

        check = os.path.isdir(log_dir)
        if check == False:
            os.mkdir(log_dir)

        current_dir = os.getcwd()
        path_text = self.creanPath(current_dir + r'/config/' + name + '.ini')
        path_data = os.path.split(path_text)
        config_file = self.creanPath(path_data[0] + '/' + path_data[1])
        return config_file

    def checkEnvironment(self):
        config_data = self.config['BASE']['local-development-environment']
        args = ['', config_data]

        answer = self.check_param.check(
            args,
            'Please enter directory path of your local development environment.  ex)C:/previewBox/m2-dev.local',
            1,
            r'm2-dev.local'
        )

        env = self.reCheckEnvironment(answer)
        self.config['BASE']['local-development-environment'] = env

        with open(self.config_file, 'w') as file:
            self.config.write(file)
        return env

    def reCheckEnvironment(self, answer):
        check = os.path.isdir(answer)
        if check == False:
            print(f'\nThe entered directory path cannot be found. : {answer}')

            args = ['', '']
            newAnswer = self.check_param.check(
                args,
                'Please enter directory path of your local development environment.  ex)C:/previewBox/m2-dev.local',
                1,
                r'm2-dev.local'
            )
            env = self.reCheckEnvironment(newAnswer)
            return env
        else:
            return answer

cf = Config()
DEVELOPMENT_ENVIRONMENT = cf.checkEnvironment()