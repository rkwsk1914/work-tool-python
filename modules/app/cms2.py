import subprocess
import re
import os
import pprint
import webbrowser
from pathlib import Path
from bs4 import BeautifulSoup

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.hearing import Hearing
from modules.common.backlog_api import BacklogApi
from modules.common.scraping import Scraping
from modules.common.svn import SvnConroller
from modules.app.resourcs_check import ResourceChecK

from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.config.db2 import CMSLSIT
from modules.config.db2 import ENVLIST

#
# SUB
#
class OpenExe:
    cms_countent = '/cms-part/now-cms-copy.inc'
    localcode_pc = '/cms-part/now-sitecore-localcode-pc.inc'
    localcode_sp = '/cms-part/now-sitecore-localcode-sp.inc'
    conten_pc = '/cms-part/now-sitecore-content-pc.inc'
    conten_sp = '/cms-part/now-sitecore-content-sp.inc'

    cookipit = ''

    def __init__(self, console):
        self.fc = FileController()
        self.sc = Scraping()
        self.console = console

    def folderOpen(self, full_path):
        try:
            #p = subprocess.Popen(["explorer",  full_path], shell=True)
            print('folder open')
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
            #webbrowser.open(url)
            print('open web')
        except:
            log_msg = f'''

            Web site open failed. : {url}
            '''.strip()
            self.console.log(log_msg)

    def winMergeOpen(self, new_content):
        current_dir = os.getcwd()
        now_cms_content = self.fc.creanPath(current_dir + self.cms_countent)
        cmd = 'start WinMergeU ' + new_content + ' ' + now_cms_content
        try:
            #subprocess.check_call(cmd, shell=True)
            print(cmd)
        except:
            log_msg = f'''

            WinMerge failed. : {cmd}
            '''.strip()
            self.console.log(log_msg)
            return False

    def openCockpit(self, page_path, page_data, env):
        url = ENVLIST[env]['domain']['pc'] + CMSLSIT['Sitecore_PROD']['checkTool'] + '/?' + page_path + '/'
        account = ENVLIST[env]['account']
        password = ENVLIST[env]['password']
        url_auth = re.sub(r'https://', f'https://{account}:{password}@', url)
        self.webOpen(url_auth)

        try:
            request = self.sc.createRequest(url, account, password)
            data = self.sc.getUrlResponse(request, url)
        except:
            log_msg = f'''

            request failed. : {url_auth}
            '''.strip()
            self.console.log(log_msg)
        else:
            self.openWinMergeWithCockpit(data, page_data)

    def openWinMergeWithCockpit(self, data, page_data):
        soup = BeautifulSoup(data,'html.parser')
        codeboxList = [tag.text for tag in soup.find_all(class_='codebox')]
        current_dir = os.getcwd()
        localcode_pc = self.fc.creanPath(current_dir + self.localcode_pc)
        localcode_sp = self.fc.creanPath(current_dir + self.localcode_sp)
        conten_pc = self.fc.creanPath(current_dir + self.conten_pc)
        conten_sp = self.fc.creanPath(current_dir + self.conten_sp)
        self.fc.writing(re.sub(r'^\r\n', '',codeboxList[0]), localcode_pc)
        self.fc.writing(re.sub(r'^\r\n', '',codeboxList[1]), localcode_sp)
        self.fc.writing(re.sub(r'^\r\n', '',codeboxList[2]), conten_pc)
        self.fc.writing(re.sub(r'^\r\n', '',codeboxList[3]), conten_sp)

        if not len(page_data['loacalcode']) == 0:
            self.winMergeOpen(localcode_pc)
            self.winMergeOpen(localcode_sp)

        if not len(page_data['article']) == 0:
            self.winMergeOpen(conten_pc)
            self.winMergeOpen(conten_sp)

    def preview(self, page_dir):
        url = CMSLSIT['Sitecore_PROD']['preview'] + page_dir + '/'
        account =  CMSLSIT['Sitecore_PROD']['account']
        password =  CMSLSIT['Sitecore_PROD']['password']
        url_auth = re.sub(r'https://', f'https://{account}:{password}@', url)
        #print(url_auth)
        self.webOpen(url)


