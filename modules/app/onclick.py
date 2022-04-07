import pandas as pd
import numpy as np
import re
import os
import math
import pprint
from bs4 import BeautifulSoup

from modules.common.file_controller import FileController

class Onclick:
    def __init__(self, html_full_path):
        self.csv = '/onclick-part/onclick.csv'
        self.fc = FileController()
        self.html = self.fc.creanPath(html_full_path)
        self.csv_data = self.readCsv()
        return

    def readCsv(self):
        current_dir = os.getcwd()
        mycsv = self.fc.creanPath(current_dir + self.csv)
        print(mycsv)
        csv_data = pd.read_csv(mycsv)
        return csv_data

    def upDateHTML(self):
        html_data = self.fc.reading(self.html)

        new_html_data = []

        for line in html_data:
            new_line = self.reWriteLine(line)
            new_html_data.append(new_line)
        return

    def reWriteLine(self, line):
        self.checkReWriteLine(line)
        return

    def getOnclickData(self, data):
        onclick_data = ''
        return onclick_data

    def checkReWriteLine(self, line):
        i = 0
        while i < len(self.csv_data):
            tag = self.csv_data.loc[i,"tag"]
            className = self.csv_data.loc[i,"class"] if not pd.isna(self.csv_data.loc[i,"class"]) else ''
            csv_href = self.csv_data.loc[i,"href"] if not pd.isna(self.csv_data.loc[i,"href"]) else ''

            if className == '' and csv_href == '':
                i += 1
                continue

            href = re.sub(r'https://www.softbank.jp', '', csv_href)
            prefix = r'<' + tag + r'\s?'
            classRegExp = r'class=\"(' + className + r'|(\w|\_|\-|\s)+)' + '\"'
            hrefRegExp = r'href=\"' + href + '\"' if href else r''
            regExpData = prefix + r'(' + classRegExp + r')?\s?(' + hrefRegExp + r')?'
            print(regExpData)
            RegExp = re.compile(regExpData)
            #pprint.pprint(RegExp)
            check = re.search(RegExp, line)

            if not check is None:
                print('none')
                #print(line)
                return
            i += 1
        return False

    def test(self):
        html_data = self.fc.readingOneline(self.html)
        soup = BeautifulSoup(html_data, 'html.parser')
        pprint.pprint(soup)
        #print(html_data)
        self.checkReWriteLine(html_data)
        return

    def start(self):
        #self.upDateHTML()
        self.test()

