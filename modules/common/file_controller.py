import requests
import json
import pprint
import re

import shutil

import os
import zipfile


class FileController:
    # property

    # constructor
    def __init__(self):
        return

    # method
    def creanPath(self, path_text):
        crean_path = re.sub('/', r"\\", path_text)
        return crean_path

    def addWrite(self, line, flie_full_path):
        with open(flie_full_path, 'a') as f:
            print(line, file=f)

    def reading(self, flie_full_path):
        f = open('C:/previewBox/m2-dev.local/kawasaki-lab/asign/index.html','r')
        lines = f.readlines()
        f.close()
        return lines

    def getApi(self):
        #url = 'https://zipcloud.ibsnet.co.jp/api/search'
        url = 'https://sbweb.backlog.jp/api/v2/issues?apiKey=AwsNnM4SiMasJlwLFFoaNpKcU4XZ6bNUUYl10S6G0oblZXSVEUXxa51c61ttPjts'

        #params = {'zipcode':'2330008'}
        params = {}

        res = requests.get(url, params=params)
        data = json.loads(res.text)
        pprint.pprint(data)

    def createZip(self, dir_path):
        #print(f'zip: {dir_path}')
        crean_path = self.creanPath(dir_path)
        shutil.make_archive(crean_path, format='zip', root_dir=crean_path)

        # all path ver
        #zip_path = dir_path + '.zip'
        #zip_name = self.creanPath(re.sub(r'/\\/\.zip|/\.zip', r'\.zip', zip_path))
        #zp = zipfile.ZipFile(zip_name, 'w')

        #for dirname, subdirs, filenames in os.walk(dir_path):
        #    for fname in filenames:
        #        zp.write(fname)

        #zp.close()

    def copy(self, origin, clone):
        origin_dir = os.path.dirname(origin)
        check_origin = os.path.dirname(clone)

        if check_origin == False:
            print(f'Not exsits {origin}')
            return False

        clone_dir = os.path.dirname(clone)
        check = os.path.exists(clone_dir)

        if check == False:
            clone_dir_list = re.split(r'\\', clone_dir)
            clone_dir_path = ''
            #pprint.pprint(clone_dir_list)

            index = 0
            for clone_dir_item in clone_dir_list:
                if index != 0:
                    clone_dir_path = clone_dir_path + r'\\' + clone_dir_item
                else:
                    clone_dir_path = clone_dir_path + clone_dir_item

                #print(clone_dir_path)
                check_clone_dir_path = os.path.exists(clone_dir_path)

                if check_clone_dir_path == False:
                    os.mkdir(self.creanPath(clone_dir_path))

                index = 1

        shutil.copy(origin, clone)
        return True

    def deleate(self, full_path):
        path = self.creanPath(full_path)
        shutil.rmtree(path)
        return

    def empty(self, dir_path):
        path = self.creanPath(dir_path)
        shutil.rmtree(path)
        os.mkdir(path)
        return