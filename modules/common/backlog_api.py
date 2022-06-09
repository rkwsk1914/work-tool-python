import re
import pprint

from modules.common.api import ApiControlller
from modules.config.setup import BACKLOG_KEY
from modules.common.env_list import EnvList

class BacklogApi(ApiControlller):
    prefix = 'https://sbweb.backlog.jp/api/v2/'
    comment_prefix = 'https://sbweb.backlog.jp/view/'
    apikey = BACKLOG_KEY

    def __init__(self, comment_url):
        request_url = self.createRequestURL(comment_url)
        self.json_data = self.get(request_url)

    def createRequestURL(self, comment_url):
        comment = re.search('#comment-\d*', comment_url).group()
        comment_id = re.search('\d+', comment).group()
        ticket_id = re.search('\w*-\d*', comment_url).group()
        request_url = self.prefix + 'issues/' + ticket_id + '/comments/' + comment_id + '?apiKey=' + self.apikey
        return request_url

    def checkJson(self):
        #print(self.json_data)
        flie_data_text = ''
        if self.json_data['content']:
            content = self.json_data['content']
            re_text = re.search(r'\*\*\*修正した全てのファイル\s?\n\{code\}\n(((■\S{2})|\w|\_|\-|\.|/)*\n)*\{/code\}', content)

            if re_text is None:
                return None
            else:
                all_text = re_text.group()
                without_pre_text = re.sub(r'\*\*\*修正した全てのファイル\s?\n\{code\}\n', '', all_text)
                flie_data_text = re.sub(r'\n\{/code\}', '', without_pre_text)
                #print(flie_data_text)
            return flie_data_text

        return None

    def changeListFromText(self, status_text, flie_data_text):
        rep = re.compile(status_text + '\n(/\S*\n)*')
        rep_text = re.search(rep, flie_data_text)

        if rep_text is None:
            return []
        else:
            re_text = rep_text.group()
            flie_text = re.sub(re.compile(status_text + '\n'), '', re_text)
            result = re.split('\n', flie_text)
            num = len(result) - 1

            if result[num] == '':
                result.pop(-1)
            return result

        return []

    def getFileList(self, flie_data_text):
        #print(flie_data_text)
        file_list = {
            'update': self.changeListFromText('■更新', flie_data_text),
            'new': self.changeListFromText('■新規', flie_data_text),
            'delete': self.changeListFromText('■削除', flie_data_text)
        }
        return file_list

    def getEnvironment(self):
        if self.json_data['content']:
            content = self.json_data['content']
            re_text = re.search('\*\*\*投入環境\n\{code\}\n\S*\n\{/code\}', content)
            #print(re_text)
            if re_text is None:
                return None
            else:
                all_text = re_text.group()
                without_pre_text = re.sub('\*\*\*投入環境\n\{code\}\n', '', all_text)
                env_text = re.sub('\n\{/code\}', '', without_pre_text)
                #print(env_text)

                check_blank = re.search('\(\S*\)', env_text)
                if check_blank is None:

                    envlist = EnvList()
                    result = envlist.getExistEnvironmentFromString(env_text)
                    if result == None:
                        print('backlog\'s enviroment is undefined. : ' + env_text)
                        return None

                    return result
        return None

    def getCacheList(self):
        flie_data_text = ''
        if self.json_data['content']:
            content = self.json_data['content']
            re_text = re.search(r'\*\*\*キャッシュ対策するファイル ※pdfを除くリソース\n\{code\}\n((\w|\_|\-|\.|/)*\n)*\{/code\}', content)
            if re_text is None:
                return None
            else:
                all_text = re_text.group()
                without_pre_text = re.sub(r'\*\*\*キャッシュ対策するファイル ※pdfを除くリソース\n\{code\}\n', '', all_text)
                flie_data_text = re.sub(r'\n\{/code\}', '', without_pre_text)

                result = re.split('\n', flie_data_text)
                num = len(result) - 1

                if result[num] == '':
                    result.pop(-1)
                return result
            return []
        return []

    def getUpDatedFile(self):

        flie_data_text = self.checkJson()
        #print(flie_data_text)

        if flie_data_text is None:
            return None

        file_list = self.getFileList(flie_data_text)
        return file_list

    def getUpDatedEnv(self):
        env = self.getEnvironment()
        return env
