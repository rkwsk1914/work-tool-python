import pprint
import subprocess
import re
import os
import time
import asyncio
import glob
import numpy as np
from multiprocessing import Pool

from modules.common.hearing import Hearing
from modules.common.log_master import LogMater
from modules.common.file_controller import FileController
from modules.common.backlog_api import BacklogApi

#from modules.config.setup import DEVELOPMENT_ENVIRONMENT
from modules.common.config import DEVELOPMENT_ENVIRONMENT

console = LogMater('Cache')

class Message():
    def __init__(self):
        self.app_name = __class__.__name__
        return

    def showList(self, list_title, list_array):
        print('')
        console.log(self.app_name, f'{list_title}')
        console.log(self.app_name, "=========================================================")

        for item in list_array:
            console.log(self.app_name, item)

        console.log(self.app_name, "=========================================================")
        console.log(self.app_name, f'                       Number of target: {len(list_array)}')
        print('')
        return


class CountTimer():
    def __init__(self):
        self.app_name = __class__.__name__
        return

    def start(self, processe_name, msg=''):
        # 計測開始
        console.log(self.app_name, f'{msg} {processe_name} start.')
        self.start = time.time()
        print('しばらくお待ち下さい。Please wait a moment.')
        return

    def finish(self, processe_name, msg=''):
        # 計測終了
        end = time.time()
        delta = end - self.start
        console.log(self.app_name, f'{msg} {processe_name} finish. [ processing time(/seconds): {format(round(delta,3))} ]')
        return


class CacheSVN():
    def __init__(self, env):
        self.app_name = __class__.__name__
        self.env = env
        self.fc = FileController()
        self.ct = CountTimer()

        self.envPath = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '\\' + self.env)
        return

    def __setSVNCommand(self):
        cmd = 'svn st ' + self.envPath
        return cmd

    def __doCheckSvn(self, cmd):
        try:
            cp = subprocess.run(cmd, capture_output=True)
        except:
            console.error(self.app_name, f'request failed. : {url_auth}')
            return []
        else:
            stdout = cp.stdout
            pprint.pprint(stdout)

            try:
                data = stdout.decode('shift-jis')
            except:
                console.error(self.app_name, f'decode failed. : {url_auth}')
                return []
            else:
                #pprint.pprint(data)
                data_list = re.split(r'\n', data)
                file_list = self.__doGetFileList(data_list)
                return file_list

    def __doGetFileList(self, data_list):
        file_list = []
        i = 0
        while i < len(data_list):
            check_M = re.search(r'M\s{7}', data_list[i])

            if not check_M is None:
                item_path = re.sub(r'M\s{7}', '', data_list[i])
                """
                check_asset_item = self.fc.checkAssetFile(self.fc.creanPath(item_path))
                if check_asset_item == False:
                    i += 1
                    continue
                """

                data_item = re.sub(r'\\', '/', data_list[i])
                reg_env_path = re.sub(r'\\', '/', self.envPath)
                regExpData = r'M\s{7}' + reg_env_path + r'|\s'
                regExp = re.compile(regExpData)

                relative_path = re.sub(regExpData, '', data_item)
                file_path = re.sub(r'\\', '/', relative_path)
                file_list.append(file_path)

            i += 1
        return file_list

    def __getCacheList(self, file_list):
        result = []
        for file_item in file_list:

            isAsset = self.fc.checkAssetFile(file_item)
            if isAsset == True:

                isSrc = re.search(r'/src/', file_item)
                if isSrc is None:
                    result.append(file_item)
        return result

    def __getAllUpdataHTMLList(self, file_list):
        #pprint.pprint(file_list)
        result = []
        dir = DEVELOPMENT_ENVIRONMENT + '/' + self.env
        for file_item in file_list:
            isWiro = re.search(r'wiro_localcode.inc|wiro_content.inc', file_item)
            isHTML = re.search(r'\.html', file_item)
            if not isWiro is None:
                wiro_localcode = re.sub(r'wiro_localcode.inc|wiro_content.inc', 'wiro_localcode.inc', file_item)
                wiro_content = re.sub(r'wiro_localcode.inc|wiro_content.inc', 'wiro_content.inc', file_item)
                result.append(self.fc.creanPath(dir + wiro_localcode))
                result.append(self.fc.creanPath(dir + wiro_content))
            elif not isHTML is None:
                result.append(self.fc.creanPath(dir + file_item))
        return result

    def getSVNCacheData(self):
        self.ct.start(processe_name='do svn command', msg='SVNコミット情報取得開始。')

        cmd = self.__setSVNCommand()
        console.log(self.app_name, f'コマンドを実行。do command "{cmd}"')
        svn_updata_list = self.__doCheckSvn(cmd)

        data = {
            'cache_list': self.__getCacheList(svn_updata_list),
            'all_cache_html_list': self.__getAllUpdataHTMLList(svn_updata_list)
        }

        self.ct.finish(processe_name='do svn command', msg='SVNコミット情報取得終了。')
        return data


