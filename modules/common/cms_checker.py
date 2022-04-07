import re

from modules.config.db import CMSLSIT

class CMSchecker:
    def __init__(self, cms_type):
        self.cms_type = cms_type
        return

    def checkCategory(self, page_path):
        check_wiro2 = re.search(r'/ybb/|/internet/', page_path)
        check_corp = re.search(r'/corp/|/disaster/', page_path)

        if not check_wiro2 is None:
            return CMSLSIT['WIRO']['internet']
        elif not check_wiro2 is None:
            CMSLSIT['WIRO']
            return CMSLSIT['WIRO']['COPR']
        else:
            return CMSLSIT['WIRO']['WIRO']

    def checkCMSType(self):
        check_sitecore = re.search(r'Sitecore', self.cms_type)
        check_wiro = re.search(r'WIRO', self.cms_type)

        if not check_sitecore is None:
            return 'Sitecore'
        elif not check_wiro is None:
            return 'WIRO'
        else:
            return 'undifend'

    def setCMSdata(self, page_path):
        check_sitecore = re.search(r'Sitecore', self.cms_type)
        check_wiro = re.search(r'WIRO', self.cms_type)

        if not check_sitecore is None:
            return CMSLSIT[self.cms_type]
        elif not check_wiro is None:
            return self.checkCategory(page_path)
        else:
            return 'undifend'

    def checkLang(self, page_path):
        check_english = re.search(r'/en/', page_path)

        if not check_english is None:
            return 'en'
        else:
            return 'ja'
