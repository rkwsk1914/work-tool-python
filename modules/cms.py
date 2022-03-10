import subprocess
import re
import os
import pprint
import webbrowser
from pathlib import Path

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.hearing import Hearing

from modules.backlog_api import BacklogApi
from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.config.db import CMSLSIT

class ThrowList(BacklogApi):
    data = {}

    def __init__(self, comment_url):
        super().__init__(comment_url)

        file_list = self.getUpDatedFile()
        self.throw_lists = list(set(file_list['update'] + file_list['new']))
        self.del_list = file_list['delete']
        self.env = self.getUpDatedEnv()
        self.console = LogMater()
        self.fc = FileController()

    def setItemPath(self, item):
        return self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + item)

    def getPagePath(self, item):
        page_dir = os.path.dirname(item)
        page_set_data = re.sub(r'/set/data', '', page_dir)
        page_path = re.sub(r'/(img|js|css|pdf|)/\S*', '', page_set_data)
        return page_path

    def getPageList(self):
        all_page_list = []
        for item in self.throw_lists:
            page_path = self.getPagePath(item)
            all_page_list.append(page_path)

        for item_del in self.del_list:
            page_path_del = self.getPagePath(item_del)
            all_page_list.append(page_path_del)

        page_list = list(set(all_page_list))
        #pprint.pprint(page_list)
        return page_list

    def getPageData(self, page_list):
        for page in page_list:
            self.data[page] = self.createPageData()

            for item in self.throw_lists:
                page_path = self.getPagePath(item)
                if page_path == page:
                    self.classificationItem(page_path, item)

            for item_del in self.del_list:
                page_path_del = self.getPagePath(item_del)
                if page_path_del == page:
                    self.data[page_path_del]['delete'].append(item_del)

    def createPageData(self):
        data = {
            'article': [],
            'loacalcode': [],
            'meta': [],
            'html': [],
            'css': [],
            'js': [],
            'pdf': [],
            'img': [],
            'other': [],
            'delete': []
        }
        return data

    def classificationItem(self, page, item):
        path = self.setItemPath(item)
        split_data = os.path.splitext(path)
        basename = os.path.basename(item)
        #print(basename)
        extends = re.sub(r'\.', '', split_data[1])

        if extends == 'inc':
            if basename == 'wiro_content.inc':
                self.data[page]['article'].append(item)
            elif basename == 'wiro_localcode.inc':
                self.data[page]['loacalcode'].append(item)
            elif basename == 'wiro_meta.inc':
                self.data[page]['meta'].append(item)
            elif basename == 'wiro_ogimage.inc':
                self.data[page]['meta'].append(item)
            else:
                self.data[page]['html'].append(item)
            return
        elif extends == 'png' \
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
            self.data[page]['img'].append(item)
            self.data[page]['img'].sort()
        elif extends == 'css':
            self.data[page]['css'].append(item)
            self.data[page]['css'].sort()
        elif extends == 'js':
            self.data[page]['js'].append(item)
            self.data[page]['js'].sort()
        elif extends == 'pdf':
            self.data[page]['pdf'].append(item)
            self.data[page]['pdf'].sort()
        else:
            self.data[page]['other'].append(item)
            self.data[page]['other'].sort()

    def getResouceDirList(self, file_list):
        dir_list = []
        for item in file_list:
            dir_item = os.path.dirname(item)
            dir_list.append(dir_item)
        result_lsit = list(set(dir_list))
        return result_lsit

    def getResouceItemList(self, dir_item, file_list):
        all_list = []
        for item in file_list:
            dir_name = os.path.dirname(item)
            if dir_name == dir_item:
                all_list.append(item)

        result_lsit = list(set(all_list))
        return result_lsit


class OpenExe:
    winmerge_copy_file: 'config/wiro.inc'

    def __init__(self):
        return

    def folderOpen(self, full_path):
        try:
            p = subprocess.Popen(["explorer",  full_path], shell=True)
        except:
            log_msg = f'''

            Folder open failed. : {full_path}
            '''.strip()
            self.console.log(log_msg)

        #check = p.poll()
        #if check is None:
        #    p.kill()

    def webOpen(self, url):
        try:
            webbrowser.open(url)
            #print('open web')
        except:
            log_msg = f'''

            Web site open failed. : {url}
            '''.strip()
            self.console.log(log_msg)

    def winMergeOpen(self, fulll_path):
        cmd = 'start WinMergeU ' + fulll_path + ' ' + self.winmerge_copy_file
        try:
            subprocess.check_call(cmd, shell=True)
        except:
            log_msg = f'''

            WinMerge failed. : {cmd}
            '''.strip()
            self.console.log(log_msg)
            return False