class FileListMaker():
    def __init__(self, env):
        self.app_name = __class__.__name__
        self.env = env

        self.file_list = []
        self.file_list_glob = []

        self.ct = CountTimer()
        self.fc = FileController()
        return

    def __getFileList(self, path):
        for item in os.listdir(path):
            item_path = self.fc.creanPath(path + '/' + item)
            check_file = os.path.isfile(item_path)

            if check_file == True:
                check_text = self.fc.checkTextFile(item_path)

                if check_text == True:
                    self.file_list.append(item_path)
        return

    def walkTreeToGetCodeFileList(self):
        dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env)
        processe_name = f'get directory tree data: [ {dir} ]'
        self.ct.start(processe_name=processe_name, msg='全ファイルリスト取得開始。')

        for curDir, dirs, files in os.walk(dir):
            check_ignore = re.search(r'node_modules|\.git|\.svn', curDir)
            #check_ignore = re.search(r'node_modules|\.git|\.svn|', curDir)

            if check_ignore is None:
                self.__getFileList(curDir)

        self.ct.finish(processe_name=processe_name, msg='全ファイルリスト取得終了。')
        return self.file_list

    def getGlob(self):
        dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env) + "\**\*"
        glob_list = glob.glob(dir, recursive=True)

        for glob_item in glob_list:
            check_ignore = re.search(r'node_modules|\.git|\.svn', glob_item)

            if check_ignore is None:
                item_path = self.fc.creanPath(glob_item)
                check_file = os.path.isfile(item_path)

                if check_file == True:
                    check_text = self.fc.checkTextFile(item_path)

                    if check_text == True:
                        self.file_list_glob.append(item_path)
        return self.file_list_glob

    def __getFixList(self, file_path):
        check_ignore = re.search(r'node_modules|\.git|\.svn', file_path)
        #check_ignore = re.search(r'node_modules|\.git|\.svn|', file_path)
        if check_ignore is None:
            fix_path = re.sub(r'\r', '', file_path)
            result_path = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '\\' + self.env + '\\' + fix_path)
            return result_path
        return None

    def doPowershell(self):
        dir = self.fc.creanPath(DEVELOPMENT_ENVIRONMENT + '/' + self.env)
        power_commond = "Get-ChildItem " + dir + " -Recurse -Name -Include *.inc, *.php, *.txt, *.html, *.json, *.jsonp, *.js, *.jsx, *.ts, *.tsx, *.vue, *.csv, *.css, *.sass, *.scss"
        cmd = 'powershell -Command' + ' ' + power_commond
        processe_name = f'get directory tree data: \ncommand[ {cmd} ]'
        self.ct.start(processe_name=processe_name, msg='全ファイルリスト取得開始。')
        try:
            cp = subprocess.run(cmd, capture_output=True)
        except:
            console.error(self.app_name, f'Windows PowerShellコマンド失敗。command failed. : {cmd}')
            return ['error']
        else:
            stdout = cp.stdout

            try:
                data = stdout.decode('shift-jis')
            except:
                console.error(self.app_name, f'decode failed. : {cmd}')
                return ['error']
            else:
                data_list = re.split(r'\n', data)
                fix_list = [self.__getFixList(i) for i in data_list]
                file_list = list(filter(None, fix_list))
                self.ct.finish(processe_name=processe_name, msg='全ファイルリスト取得終了。')
                return file_list


