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
from modules.common.cms_checker import CMSchecker
from modules.common.spinner import Spinner

from modules.app.resourcs_check import ResourceChecK

from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.config.db import CMSLSIT
from modules.config.db import ENVLIST

console = LogMater('CMS')

#
# SUB
#
class OpenExe:
    cms_countent = '/cms-part/now-cms-copy.inc'
    localcode_pc = '/cms-part/now-sitecore-localcode-pc.inc'
    localcode_sp = '/cms-part/now-sitecore-localcode-sp.inc'
    conten_pc = '/cms-part/now-sitecore-content-pc.inc'
    conten_sp = '/cms-part/now-sitecore-content-sp.inc'
    test = False

    cookipit = ''

    def __init__(self):
        self.app_name = __class__.__name__
        self.fc = FileController()
        self.sc = Scraping()

    def folderOpen(self, full_path):
        try:
            if self.test == False:
                p = subprocess.Popen(["explorer",  full_path], shell=True)
            else:
                print('folder open')
        except:
            console.error(self.app_name, f'Folder open failed. : {full_path}')

    def webOpen(self, url):
        try:
            if self.test == False:
                webbrowser.open(url)
            else:
                print(f'open web : {url}')
        except:
            console.error(self.app_name, f'Web site open failed. : {url}')

    def winMergeOpen(self, new_content):
        current_dir = os.getcwd()
        now_cms_content = self.fc.creanPath(current_dir + self.cms_countent)
        cmd = 'start WinMergeU ' + new_content + ' ' + now_cms_content
        try:
            if self.test == False:
                subprocess.check_call(cmd, shell=True)
            else:
                print(cmd)
        except:
            console.error(self.app_name, f'WinMerge failed. : {cmd}')
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
            console.error(self.app_name, f'request failed. : {url_auth}')
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
        self.webOpen(url)


class showMessage():
    def __init__(self, data):
        self.app_name = __class__.__name__
        self.data = data
        return

    def showEnd(self, page_count):
        console.log(self.app_name, '')
        console.log(self.app_name, f'({page_count - 1}/{len(self.data)}) Page List')
        console.log(self.app_name, '-------------------------------------------------------------------------------------')

        self.showList(self.data)

        console.log(self.app_name, '-------------------------------------------------------------------------------------')
        console.log(self.app_name, '                Completed.')
        console.log(self.app_name, '')

        input('Did you close all sandbox folder? : ')
        return

    def showStart(self, page_count):
        console.log(self.app_name, '')
        console.log(self.app_name, f'({page_count}/{len(self.data)}) Page List')
        console.log(self.app_name, '-------------------------------------------------------------------------------------')

        self.showList(self.data)

        console.log(self.app_name, '-------------------------------------------------------------------------------------')
        console.log(self.app_name, '')

    def showData(self, page_dir, page_count):
        page_data = self.data[page_dir]

        console.log(self.app_name, '')
        console.log(self.app_name, f'({page_count}/{len(self.data)})')
        console.log(self.app_name, f'{page_dir}')
        console.log(self.app_name, '-------------------------------------------------------------------------------------')
        console.log(self.app_name, f'   article: {len(page_data["article"])}     loacalcode: {len(page_data["loacalcode"])}')
        console.log(self.app_name, f'   meta {len(page_data["meta"])}    html: {len(page_data["html"])}')
        console.log(self.app_name, '-------------------------------------------------------------------------------------')
        console.log(self.app_name, f'   css: {len(page_data["css"])}    js: {len(page_data["js"])}')
        console.log(self.app_name, f'   img: {len(page_data["img"])}')
        console.log(self.app_name, f'   pdf: {len(page_data["pdf"])}    other: {len(page_data["other"])}')
        console.log(self.app_name, '-------------------------------------------------------------------------------------')
        console.log(self.app_name, f'   delete: {len(page_data["delete"])}')
        console.log(self.app_name, '-------------------------------------------------------------------------------------')
        console.log(self.app_name, '')

    def showList (self, array_lsit):
        for item in array_lsit:
            console.log(self.app_name, f'    {item}')


