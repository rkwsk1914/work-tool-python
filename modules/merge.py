import subprocess
import re
import os

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater

from modules.backlog_api import BacklogApi
from modules.config.setup import DEVELOPMENT_ENVIRONMENT

class Merge(BacklogApi):

    def __init__(self, comment_url, merge_env):
        super().__init__(comment_url)
        self.file_list = self.getUpDatedFile()
        self.origin_env = self.getUpDatedEnv()
        self.merge_env = merge_env
        self.console = LogMater()
        self.fc = FileController()

    def setItemPath(self, env, item):
        return self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + env + item)

    def doCopy(self, item):
        orign_item = self.setItemPath(self.origin_env, item)
        merge_item = self.setItemPath(self.merge_env, item)

        check = self.fc.copy(orign_item, merge_item)
        if check == True:
            log_msg = f'''

            Copy:
            {orign_item}
            {merge_item}
            '''.strip()
            self.console.log(log_msg)

    def checkCodeFile(self, path):
        data = os.path.splitext(path)
        #print(data[1])
        extends = re.sub(r'\.', '', data[1])
        #print(f'extends: {extends}')
        if extends == 'pdf' \
            or extends == 'png' \
            or extends == 'PNG' \
            or extends == 'jpg' \
            or extends == 'jpeg' \
            or extends == 'JPG' \
            or extends == 'JPEG' \
            or extends == 'pjp' \
            or extends == 'pjpeg' \
            or extends == 'jfif' \
            or extends == 'jpe' \
            or extends == 'gif' \
            or extends == 'svg':
            return True
        return False

    def doMerge(self, item):
        orign_item = self.setItemPath(self.origin_env, item)
        merge_item = self.setItemPath(self.merge_env, item)

        check_img = self.checkCodeFile(merge_item)
        if check_img == True:
            print(f'img cpoy : {item}')
            self.doCopy(item)
            return

        check = self.winmerge(orign_item, merge_item)
        check = True
        if check == True:
            log_msg = f'''

            Merge:
            {orign_item}
            {merge_item}
            '''.strip()
            self.console.log(log_msg)
        return


    def winmerge(self, orign_item, merge_item):
        cmd = 'start WinMergeU ' + orign_item + ' ' + merge_item
        try:
            subprocess.check_call(cmd, shell=True)
        except:
            log_msg = f'''

            WinMerge failed: {cmd}
            {orign_item}
            {merge_item}
            '''.strip()
            self.console.log(log_msg)
            return False
        return True

    def doDel(self, item):
        merge_item = self.setItemPath(self.merge_env, item)

        check = True
        if check == True:
            log_msg = f'''

            Delete:
            {merge_item}
            '''.strip()
            self.console.log(log_msg)

    def start(self):
        start_msg = f'''

        Start.

        '''.strip()
        self.console.log(start_msg)

        for item in self.file_list['update']:
            self.doMerge(item)

        for item in self.file_list['new']:
            self.doCopy(item)

        for item in self.file_list['delete']:
            self.doDel(item)

        end_msg = f'''

        Completed.

        '''.strip()
        self.console.log(end_msg)
        return
