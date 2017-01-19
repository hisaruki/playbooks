#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging,time,re,requests,mimetypes,argparse,os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class PlayBooks:
  def __init__(self):
    self.logger = logging.getLogger('Play Books')
    self.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    #fh = logging.FileHandler("playbooks.log",mode="a")
    #fh.setLevel(logging.INFO)
    #fh.setFormatter(formatter)
    self.logger.addHandler(ch)
    #self.logger.addHandler(fh)
    self.logger.debug("Initialize..")

  def login(self):
    self.logger.debug("Logging in...")
    self.driver.get('https://accounts.google.com/')
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'#Email'))
    )

    self.driver.find_elements_by_css_selector('#Email')[0].send_keys(input("username:"))
    self.driver.find_elements_by_css_selector('#next')[0].send_keys('\n')
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'#Passwd'))
    )
    self.driver.find_elements_by_css_selector('#Passwd')[0].send_keys(input("password:"))
    self.driver.find_elements_by_css_selector('#signIn')[0].send_keys('\n')
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'body'))
    )

  def boot(self,driver="PhantomJS"):
    if driver == "Chrome":
      self.driver = webdriver.Chrome()
    if driver == "PhantomJS":
      self.driver = webdriver.PhantomJS(
        desired_capabilities={
          'phantomjs.page.settings.userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        },
        service_args=['--ssl-protocol=tlsv1'],
        service_log_path=os.path.devnull
      )

  def list(self,url):
    self.logger.debug("Getting Images List...")
    self.driver.get(url)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'[id=":0.reader"]'))
    )
    iframe = self.driver.find_element_by_css_selector('[id=":0.reader"]')
    self.driver.switch_to_frame(iframe)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'body[class]'))
    )

    result = []

    def page(key):
      document = BeautifulSoup(self.driver.page_source,"lxml")
      b = document.select("body > div > div > table td > div > div > div")[-1]
      for img in document.select("img"):
        img = re.sub('&w=[0-9]*','',img.get("src"))
        if not img in result:
          result.append(img)
      self.logger.debug({
        u'\ue00e':"Pageup.",
        u'\ue00f':"Pagedown."
      }[key])
      actions = webdriver.ActionChains(self.driver)
      actions.send_keys(key)
      actions.perform()
      time.sleep(0.1)
      document = BeautifulSoup(self.driver.page_source,"lxml")
      a = document.select("body > div > div > table td > div > div > div")[-1]
      for img in document.select("img"):
        img = re.sub('&w=[0-9]*','',img.get("src"))
        if not img in result:
          result.append(img)
      return int(b == a)

    time.sleep(2)

    document = BeautifulSoup(self.driver.page_source,"lxml")
    self.title = document.select("body > div > div > table td > span > span")[0].get_text()
    up = u'\ue00e'
    down = u'\ue00f'

    uperr = 0
    downerr = 0

    while uperr < 5:
      uperr += page(up)

    while downerr < 10:
      downerr += page(down)
    self.driver.quit()

    return list(set(result))

  def save(self,imgurl):
    try:
      Path(self.title).mkdir()
    except:
      ""
    n = self.title+"/"+re.search('pg=[^&]*',imgurl).group(0).replace("pg=","")
    ext = ".jpg"
    self.logger.info(imgurl)
    r = requests.get(imgurl)
    ext = mimetypes.guess_extension(r.headers["content-type"], strict=False)
    if ext == ".jpe" or ext == ".jpeg":
      ext = ".jpg"
    with Path(n+ext).open("wb") as f:
      f.write(r.content)

parser = argparse.ArgumentParser(description="playbooks")
parser.add_argument("url")
parser.add_argument("--driver",default="PhantomJS")
args = parser.parse_args()

p = PlayBooks()
p.boot(args.driver)
#if args.login:p.login()
url = args.url
for imgurl in p.list(url):
  p.save(imgurl)

