#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging,time,re,requests,mimetypes
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class PlayBooks:
  def __init__(self,driver=None):
    self.logger = logging.getLogger('Play Books')
    self.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    fh = logging.FileHandler("playbooks.log",mode="a")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    self.logger.addHandler(ch)
    self.logger.addHandler(fh)


    self.logger.info("Initialize..")
    self.profile = webdriver.FirefoxProfile()
    self.driver = webdriver.PhantomJS(
      desired_capabilities={
        'phantomjs.page.settings.userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
      },
      service_args=['--ssl-protocol=tlsv1'],
    )
    if driver == "chrome":
      self.driver = webdriver.Chrome()


  def list(self,url):
    self.logger.info("Getting Images List..")
    self.driver.get(url)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'[id=":0.reader"]'))
    )
    iframe = self.driver.find_element_by_css_selector('[id=":0.reader"]')
    self.driver.switch_to_frame(iframe)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'body[class]'))
    )

    for i in range(0,100):
      actions = webdriver.ActionChains(self.driver)
      actions.send_keys(u'\ue012')
      actions.perform()
      time.sleep(0.1)

    document = BeautifulSoup(self.driver.page_source,"lxml")

    self.title = document.select("body > div > div > table td > span > span")[0].get_text()

    for img in document.select("img"):
      yield re.sub('&w=[0-9]*','',img.get("src"))

  def save(self,imgurl):
    n = self.title+"_"+re.search('pg=[^&]*',imgurl).group(0).replace("pg=","")
    ext = ".jpg"
    print(imgurl)
    r = requests.get(imgurl)
    ext = mimetypes.guess_extension(r.headers["content-type"], strict=False)
    with Path(n+ext).open("wb") as f:
      f.write(r.content)

p = PlayBooks(driver="chrome")
url = 'https://play.google.com/books/reader?id=j4eoDAAAQBAJ&printsec=frontcover&output=reader&hl=ja'
for imgurl in p.list(url):
  p.save(imgurl)