class CmsThrow(showMessage):
    page_count = 0
    sandbox = '/cms-part/sandbox'

    def __init__(self, data, env, cms_type):
        super().__init__(data)
        self.app_name = __class__.__name__
        self.env = env
        self.data = data
        self.cms_type = cms_type

        console.log(self.app_name, f'(init) env : {env}')
        console.log(self.app_name, f'(init) cms : {cms_type}')
        console.log(self.app_name, '')

        self.hearinger = Hearing()
        self.fc = FileController()
        self.cms_c = CMSchecker(cms_type)
        self.openExe = OpenExe()
        return

    def resetSandBox(self):
        current_dir = os.getcwd()
        sandbox = current_dir + self.sandbox
        check = os.path.exists(sandbox)
        if check == True:
            self.fc.empty(sandbox)
        else:
            os.mkdir(sandbox)

    def setItemPath(self, item):
        return self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + item)

    def setCloneResources(self, file_list):
        for item in file_list:
            origin = self.setItemPath(item)

            current_dir = os.getcwd()
            clone = self.fc.creanPath(current_dir + self.sandbox + item)
            clone_dir = os.path.dirname(clone)
            self.fc.copy(origin, clone)

    def checkDone(self, item):
        check = self.hearinger.select(f'(progress: {self.page_count}/{len(self.data)} ) Did you input {item} ?', ('y', 'n'), True)

        if check == 'n':
            console.log(self.app_name, f'again input {item}')
            self.checkDone(item)
            return

        console.log(self.app_name, '')
        return

    def checkDelete(self, item):
        check = self.hearinger.select(f'Did you delete {file_item} ?', ('y', 'n'), True)

        if check == 'n':
            console.log(self.app_name, f'again delete {item}')
            self.checkDelete(item)
        return

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


class CMSWIRO(CmsThrow):
    def __init__(self, data, env, cms_type):
        super().__init__(data, env, cms_type)
        self.app_name = __class__.__name__
        return

    def throwArtcle(self, page_dir):
        file_list = list(set(page_data['article'] + page_data['loacalcode'] + page_data['meta'] + page_data['html']))

        if len(file_list) < 1:
            return

        cms_data = self.cms_c.setCMSdata(page_dir)
        lang = self.cms_c.checkLang(page_dir)
        self.openExe.webOpen(cms_data[lang]['article'] + page_dir)

        for file_item in file_list:
            new_content = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + '/' + file_item)
            self.openExe.winMergeOpen(new_content)
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

            cms_data = self.cms_c.setCMSdata(dir_item)
            lang = self.cms_c.checkLang(page_dir)
            url = cms_data[lang]['resources'] + dir_item
            common_url = re.sub(r'/set/common', r'/common', url)
            data_url = re.sub(r'/set/data', r'/data', common_url)
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
        self.openExe.webOpen(CMSLSIT['WIRO']['WIRO']['ja']['article'])
        check = self.hearinger.select(f'Did you login WIRO ?', ('y', 'n'), True)

        for page_dir in self.data:
            self.showData(page_dir, self.page_count)
            self.throwArtcle(page_dir)
            self.throwResources(page_dir)
            self.page_count += 1

        self.showEnd(self.page_count)
        self.resetSandBox()
        return


