import subprocess
import re
import os

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.backlog_api import BacklogApi
from modules.common.svn import SvnConroller

from modules.config.setup import DEVELOPMENT_ENVIRONMENT

console = LogMater('Merge')

class Merge(BacklogApi):

    def __init__(self, comment_url, merge_env, fouce_copy):
        super().__init__(comment_url)
        self.app_name = __class__.__name__
        self.file_list = self.getUpDatedFile()
        self.origin_env = self.getUpDatedEnv()
        self.merge_env = merge_env
        self.fouce_copy = self.checkForceCopy(fouce_copy)
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
            console.log(self.app_name, log_msg)

    def doMerge(self, item):
        orign_item = self.setItemPath(self.origin_env, item)
        merge_item = self.setItemPath(self.merge_env, item)

        check = os.path.exists(merge_item)
        if check == False:
            self.doCopy(item)
            return

        check_code = self.fc.checkCodeFile(merge_item)
        if check_code == False:
            self.doCopy(item)
            return

        if self.fouce_copy == True:
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
            console.log(self.app_name, log_msg)
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
            console.log(self.app_name, log_msg)
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
            console.log(self.app_name, log_msg)

    def updataSvn(self):
        orign_dir = self.setItemPath(self.origin_env, '')
        merge_dir = self.setItemPath(self.merge_env, '')
        orign_svn = SvnConroller(orign_dir)
        merge_svn = SvnConroller(merge_dir)
        orign_check = orign_svn.update()
        merge_check = merge_svn.update()

        if orign_check == False or merge_check == False:
            return False
        return True

    def checkForceCopy(self, fouce_copy):
        if fouce_copy == 'y' or fouce_copy == 'yes':
            return True
        else:
            return False


    def start(self):
        if self.origin_env is None:
            return

        checkSvn =  self.updataSvn()
        if checkSvn == False:
            return

        start_msg = f'''

        Start.

        '''.strip()
        console.log(self.app_name, start_msg)

        for item in self.file_list['update']:
            self.doMerge(item)

        for item in self.file_list['new']:
            self.doCopy(item)

        for item in self.file_list['delete']:
            self.doDel(item)

        end_msg = f'''

        Completed.

        '''.strip()
        console.log(self.app_name, end_msg)
        return
