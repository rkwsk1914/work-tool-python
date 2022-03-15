import urllib.request
from bs4 import BeautifulSoup
import re
import os
import subprocess
import base64
import pprint

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.scraping import Scraping

from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.config.setup import SOFTBANK_DOMAIN
from modules.config.setup import SOFTBANK_CDN
from modules.config.db import CMSLSIT
from modules.config.db import ENVLIST

class OpenExe:
    cms_countent = '/catch-up-part/now-cms-copy.inc'
    cookipit = ''

    def __init__(self, page_path, cms_type, env, console):
        self.fc = FileController()
        self.page_path = page_path
        self.cms_type = cms_type
        self.env = env
        self.console = console

    def openWiroFiles(self):
        self.winMergeOpen('wiro_content.inc')
        self.winMergeOpen('wiro_localcode.inc')
        self.winMergeOpen('wiro_meta.inc')
        self.winMergeOpen('wiro_ogimage.inc')

    def webOpen(self, url):
        try:
            #webbrowser.open(url)
            print('open web')
        except:
            log_msg = f'''

            Web site open failed. : {url}
            '''.strip()
            self.console.log(log_msg)

    def winMergeOpen(self, inc_item):
        current_dir = os.getcwd()
        local_content = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env + self.page_path + inc_item)
        cms_countent = self.fc.creanPath(current_dir + self.cms_countent)
        cmd = 'start WinMergeU ' + cms_countent + ' ' + local_content
        try:
            #subprocess.check_call(cmd, shell=True)
            print(cmd)
        except:
            log_msg = f'''

            WinMerge failed. : {cmd}
            '''.strip()
            self.console.log(log_msg)
            return False

    def openCockpit(self):
        url = ENVLIST[self.env]['domain']['pc'] + CMSLSIT[self.cms_type]['checkTool'] + '/?' + self.page_path + '/'
        account = ENVLIST[self.env]['account']
        password = ENVLIST[self.env]['password']
        url_auth = re.sub(r'https://', f'https://{account}:{password}@', url)
        try:
            #webbrowser.open(url_auth)
            print('open web')
        except:
            log_msg = f'''

            Web site open failed. : {url_auth}
            '''.strip()
            self.console.log(log_msg)