class ExceptionContets():
    def __init__(self):
        return

    # mode = page | content
    def check(self, dir_item, mode):
        result = dir_item

        check_pc_include = re.search(r'/mobile/design/parts/common/pc/include/support/', dir_item)
        if not check_pc_include is None:
            if mode == 'page':
                result = '/mobile/_Metadata/common/pc/include/support/'
            else:
                result = re.sub(r'/mobile/design/parts/common/pc/include/support/', '/mobile/_Metadata/common/pc/include/support/', dir_item)

        check_sp_include = re.search(r'/mobile/design/parts/common/sp/include/support/', dir_item)
        if not check_sp_include is None:
            if mode == 'page':
                result = '/mobile/_Metadata/common/sp/include/support/'
            else:
                result = re.sub(r'/mobile/design/parts/common/sp/include/support/', '/mobile/_Metadata/common/sp/include/support/', dir_item)

        check_pc_cancellation_include = re.search(r'/mobile/design/parts/common/pc/include/support/cancellation-contact/', dir_item)
        if not check_pc_cancellation_include is None:
            if mode == 'page':
                result = '/mobile/_Metadata/common/pc/include/support/cancellation-contact/'
            else:
                result = re.sub(r'/mobile/design/parts/common/pc/include/support/cancellation-contact/', '/mobile/_Metadata/common/pc/include/support/cancellation-contact/', dir_item)

        check_sp_cancellation_include = re.search(r'/mobile/design/parts/common/sp/include/support/cancellation-contact/', dir_item)
        if not check_sp_cancellation_include is None:
            if mode == 'page':
                result = '/mobile/_Metadata/common/sp/include/support/cancellation-contact/'
            else:
                result = re.sub(r'/mobile/design/parts/common/sp/include/support/cancellation-contact/', '/mobile/_Metadata/common/sp/include/support/cancellation-contact/', dir_item)

        check_pc_mobile_top = re.search(r'/mobile/design/parts/top/pc/', dir_item)
        if not check_pc_mobile_top is None:
            result = '/mobile/_Local/HTML_PC_10'

        check_sp_mobile_top = re.search(r'/mobile/design/parts/top/sp/', dir_item)
        if not check_sp_mobile_top is None:
            result = '/mobile/_Local/HTML_SP_10'

        return result