class showMessage():
    def __init__(self, data, console):
        self.data = data
        self.console = console
        return

    def showEnd(self, page_count):
        pre_msg = f'''
        ({page_count}/{len(self.data)}) Page List
        ----------------------------------------------------
        '''.strip()
        self.console.log(pre_msg)

        self.showList(self.data)

        last_msg = f'''
                ----------------------------------------------------

                Completed.
        '''.strip()
        self.console.log(last_msg)
        self.console.log('')

        input('Did you close all sandbox folder? : ')
        return

    def showStart(self, page_count):
        pre_msg = f'''
        ({page_count}/{len(self.data)}) Page List
        ----------------------------------------------------
        '''.strip()
        self.console.log(pre_msg)

        self.showList(self.data)

        last_msg = f'''
                ----------------------------------------------------
        '''.strip()
        self.console.log(last_msg)
        self.console.log('')

    def showData(self, page_dir, page_count):
        page_data = self.data[page_dir]
        log_msg = f'''

        ({page_count}/{len(self.data)})
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


class CmsThrow(showMessage):
    page_count = 0
    sandbox = '/cms-part/sandbox'

    def __init__(self, data, env, cms_type, console):
        super().__init__(data, console)
        self.env = env
        self.data = data
        self.cms_type = cms_type
        self.hearinger = Hearing()
        self.fc = FileController()
        self.openExe = OpenExe(self.console)
        return

    def setLang(self, page_dir):
        checkEnLange = re.search(r'/en/', page_dir)

        if checkEnLange is None:
            self.lang = 'en'
        else:
            self.lang = 'ja'
        return

    def resetSandBox(self):
        current_dir = os.getcwd()
        sandbox = current_dir + self.sandbox
        check = os.path.exists(sandbox)
        if check == True:
            self.fc.empty(sandbox)
        else:
            os.mkdir(sandbox)

    def setCloneResources(self, file_list):
        for item in file_list:
            origin = self.setItemPath(item)

            current_dir = os.getcwd()
            clone = self.fc.creanPath(current_dir + self.sandbox + item)
            clone_dir = os.path.dirname(clone)
            self.fc.copy(origin, clone)

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

    def getResouceDirList(self, file_list):
        dir_list = []
        for item in file_list:
            dir_item = os.path.dirname(item)
            dir_list.append(dir_item)
        result_lsit = list(set(dir_list))
        return result_lsit


class CMSWIRO(CmsThrow):
    def __init__(self, data, env, cms_type, console):
        super().__init__(data, env, cms_type, console)
        return

    def throwDelete(self, page_dir):
        page_data = self.data[page_dir]['delete']
        count = 0

        for file_item in page_data:
            url = CMSLSIT['WIRO'][self.cms_type]['resources'] + dir_item
            self.openExe.webOpen(url)

            self.checkDelete(f'{file_item} ({count}/{len(page_data)})')
            count += 1

    def throwArtcle(self, page_dir):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['article'] + page_data['loacalcode'] + page_data['meta'] + page_data['html']))
        for file_item in file_list:
            new_content = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + '/' + file_item)
            self.openExe.winMergeOpen(new_content)
            self.checkDone(file_item)

    def throwResources(self, page_dir, category_type):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['css'] + page_data['js'] + page_data['img'] + page_data['pdf'] + page_data['other']))

        self.setCloneResources(file_list)
        dir_lsit = self.getResouceDirList(file_list)

        count = 0
        for dir_item in dir_lsit:
            current_dir = os.getcwd()
            sandbox_item = self.fc.creanPath(current_dir + self.sandbox + dir_item)

            url = CMSLSIT['WIRO'][category_type]['resources'] + dir_item
            data_url = re.sub(r'/set/data', r'/data', url)
            self.openExe.webOpen(data_url)
            self.openExe.folderOpen(sandbox_item)

            file_items = self.getResouceItemList(dir_item, file_list)
            self.showList(file_items)
            count = count + len(file_items)

            self.checkDone(f'{dir_item} ({count}/{len(file_list)}, add: {len(file_items)})')

    def start(self):
        self.resetSandBox()
        self.page_count = 1
        self.showStart(self.page_count)
        self.openExe.webOpen(CMSLSIT['WIRO']['WIRO'][self.cms_type]['article'])
        check = self.hearinger.select(f'Did you login WIRO ?', ('y', 'n'), True)

        for page_dir in self.data:
            self.setLang(page_dir)
            self.showData(page_dir, self.page_count)
            category_type = self.checkCategoryType(page_dir)
            url = CMSLSIT['WIRO'][category_type]['article'] + page_dir + CMSLSIT[self.cms_type]['search_key']
            self.openExe.webOpen(url)
            self.throwArtcle(page_dir)
            self.throwResources(page_dir, category_type)
            self.throwDelete(page_dir)
            self.page_count += 1

        self.showEnd(self.page_count)
        self.resetSandBox()
        return


class CMSSitecore(CmsThrow):
    def __init__(self, data, env, cms_type, console):
        super().__init__(data, env, cms_type, console)
        return

    def openContentEditor(self, page_dir):
        key = CMSLSIT[self.cms_type]['search_key']['content']['key']
        lang = CMSLSIT[self.cms_type]['search_key']['content'][self.lang]
        url = key + page_dir + lang
        self.openExe.webOpen(url)

    def throwArtcle(self, page_dir):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['article'] + page_data['loacalcode'] + page_data['meta'] + page_data['html']))
        for file_item in file_list:
            self.checkDone(file_item)

    def throwResources(self, page_dir):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['css'] + page_data['js'] + page_data['img'] + page_data['pdf'] + page_data['other']))

        self.setCloneResources(file_list)
        dir_lsit = self.getResouceDirList(file_list)

        count = 0
        for dir_item in dir_lsit:
            current_dir = os.getcwd()
            sandbox_item = self.fc.creanPath(current_dir + self.sandbox + dir_item)

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

            self.showDirItem(dir_item)

            self.checkDone(f'{dir_item} ({count}/{len(file_list)}, add: {len(file_items)})')

    def showDirItem(self, page_dir):
        self.console.log('')
        content_editor_path = re.sub(r'/', '    ', page_dir)
        self.console.log(content_editor_path)
        self.console.log('')

    def createContenURL(self):
        url = ""
        return url

    def createMediaURL(self):
        url = ""
        return url

    def start(self):
        self.resetSandBox()

        self.page_count = 1
        self.showStart(self.page_count)
        self.openExe.webOpen(CMSLSIT[self.cms_type]['article'])
        self.openExe.webOpen(CMSLSIT[self.cms_type]['resources'])
        check = self.hearinger.select(f'Did you login Sitecore PROD ?', ('y', 'n'), True)

        for page_dir in self.data:
            self.setLang(page_dir)
            self.showData(page_dir, self.page_count)
            page_data = self.data[page_dir]

            self.throwResources(page_dir)
            #self.throwDelete(page_dir)

            self.openExe.openCockpit(page_dir, page_data, self.env)

            self.showDirItem(page_dir)

            self.openContentEditor(page_dir)
            self.throwArtcle(page_dir)

            self.openExe.preview(page_dir)
            self.openExe.preview(page_dir)
            self.hearinger.select(f'check 承認依頼 "{page_dir}" ?', ('y', 'n'), True)
            self.hearinger.select(f'check preview "{page_dir}" ?', ('y', 'n'), True)

            self.page_count += 1

        self.showEnd(self.page_count)
        self.resetSandBox()
        return


#
# MAIN
#
class ThrowList(BacklogApi):
    data = {}

    def __init__(self, comment_url):
        super().__init__(comment_url)

        file_list = self.getUpDatedFile()
        self.throw_lists = list(set(file_list['update'] + file_list['new']))
        self.del_list = file_list['delete']
        self.env = self.getUpDatedEnv()
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
        elif extends == 'php':
            return
        elif extends == 'html':
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

    def getResouceItemList(self, dir_item, file_list):
        all_list = []
        for item in file_list:
            dir_name = os.path.dirname(item)
            if dir_name == dir_item:
                all_list.append(item)

        result_lsit = list(set(all_list))
        return result_lsit


class CMSController(ThrowList):
    def __init__(self, comment_url, cms_type='WIRO'):
        super().__init__(comment_url)
        self.cms_type = cms_type
        self.rc = ResourceChecK(comment_url, cms_type=cms_type)
        self.console = LogMater()
        return

    def checkCMSType(self):
        check_sitecore = re.search(r'Sitecore', self.cms_type)
        check_wiro = re.search(r'WIRO', self.cms_type)

        if not check_sitecore is None:
            return 'Sitecore'
        elif not check_wiro is None:
            return 'WIRO'
        else:
            return 'undifend'

    def updataSvn(self):
        orign_dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env)
        orign_svn = SvnConroller(orign_dir)
        orign_svn.update()
        return

    def start(self):
        self.getPageData(self.getPageList())
        #pprint.pprint(self.data)

        #self.updataSvn()

        check_cms_type = self.checkCMSType()
        if check_cms_type == 'WIRO':
            wiro_cms = CMSWIRO(self.data, self.env, self.cms_type, self.console)
            wiro_cms.start()
        elif check_cms_type == 'Sitecore':
            sitecore_cms = CMSSitecore(self.data, self.env, self.cms_type, self.console)
            sitecore_cms.start()
        else:
            return

        self.rc.start()
        return