class CacheDataCreater():
    def __init__(self, env):
        self.app_name = __class__.__name__
        self.env = env

        self.target_file_list = []
        self.upData_file_list = []

        self.ct = CountTimer()
        self.ms = Message()
        self.fc = FileController()
        self.flm = FileListMaker(env)
        return

    def __grepCheckCacheFile(self, code_file, cache_list):
        is_text = self.fc.checkTextFile(code_file)
        if is_text == False:
            return

        data = self.fc.readingOneline(code_file)
        for cache_item in cache_list:
            check = re.search(cache_item, data)
            if not check is None:
                return True
        return False

    def __wrapGrepCheckCacheFile(self, args):
        code_file = args[0]
        cache_list = args[1]
        check = self.__grepCheckCacheFile(code_file, cache_list)

        if check == True:
            return code_file
        return None

    def __grep(self, cache_list, code_files):
        processe_name = 'Grep'
        #self.ct.start(processe_name=processe_name, msg='グレップ開始。')
        console.log(self.app_name, f'グレップファイル数。Number 0f Greping files: {len(code_files)}')

        files = []

        args = [[i, cache_list] for i in code_files]

        #pool = Pool(processes=4)
        #files = pool.map(self.__wrapGrepCheckCacheFile, args)
        files = map(self.__wrapGrepCheckCacheFile, args)

        files_filtered = filter(None, files)
        result = list(files_filtered)

        #self.ct.finish(processe_name=processe_name, msg='グレップ終了。')
        return result

    def __checkHTMLFile(self, path):
        data = os.path.splitext(path)
        extends = re.sub(r'\.|\s', '', data[1])
        #print(extends)
        if extends == 'inc' \
            or extends == 'php' \
            or extends == 'html':
                return True
        return False

    def __getFileData(self, cache_list, code_files):
        add_cache_list = []
        exist_asset_flag = True

        #グレップ
        updata_code_files = self.__grep(cache_list, code_files)

        for code_file in updata_code_files:
            # バックスラッシュ書式の相対パスに変更
            dir = DEVELOPMENT_ENVIRONMENT + '\\' + self.env
            dir_p = re.sub(r'\\', '/', dir)
            dir_s = re.sub(r'\/\/', '/', dir_p)
            regExp = re.compile(dir_s)
            file_p = re.sub(r'\\', '/', code_file)
            dir_path = re.sub(regExp, '', file_p)

            # HTML系ファイルか確認
            check_html = self.__checkHTMLFile(dir_path)
            if check_html == False:
                add_cache_list.append(dir_path)

        self.target_file_list = list(set(self.target_file_list + cache_list))
        self.upData_file_list = list(set(self.upData_file_list + updata_code_files))

        if len(add_cache_list) > 0:
            #まだアセットリソースファイルがある場合、それの読み込みファイルを再グレップ
            self.__getFileData(add_cache_list, code_files)
        return

    def getCacheFileListData(self, cache_list):
        #code_files = self.flm.walkTreeToGetCodeFileList()

        code_files = self.flm.doPowershell()
        if code_files[0] == 'error' or len(code_files) < 1:
            code_files = self.flm.walkTreeToGetCodeFileList()

        self.__getFileData(cache_list, code_files)

        data = {
            'target_file_list': self.target_file_list,
            'upData_file_list': self.upData_file_list
        }
        self.ms.showList('キャッシュ更新が必要なアセットリソースファイル一覧', data['target_file_list'])
        self.ms.showList('キャッシュ更新をするソースコードファイル一覧', data['upData_file_list'])
        return data


