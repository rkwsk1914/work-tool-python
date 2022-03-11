import chromedriver_binary
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW


class Scraping:
    def __init__(self):
        print('')
        print(f'Now starting chromedriver ...')
        self.driver_sp = self.initiPhone()
        self.driver_pc = self.initPC()
        print('')
        print(f'chromedriver start')

    def initiPhone(self):
        service = Service()
        service.creationflags = CREATE_NO_WINDOW
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=320,768")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-logging --v=1")
        options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1')
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def initPC(self):
        service = Service()
        service.creationflags = CREATE_NO_WINDOW
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1400,768")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-logging --v=1")
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def getPageDataVerSP(self, url):
        self.driver_sp.get(url)
        data = self.driver_sp.page_source
        return data

    def getPageDataVerPC(self, url):
        self.driver_sp.get(url)
        data = self.driver_pc.page_source
        return data

    def close(self):
        self.driver_sp.close()
        self.driver_pc.close()
        print('')
        print(f'chromedriver close')
        return