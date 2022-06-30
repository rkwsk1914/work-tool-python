import urllib.request
import base64
import re
import os
import pprint

from modules.common.file_controller import FileController
from modules.common.log_master import LogMater
from modules.common.backlog_api import BacklogApi
from modules.common.cms_checker import CMSchecker

from modules.config.db import CMSLSIT
from modules.config.db import ENVLIST

console = LogMater('ResourceChecK')

class RequestServer():
    def __init__(self, cms_type, env):
        self.app_name = __class__.__name__
        self.env = env
        self.cms_c = CMSchecker(cms_type)
        return

    def createRequest(self, url, username, password):
        # Basic認証用の文字列を作成.
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(username, password).encode('utf-8'))

        # Basic認証付きの、GETリクエストを作成する.
        request = urllib.request.Request(url,
            headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        return request

    def getUrlResponse(self, request, url):
        response = None
        data = ''
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            console.log(self.app_name, f'    {e.reason} : {url}')
        else:
            data = response.read()
        finally:
            if response:
                response.close()
        return data

    def requestTestUp(self, item, device):
        url_a = ENVLIST[self.env]['domain'][device] + item
        account_a = ENVLIST[self.env]['account']
        password_a = ENVLIST[self.env]['password']
        request_a = self.createRequest(url_a, account_a, password_a)
        result = {
            'data': self.getUrlResponse(request_a, url_a),
            'url': url_a
        }
        return result

    def requestPreview(self, item, device):
        url_b = ''

        cms_data = self.cms_c.setCMSdata(item)
        check_cms_type = self.cms_c.checkCMSType()
        if check_cms_type == 'WIRO':
            url_b = cms_data['preview'][device] + item
        elif check_cms_type == 'Sitecore':
            url_b = cms_data['preview'] + item
        else:
            print('')
            console.error(self.app_name, f'Not found CMS domain. {self.cms_type}')
            print('')
            return None

        account_b = cms_data['account']
        password_b = cms_data['password']
        request_b = self.createRequest(url_b, account_b, password_b)

        result = {
            'data': self.getUrlResponse(request_b, url_b),
            'url': url_b
        }
        return result

class ResourceChecK(BacklogApi):
    miss_list = []
    fail_list = []

    def __init__(self, comment_url, cms_type):
        super().__init__(comment_url)
        self.app_name = __class__.__name__

        self.fc = FileController()
        self.cms_c = CMSchecker(cms_type)

        file_list = self.getUpDatedFile()
        all_list = list(set(file_list['update'] + file_list['new']))
        self.check_list = self.getResouceList(all_list)
        self.env = self.getUpDatedEnv()

        self.rs = RequestServer(cms_type, self.env)
        return

    def getResouceList(self, file_list):
        check_list = []
        for item in file_list:
            path = self.fc.creanPath(item)
            split_data = os.path.splitext(path)
            basename = os.path.basename(item)
            extends = re.sub(r'\.', '', split_data[1])

            if extends == 'php' \
                or extends == 'html' \
                or extends == 'inc':
                continue
            else:
                check_list.append(item)

        result_lsit = list(set(check_list))
        return result_lsit

    def check(self, item, device):
        result_a = self.rs.requestTestUp(item, device)
        result_b = self.rs.requestPreview(item, device)

        if result_a['data'] == '' or result_b['data'] == '':
            self.fail_list.append(item)
            console.log(self.app_name, 'Fail')
            console.log(self.app_name, result_a['url'])
            console.log(self.app_name, result_b['url'])
            console.log(self.app_name, '')
            return

        if result_a['data'] == result_b['data']:
            console.log(self.app_name, True)
            console.log(self.app_name, result_a['url'])
            console.log(self.app_name, result_b['url'])
            console.log(self.app_name, '')
        else:
            self.miss_list.append(item)
            console.log(self.app_name, False)
            console.log(self.app_name, result_a['url'])
            console.log(self.app_name, result_b['url'])
            console.log(self.app_name, '')
        return

    def showMissList(self):
        miss_list_fix = set(self.miss_list)
        if len(miss_list_fix) < 1:
            console.log(self.app_name, '')
            console.log(self.app_name, '')
            console.log(self.app_name, 'All Resources are Same. OK. ')
            return
        else:
            console.log(self.app_name, '')
            console.log(self.app_name, '')
            console.log(self.app_name, 'Difference exist. ')

            for item in miss_list_fix:
                console.log(self.app_name, item)
                console.log(self.app_name, '')
        return

    def showFailList(self):
        fail_list_fix = set(self.fail_list)
        if len(fail_list_fix) < 1:
            console.log(self.app_name, '')
            console.log(self.app_name, '')
            console.log(self.app_name, 'Request URL \'s are All Success. ')
            console.log(self.app_name, '')
            console.log(self.app_name, '')
            return
        else:
            console.log(self.app_name, '')
            console.log(self.app_name, '')
            console.log(self.app_name, 'Request URL \'s has Fail. ')

            for item in fail_list_fix:
                console.log(self.app_name, item)
                console.log(self.app_name, '')
        return

    def start (self):
        for item in self.check_list:
            self.check(item, 'pc')
            self.check(item, 'sp')

        self.showFailList()
        self.showMissList()
        return