class CodeWriter():
    def __init__(self, param):
        self.app_name = __class__.__name__
        self.param = param
        self.fc = FileController()
        self.hearinger = Hearing()
        return

    def __reWrite(self, upData_file, target_file_list):
        new_data = []

        data = self.fc.reading(upData_file)
        for line in data:
            new_line = line

            for target in target_file_list:
                check_target_line = re.search(target, line)

                if not check_target_line is None:
                    new_cache = target + '?' + self.param

                    regExpData = target + r'\?(\w|\-|\_)+'
                    RegExp = re.compile(regExpData)
                    check_hasCache = re.search(RegExp, line)

                    if check_hasCache is None:
                        new_line = re.sub(target, new_cache, line)
                    else:
                        new_line = re.sub(RegExp, new_cache, line)

            new_data.append(new_line)
        self.fc.writing(new_data, upData_file)
        return

    def __rewriteAllAssetCode(self, upData_file):
        new_data = []

        data = self.fc.reading(upData_file)
        for line in data:
            new_line = line

            isline = re.search(r'/((\w|\-|\_)+/)+(\w|\-|\_)+\.\w+(\?(\w|\-|\_)+)?', line)
            if not isline is None:
                isline.group()
                new_code = re.search(r'/((\w|\-|\_)+/)+(\w|\-|\_)+\.\w+', line).group() + '?' + self.param
                new_line = re.sub(r'/((\w|\-|\_)+/)+(\w|\-|\_)+\.\w+(\?(\w|\-|\_)+)?', new_code, line)

            new_data.append(new_line)
        self.fc.writing(new_data, upData_file)
        return

    def upDateChahe(self, cache_data, mode="normal"):
        check_continuance = self.hearinger.select('HTMLのキャッシュ更新続けますか？ ', ['y', 'n', 'yes', 'no'], blank_ok=False)
        if check_continuance == 'n' or check_continuance == 'no':
            console.log(self.app_name, 'HTMLのキャッシュ更新をキャンセルしました。HTML cache updates are canceled.')
            return False

        target_file_list = cache_data['target_file_list']
        upData_file_list = cache_data['upData_file_list']

        console.log(self.app_name,f'キャッシュ更新開始。Start updata caches. [mode={mode}]')
        for upData_file in upData_file_list:
            if mode == 'all':
                self.__rewriteAllAssetCode(upData_file)
            else:
                self.__reWrite(upData_file, target_file_list)
        console.log(self.app_name,f'キャッシュ更新完了。Finish updata caches. [mode={mode}]')
        return True


class Cache():
    def __init__(self, env, param):
        self.app_name = __class__.__name__
        self.env = env
        self.param = param

        self.hearinger = Hearing()
        self.csvn = CacheSVN(env)
        self.cdc = CacheDataCreater(env)
        self.cw = CodeWriter(param)
        self.ct = CountTimer()

        print('')
        console.log(self.app_name, f'(Init) development environment : {self.env}')
        console.log(self.app_name, f'(Init) Update Cache Parameters : {self.param}')
        print('')
        return

    def __remindUserTocheckForDifferences(self):
        hearinger = Hearing()
        print('\n必ずコミット前に必ず上記ファイル（↑ updata file list）の差分を確認してください。')
        answer = hearinger.select('Please answer ==> ', ['y', 'yes'])
        console.log(self.app_name, f'Confirm recognition of differences before updating SVN. : {answer}')
        return

    def doCache(self, data):
        # 計測開始
        print('')
        self.ct.start(processe_name='doCache', msg='メイン処理開始。')

        cache_list = data['cache_list']
        all_cache_html_list = data['all_cache_html_list']

        if len(cache_list) < 1 and len(all_cache_html_list) < 1:
            print('')
            console.log(self.app_name, 'No cache target.')
            answer = self.hearinger.select('\n終了しますか？ ', ['y', 'n', 'yes', 'no'], blank_ok=True)
            return

        # キャッシュデータ取得
        cache_data = self.cdc.getCacheFileListData(cache_list)

        # 計測終了
        self.ct.finish(processe_name='doCache', msg='メイン処理終了。')

        # キャッシュ更新
        check_done = self.cw.upDateChahe(cache_data)

        # 更新確認
        if check_done == True:
            self.__remindUserTocheckForDifferences()

        print('')
        console.log(self.app_name, 'end')
        return

    async def start(self):
        # アセットリソースファイル一覧 取得
        svn_data = self.csvn.getSVNCacheData()

        self.doCache(svn_data)
        return


class CacheBacklog(BacklogApi):
    def __init__(self, comment_url, param):
        super().__init__(comment_url)
        self.app_name = __class__.__name__
        self.stop = False

        self.cache_target_list = self.getCacheList()
        env = self.getUpDatedEnv()

        if env == None:
            console.error(self.app_name, f'(Init) miss getting Enviroment from Backlog. {comment_url}')
            self.stop = True
            return

        print()
        console.log(self.app_name, f'(Init) from Backlog.')
        self.cc = Cache(env, param)
        return

    async def start(self):
        if self.stop == True:
            return

        data = {
            'cache_list': self.cache_target_list,
            'all_cache_html_list': []
        }
        self.cc.doCache(data)

        return
