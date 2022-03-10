import datetime
import os

from modules.common.file_controller import FileController

class LogMater(FileController):

    def __init__(self):
        self.log_file = self.createNewLog()

    def createNewLog(self):
        current_dir = os.getcwd()
        log_dir = self.creanPath(current_dir + '/log')

        check = os.path.isdir(log_dir)
        if check == True:
            dt_now = datetime.datetime.now()
            now_time = dt_now.strftime('%Y_%m_%d_%H-%M-%S')
            path_text = self.creanPath(current_dir + r'/log/log-' + now_time + '.txt')
            path_data = os.path.split(path_text)
            log_file = self.creanPath(path_data[0] + '/' + path_data[1])
            #print(log_file)
            return log_file
        return None

    def log(self, text):
        if self.log_file is None:
            return
        print(text)
        self.addWrite(text, self.log_file)

