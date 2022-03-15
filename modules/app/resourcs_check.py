import urllib.request
import base64
import re
import os
import pprint

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.backlog_api import BacklogApi

from modules.config.db import CMSLSIT
from modules.config.db import ENVLIST

class ResourceChecK(BacklogApi):
    miss_list = []
    fail_list = []

    def __init__(self, comment_url, cms_type):
        super().__init__(comment_url)
        self.cms_type = cms_type
        self.console = LogMater()
        self.fc = FileController()

        file_list = self.getUpDatedFile()
        #pprint.pprint(file_list)
        all_list = list(set(file_list['update'] + file_list['new']))
        self.check_list = self.getResouceList(all_list)
        #pprint.pprint(self.check_list)
        self.env = self.getUpDatedEnv()

    def getResouceList(self, file_list):
        check_list = []
        for item in file_list:
            path = self.fc.creanPath(item)
            split_data = os.path.splitext(path)
            basename = os.path.basename(item)
            #print(basename)
            extends = re.sub(r'\.', '', split_data[1])

            #print(extends)
            if extends == 'php' \
                or extends == 'html' \
                or extends == 'inc':
                continue
            else:
                check_list.append(item)

        result_lsit = list(set(check_list))
        return result_lsit

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

    def check(self, item):
        data_a = ''
        data_b = ''

        url_a = ENVLIST[self.env]['domain']['pc'] + item
        account_a = ENVLIST[self.env]['account']
        password_a = ENVLIST[self.env]['password']
        request_a = self.createRequest(url_a, account_a, password_a)

        url_b = ''
        check_cms_type = self.checkCMSType()
        if check_cms_type == 'WIRO':
            url_b = CMSLSIT[self.cms_type]['preview']['pc'] + item
        elif check_cms_type == 'Sitecore':
            url_b = CMSLSIT[self.cms_type]['preview'] + item
        else:
            self.console.log('')
            self.console.log(f'Not found CMS domain. {self.cms_type}')
            self.console.log('')
            return

        account_b = CMSLSIT[self.cms_type]['account']
        password_b = CMSLSIT[self.cms_type]['password']
        request_b = self.createRequest(url_b, account_b, password_b)

        data_a = self.getUrlResponse(request_a, url_a)
        data_b = self.getUrlResponse(request_b, url_b)

        if data_a == '' or data_b == '':
            self.fail_list.append(item)
            self.console.log('Fail')
            self.console.log(url_a)
            self.console.log(url_b)
            self.console.log('')
            return

        if data_a == data_b:
            self.console.log(True)
            self.console.log(url_a)
            self.console.log(url_b)
            self.console.log('')
        else:
            self.miss_list.append(item)
            self.console.log(False)
            self.console.log(url_a)
            self.console.log(url_b)
            self.console.log('')
        return

    def showMissList(self):
        if len(self.miss_list) < 1:
            self.console.log('')
            self.console.log('')
            self.console.log('All Resources are Same. OK. ')
            return
        else:
            self.console.log('')
            self.console.log('')
            self.console.log('Difference exist. ')

            for item in self.miss_list:
                self.console.log(item)
                self.console.log('')
        return

    def showFailList(self):
        if len(self.fail_list) < 1:
            self.console.log('')
            self.console.log('')
            self.console.log('Request URL \'s are All Success. ')
            self.console.log('')
            self.console.log('')
            return
        else:
            self.console.log('')
            self.console.log('')
            self.console.log('Request URL \'s has Fail. ')

            for item in self.fail_list:
                self.console.log(item)
                self.console.log('')
        return

    def start (self):
        for item in self.check_list:
            self.check(item)
        self.showMissList()
        self.showFailList()
        return