class CMSSitecore(CmsThrow):
    def __init__(self, data, env, cms_type):
        super().__init__(data, env, cms_type)
        self.app_name = __class__.__name__
        self.ex = ExceptionContets()
        return

    def checkExeption(self, page_dir, file_item):
        isExeption = False

        sitecore_content = self.ex.check(file_item, 'content')

        if sitecore_content == file_item:
            isExeption = False
        else:
            isExeption = True

        return isExeption

    def throwArtcle(self, page_dir):
        page_data = self.data[page_dir]
        file_list = list(set(page_data['article'] + page_data['loacalcode'] + page_data['meta']))
        alll_file_list = list(set(page_data['article'] + page_data['loacalcode'] + page_data['meta'] + page_data['html']))

        if len(alll_file_list) < 1:
            return

        url = self.createContenURL(page_dir)

        if len(file_list) > 0:
            isExeption = self.checkExeption(page_dir, file_list[0])

            if (isExeption == True):
                self.openExe.webOpen(url)
                self.showDirItem(page_dir)
                for file_item in file_list:
                    new_content = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + '/' + file_item)
                    self.openExe.winMergeOpen(new_content)
            else:
                self.openExe.webOpen(url)
                self.openExe.openCockpit(page_dir, page_data, self.env)
                self.showDirItem(page_dir)

            for file_item in file_list:
                self.checkDone(file_item)

        for html_item in page_data['html']:
            self.openExe.webOpen(self.createContenURL(html_item))
            self.openExe.winMergeOpen(self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + '/' + html_item))
            self.checkDone(html_item)

        self.openExe.preview(page_dir)
        self.hearinger.select(f'check preview "{page_dir}" ?', ('y', 'n'), True)
        self.hearinger.select(f'check 承認依頼 "{page_dir}" ?', ('y', 'n'), True)
        return

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

            url = self.createMediaURL(dir_item)
            self.openExe.webOpen(url)

            self.showDirItem(dir_item)
            self.checkDone(f'{dir_item} ({count}/{len(file_list)}, add: {len(file_items)})')

    def showDirItem(self, page_dir):
        print('')
        content_editor_path = re.sub(r'/', '    ', page_dir)
        print(content_editor_path)
        print('')

    def createContenURL(self, dir_item):
        cms_data = self.cms_c.setCMSdata(dir_item)
        lang = self.cms_c.checkLang(dir_item)
        dir = self.ex.check(dir_item, 'content')
        if lang == 'ja':
            url = cms_data['search_key']['content']['key'] + dir + cms_data['search_key']['media'][lang]
            return url
        if lang == 'en':
            en_dir = re.sub(r'en/', '', dir)
            url = cms_data['search_key']['content']['key'] + en_dir + cms_data['search_key']['media'][lang]
            return url

    def createMediaURL(self, dir_item):
        cms_data = self.cms_c.setCMSdata(dir_item)
        lang = self.cms_c.checkLang(dir_item)
        if lang == 'ja':
            url = cms_data['search_key']['media']['key'] + dir_item + cms_data['search_key']['media'][lang]
            return url
        if lang == 'en':
            #en_dir_item = re.sub(r'en/', '', dir_item)
            url = cms_data['search_key']['media']['key'] + dir_item + cms_data['search_key']['media'][lang]
            return url

    def start(self):
        self.resetSandBox()

        self.page_count = 1
        self.showStart(self.page_count)
        self.openExe.webOpen(CMSLSIT[self.cms_type]['top'])
        check = self.hearinger.select(f'Did you login Sitecore ?', ('y', 'n'), True)

        if check == 'n':
                return

        for page_dir in self.data:
            self.showData(page_dir, self.page_count)
            page_data = self.data[page_dir]

            self.throwResources(page_dir)
            self.throwArtcle(page_dir)

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
        self.app_name = __class__.__name__

        file_list = self.getUpDatedFile()
        self.throw_lists = self.getThrowFileList(file_list)
        self.del_list = file_list['delete']
        self.env = self.getUpDatedEnv()
        self.fc = FileController()
        self.ex = ExceptionContets()

    def getThrowFileList(self, file_list):
        all_file_list = list(set(file_list['update'] + file_list['new']))

        for file_item in all_file_list:
            check_src = re.search(r'/src', file_item)

            if not check_src is None:
                all_file_list.pop(all_file_list.index(file_item))

        for file_item in all_file_list:
            check_src = re.search(r'/src', file_item)

            if not check_src is None:
                all_file_list.pop(all_file_list.index(file_item))

        result = sorted(all_file_list)
        #pprint.pprint(result)
        return result

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
            page_path = self.ex.check(self.getPagePath(item), 'page')
            all_page_list.append(page_path)

        for item_del in self.del_list:
            page_path_del = self.getPagePath(item_del)
            all_page_list.append(page_path_del)

        page_list = list(set(all_page_list))
        new_page_list = sorted(page_list)
        #pprint.pprint(page_list)
        return new_page_list

    def getPageData(self, page_list):
        for page in page_list:
            self.data[page] = self.createPageData()

            for item in self.throw_lists:
                page_path = self.ex.check(self.getPagePath(item), 'page')
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


class CMSController(ThrowList):
    def __init__(self, comment_url, cms_type):
        super().__init__(comment_url)
        self.app_name = __class__.__name__
        self.cms_type = cms_type

        self.cms_c = CMSchecker(cms_type)
        self.rc = ResourceChecK(comment_url, cms_type=cms_type)
        return

    def updataSvn(self):
        orign_dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env)
        orign_svn = SvnConroller(orign_dir)
        return Spinner(orign_svn.update)()

    def start(self):
        self.getPageData(self.getPageList())

        checkSvn =  self.updataSvn()
        if checkSvn == False:
            return

        check_cms_type = self.cms_c.checkCMSType()
        if check_cms_type == 'WIRO':
            console.log(self.app_name, 'Throw WIRO')
            wiro_cms = CMSWIRO(self.data, self.env, self.cms_type)
            wiro_cms.start()
        elif check_cms_type == 'Sitecore':
            console.log(self.app_name, 'Throw Sitecore')
            sitecore_cms = CMSSitecore(self.data, self.env, self.cms_type)
            sitecore_cms.start()
        else:
            return

        self.rc.start()
        return