class HTMLGatter:
    img_list = []
    pdf_list = []
    script_list = []
    title = None
    meta_list = []
    link_list = []
    soup_sp = None
    soup_pc = None
    css_list = []
    js_list = []
    sandbox = '/catch-up-part/sandbox'

    def __init__(self, cms_type):
        self.sc = Scraping()
        self.fc = FileController()
        self.cms_type = cms_type

    def getHTMLData(self, url):
        print('')
        print(f'Now read {url} ...')
        data_sp = self.sc.getPageDataVerSP(url)
        data_pc = self.sc.getPageDataVerPC(url)
        self.soup_sp = BeautifulSoup(data_sp, 'html.parser')
        self.soup_pc = BeautifulSoup(data_pc, 'html.parser')
        self.sc.close()
        self.getList()
        print('')
        print(f'Compelte reading {url}')
        print('')
        return

    def getList(self):
        #self.getAList()
        #self.getImgList()
        #self.geScrpitList()
        self.getLinkList()
        #self.getMetaList()
        #self.getTitle()
        self.getCss()
        #self.getJavaScript()
        return

    def getAList(self):
        list_sp = self.soup_sp.find_all('a', href=re.compile(r"\.pdf"))
        list_pc = self.soup_pc.find_all('a', href=re.compile(r"\.pdf"))
        a_list = list(set(list_pc + list_sp))
        for a in a_list:
            href = a.get('href')
            crean_href = re.sub(r'//cdn.softbank.jp|//www.softbank.jp', '', href)
            self.pdf_list.append(crean_href)

        #print('')
        #print('pdf')
        #pprint.pprint(self.pdf_list)
        return

    def getImgList(self):
        list_sp = self.soup_sp.find_all('img')
        list_pc = self.soup_pc.find_all('img')
        img_tag_list = list(set(list_pc + list_sp))
        for img_tag in img_tag_list:
            src = img_tag.get('src')
            crean_src = re.sub(r'//cdn.softbank.jp|//www.softbank.jp', '', src)
            self.img_list.append(crean_src)

        #print('')
        #print('img')
        #pprint.pprint(self.img_list)
        return

    def geScrpitList(self):
        list_sp = self.soup_sp.find_all('script')
        list_pc = self.soup_pc.find_all('script')
        self.script_list = list(set(list_pc + list_sp))
        #pprint.pprint(self.script_list)
        return

    def getLinkList(self):
        list_sp = self.soup_sp.find_all('link')
        list_pc = self.soup_pc.find_all('link')
        self.link_list = list(set(list_pc + list_sp))
        #pprint.pprint(self.link_list)
        return

    def getMetaList(self):
        list_sp = self.soup_sp.find_all('meta')
        list_pc = self.soup_pc.find_all('meta')
        self.meta_list = list(set(list_pc + list_sp))
        #print('')
        #print('meta')
        #pprint.pprint(self.meta_list)
        return

    def getTitle(self):
        list_sp = self.soup_sp.find_all('title')
        list_pc = self.soup_pc.find_all('title')
        self.title = list(set(list_pc + list_sp))
        #print('')
        #print('title')
        #pprint.pprint(self.title)
        return

    def getCss(self):
        for link in self.link_list:
            href = link.get('href')
            checK_site_css = re.search(r'/site/set/data|/site/set/common', href)
            #print(checK_site_css)
            if checK_site_css is None:
                checK_my_css = re.search(r'/set/data|/set/common', href)
                if checK_my_css is None:
                    continue
                else:
                    crean_href = re.sub(r'//cdn.softbank.jp|//www.softbank.jp', '', href)
                    self.css_list.append(crean_href)
        #print('')
        #print('css')
        #pprint.pprint(self.css_list)
        for css in self.css_list:
            request = self.createRequestURL(css)
            #request = SOFTBANK_DOMAIN + css
            data = self.getUrlResponse(request, css)
            #pprint.pprint(data)
            #print('')
            #print(data)
            #print('')
            self.readCode(data)
        return

    def getJavaScript(self):
        for script in self.script_list:
            #type_elem = script.get('type')
            src = script.get('src')
            if src:
                checK_my_js = re.search(r'/set/data|/set/common', src)
                if checK_my_js is None:
                    continue
                else:
                    crean_src = re.sub(r'//cdn.softbank.jp|//www.softbank.jp', '', src)
                    self.js_list.append(crean_src)
        #print('')
        #print('JavaScript')
        #pprint.pprint(self.js_list)
        #for js in self.js_list:
        #    url = SOFTBANK_DOMAIN + js
        #    data = self.getUrlResponse(url)
        #    self.readCode(data)
        return


    def getUrlResponse(self, request, url):
        response = None
        data = ''
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            print(f'    {e.reason} : {url}')
            #self.console.log(f'    {e.reason} : {url}')
        else:
            data = response.read()
        finally:
            if response:
                response.close()
        return data

    def readCode(self, data):
        d = data.decode('utf-8')
        print(type(data))
        print(type(d))
        #pprint.pprint(d)
        print(len(data))
        print(len(d))
        lines = re.split(r'\'', d)
        lines_a = re.split(r'\n', d)
        print(type(lines))
        print(len(lines))
        print(type(lines_a))
        print(len(lines_a))
        #pprint.pprint(str(data))
        #print(type(data))
        #lines = re.split(r'\n', data.decode('utf-8'))
        #pprint.pprint(lines)
        #print(len(lines))
        for line in lines_a:
            #chekc_img = re.search(r'png|PNG|jpg|jpeg|JPG|JPEG|pjp|pjpeg|jfif|jpe|gif|svg', line)
            #print(chekc_img )
            #if chekc_img is None:
            #    continue
            #else:
            #print(line)
            #line = item.decode('utf-8')
            check = re.search(r'\/(.+\/)+.+\.\w+', line)
            print(check)
            if check is None:
                continue
            else:
                print(line)

    def download(self, url):
        path = self.fc.creanPath(url)
        name = os.path.basename(path)
        current_dir = os.getcwd()
        clone = self.fc.creanPath(current_dir + self.sandbox + name)
        print(clone)
        urllib.request.urlretrieve(url, clone)

    def createRequest(self, url, username, password):
        # Basic認証用の文字列を作成.
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(username, password).encode('utf-8'))

        # Basic認証付きの、GETリクエストを作成する.
        request = urllib.request.Request(url,
            headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        return request

    def createRequestURL(self, item):
        check_cms_type = self.checkCMSType()
        cms_url = ''
        if check_cms_type == 'WIRO':
            cms_url = CMSLSIT[self.cms_type]['preview']['pc'] + item
        elif check_cms_type == 'Sitecore':
            cms_url = CMSLSIT[self.cms_type]['preview'] + item
        else:
            #self.console.log('')
            #self.console.log(f'Not found CMS domain. {self.cms_type}')
            s#elf.console.log('')
            return

        print(cms_url)

        account = CMSLSIT[self.cms_type]['account']
        password = CMSLSIT[self.cms_type]['password']
        request = self.createRequest(cms_url, account, password)
        return request

    def checkCMSType(self):
        check_sitecore = re.search(r'Sitecore', self.cms_type)
        check_wiro = re.search(r'WIRO', self.cms_type)

        if not check_sitecore is None:
            return 'Sitecore'
        elif not check_wiro is None:
            return 'WIRO'
        else:
            return 'undifend'

class CatchUp:
    def __init__(self, page_url, cms_type, env):
        self.console = LogMater()
        self.fc = FileController()

        self.cms_type = cms_type
        self.page_url = page_url
        self.page_path = self.getPagePath(page_url)
        #print(env)
        self.openExe = OpenExe(self.page_path, cms_type, env, self.console)
        self.hg = HTMLGatter(cms_type)
        return

    def chenageCMSRequest(self, page_url):
        cms_domain = ''
        username = ''
        password = ''
        check_cms_type = self.checkCMSType()
        if check_cms_type == 'Sitecore':
            cms_url = CMSLSIT[self.cms_type]['preview'] + self.page_path
            username = CMSLSIT[self.cms_type]['account']
            password = CMSLSIT[self.cms_type]['password']

        if check_cms_type == 'WIRO':
            cms_url = CMSLSIT[self.cms_type]['preview']['pc'] + self.page_path
            username = CMSLSIT[self.cms_type]['account']
            password = CMSLSIT[self.cms_type]['password']

        url_auth = re.sub(r'https://', f'https://{username}:{password}@', cms_url)
        print(url_auth)
        request = self.createRequest(cms_url, username, password)
        return request

    def getPagePath(self, page_url):
        page_path = re.sub(SOFTBANK_DOMAIN, '', page_url)
        return page_path

    def getResoucePath(self, reslurce_url):
        resource_path = re.sub(SOFTBANK_CDN, '', page_url)
        return resource_path

    def checkCMSType(self):
        check_sitecore = re.search(r'Sitecore', self.cms_type)
        check_wiro = re.search(r'WIRO', self.cms_type)

        if not check_sitecore is None:
            return 'Sitecore'
        elif not check_wiro is None:
            return 'WIRO'
        else:
            return 'undifend'

    def getResouceList(self):
        return

    def createRequest(self, url, username, password):
        # Basic認証用の文字列を作成.
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(username, password).encode('utf-8'))

        # Basic認証付きの、GETリクエストを作成する.
        request = urllib.request.Request(url,
            headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        return request

    def checkCMSType(self):
        check_sitecore = re.search(r'Sitecore', self.cms_type)
        check_wiro = re.search(r'WIRO', self.cms_type)

        if not check_sitecore is None:
            return 'Sitecore'
        elif not check_wiro is None:
            return 'WIRO'
        else:
            return 'undifend'

    def getUrlResponse(self, request, url):
        response = None
        data = ''
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            self.console.log(f'    {e.reason} : {url}')
        else:
            data = response.read()
        finally:
            if response:
                response.close()
        return data

    def getArticle(self):
        check_cms_type = self.checkCMSType()
        if check_cms_type == 'Sitecore':
            self.console.log('')
            content_editor_path = re.sub(r'/', '    ', self.page_path)
            self.console.log(content_editor_path)
            self.console.log('')
            self.openExe.webOpen(CMSLSIT[self.cms_type]['article'])
            self.openExe.openWiroFiles()
            self.openExe.openCockpit()
            return

        if check_cms_type == 'WIRO':
            url = CMSLSIT[self.cms_type]['article'] + self.page_path + CMSLSIT[self.cms_type]['search_key']
            #print(url)
            self.openExe.webOpen(url)
            self.openExe.openWiroFiles()
        return

    def start(self):
        #self.getArticle()
        self.hg.getHTMLData(self.page_url)
        return