class CmsThrow(ThrowList):
    page_count = 0
    sandbox = '/sandbox'

    def __init__(self, comment_url, cms_type='WIRO'):
        super().__init__(comment_url)
        self.type = cms_type
        self.hearinger = Hearing()
        self.openExe = OpenExe()

    def showStart(self):
        pre_msg = f'''
        ({self.page_count}/{len(self.data)}) Page List
        ----------------------------------------------------
        '''.strip()
        self.console.log(pre_msg)

        self.showList(self.data)

        last_msg = f'''
                ----------------------------------------------------
        '''.strip()
        self.console.log(last_msg)
        self.console.log('')

    def showData(self, page_dir):
        page_data = self.data[page_dir]
        log_msg = f'''

        ({self.page_count}/{len(self.data)})
        {page_dir}
        ----------------------------------------------------
            article: {len(page_data['article'])}     loacalcode: {len(page_data['loacalcode'])}
            meta {len(page_data['meta'])}    html: {len(page_data['html'])}
        ----------------------------------------------------
            css: {len(page_data['css'])}    js: {len(page_data['js'])}
            img: {len(page_data['img'])}
            pdf: {len(page_data['pdf'])}    other: {len(page_data['other'])}
        ----------------------------------------------------
            delete: {len(page_data['delete'])}
        ----------------------------------------------------

        '''.strip()
        self.console.log(log_msg)

    def showList (self, array_lsit):
        for item in array_lsit:
            msg = f'''
            {item}
            '''.strip()
            self.console.log(item)

    def throwArtcle(self, page_dir):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['article'] + page_data['loacalcode'] + page_data['meta'] + page_data['html']))
        for file_item in file_list:
            self.checkDone(file_item)

    def setCloneResources(self, file_list):
        for item in file_list:
            origin = self.setItemPath(item)

            current_dir = os.getcwd()
            clone = self.fc.creanPath(current_dir + self.sandbox + item)
            clone_dir = os.path.dirname(clone)
            self.fc.copy(origin, clone)

    def throwResources(self, page_dir):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['css'] + page_data['js'] + page_data['img'] + page_data['pdf'] + page_data['other']))

        self.setCloneResources(file_list)
        dir_lsit = self.getResouceDirList(file_list)

        count = 0
        for dir_item in dir_lsit:
            current_dir = os.getcwd()
            sandbox_item = self.fc.creanPath(current_dir + self.sandbox + dir_item)

            if self.type == 'WIRO':
                url = CMSLSIT['WIRO']['resources'] + dir_item
                self.openExe.webOpen(url)
                self.openExe.folderOpen(sandbox_item)
            elif self.type == 'Sitecore':
                item_count = 0
                for dirname, subdirs, filenames in os.walk(sandbox_item):
                    item_count = len(filenames)
                if item_count <= 1:
                    self.openExe.folderOpen(sandbox_item)
                else:
                    self.fc.createZip(sandbox_item)
                    self.fc.deleate(sandbox_item)
                    sandbox_item_path = Path(sandbox_item)
                    sandbox_item_path.parent
                    self.openExe.folderOpen(sandbox_item_path.parent)

            file_items = self.getResouceItemList(dir_item, file_list)
            self.showList(file_items)
            count = count + len(file_items)
            self.checkDone(f'{dir_item} ({count}/{len(file_list)})')

    def throwDelete(self, page_dir):
        page_data = self.data[page_dir]['delete']
        count = 0

        if self.type == 'Sitecore':
            self.openExe.webOpen(CMSLSIT['Sitecore_PROD']['resources'])

        for file_item in page_data:
            if self.type == 'WIRO':
                url = CMSLSIT['WIRO']['resources'] + dir_item
                self.openExe.webOpen(url)

            self.checkDelete(f'{file_item} ({count}/{len(page_data)})')
            count += 1

    def checkDone(self, item):
        #self.console.log(f'\nDid you input {item} ?')
        check = self.hearinger.select(f'(progress: {self.page_count}/{len(self.data)} ) Did you input {item} ?', ('y', 'n'), True)
        #self.console.log(check)

        if check == 'n':
            self.console.log(f'again input {item}')
            self.checkDone(item)
            return

        self.console.log('')

    def checkDelete(self, item):
        #self.console.log(f'\nDid you delete {item} ?')
        check = self.hearinger.select(f'Did you delete {file_item} ?', ('y', 'n'), True)
        #self.console.log(check)

        if check == 'n':
            self.console.log(f'again delete {item}')
            self.checkDelete(item)

    def throwSitecore(self):
        self.page_count = 1
        self.showStart()
        self.openExe.webOpen(CMSLSIT['Sitecore_PROD']['article'])
        check = self.hearinger.select(f'Did you login Sitecore PROD ?', ('y', 'n'), True)

        for page_dir in self.data:
            self.showData(page_dir)
            self.throwArtcle(page_dir)
            url = CMSLSIT['Sitecore_PROD']['resources']
            self.openExe.webOpen(url)
            self.throwResources(page_dir)
            self.throwDelete(page_dir)
            self.page_count += 1

    def throwWIRO(self):
        self.page_count = 1
        self.showStart()
        self.openExe.webOpen(CMSLSIT['WIRO']['article'])
        check = self.hearinger.select(f'Did you login WIRO ?', ('y', 'n'), True)

        for page_dir in self.data:
            self.showData(page_dir)
            url = CMSLSIT['WIRO']['article'] + page_dir + CMSLSIT['WIRO']['search_key']
            self.openExe.webOpen(url)
            self.throwArtcle(page_dir)
            self.throwResources(page_dir)
            self.throwDelete(page_dir)
            self.page_count += 1

    def resetSandBox(self):
        current_dir = os.getcwd()
        sandbox = current_dir + self.sandbox
        check = os.path.exists(sandbox)
        if check == True:
            self.fc.empty(sandbox)
        else:
            os.mkdir(sandbox)

    def start(self):
        self.resetSandBox()
        self.getPageData(self.getPageList())
        #pprint.pprint(self.data)

        if self.type == 'WIRO':
            self.throwWIRO()
        elif self.type == 'Sitecore':
            self.throwSitecore()
        else:
            self.resetSandBox()
            return
        self.resetSandBox()
        return