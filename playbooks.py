#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging,time,re,requests,mimetypes,argparse,os,urllib,base64
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
    self.logger.addHandler(ch)
    #fh = logging.FileHandler("playbooks.log",mode="a")
    #fh.setLevel(logging.INFO)
    #fh.setFormatter(formatter)
    #self.logger.addHandler(fh)
    self.logger.debug("Initialize..")
    self.images = {}

  def login(self,username,password):
    self.logger.debug("Logging in...")
    self.driver.get('https://accounts.google.com/')
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'#Email'))
    )
    while not username:
      username = input("username:")
    self.driver.find_elements_by_css_selector('#Email')[0].send_keys(username)
    self.driver.find_elements_by_css_selector('#next')[0].send_keys('\n')
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'#Passwd'))
    )
    while not password:
      password = input("password:")
    self.driver.find_elements_by_css_selector('#Passwd')[0].send_keys(password)
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

  def fetch(self,url):
    self.logger.debug("Getting Images...")
    self.driver.get(url)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'[id=":0.reader"]'))
    )
    iframe = self.driver.find_element_by_css_selector('[id=":0.reader"]')
    self.driver.switch_to_frame(iframe)
    WebDriverWait(self.driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR,'body[class]'))
    )

    time.sleep(2)
    document = BeautifulSoup(self.driver.page_source,"lxml")
    self.title = document.select("body > div > div > table td > span > span")[0].get_text()
    try:
      Path(self.title).mkdir()
    except:
      ""

    def page(key):
      document = BeautifulSoup(self.driver.page_source,"lxml")
      b = document.select("body > div > div > table td > div > div > div")[-1]
      images = self.driver.execute_script('''
function ImageToBase64(img,mimetype) {
  var canvas = document.createElement('canvas');
  canvas.width  = img.width;
  canvas.height = img.height;
  var ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0);
  return canvas.toDataURL(mimetype);
}
var images = [];
document.querySelectorAll("img").forEach(function(img){
  img.src = img.src.replace(/&w=.*/,"")
  try{
    var b64 = ImageToBase64(img,"image/jpeg");
    images.push([img.src,b64,".jpg"]);
  }catch(e){}
  try{
    var b64 = ImageToBase64(img,"image/png");
    images.push([img.src,b64,".png"]);
  }catch(e){}
});
return images;
      ''');
      for image in images:
        url,b64,ext = image[0],image[1],image[2]
        b64 = re.sub(r'data:[^,]*,','',b64)
        if len(b64) and not url in self.images:
          self.images[url] = b64,ext
        if url in self.images and len(b64) > len(self.images[url][0]):
          self.images[url] = b64,ext
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
      return int(b == a)

    up = u'\ue00e'
    down = u'\ue00f'
    uperr = 0
    downerr = 0
    while uperr < 5:
      uperr += page(up)
    while downerr < 5:
      downerr += page(down)
    self.driver.quit()

  def save(self):
    for url in self.images:
      b64 = self.images[url][0]
      ext = self.images[url][1]
      qs = urllib.parse.parse_qs(url)
      if "pg" in qs:
        pg = qs["pg"][0]
        with (Path(self.title) / Path(pg+ext)).open("wb") as f:
          f.write(base64.b64decode(b64))

parser = argparse.ArgumentParser(description="playbooks")
parser.add_argument("url")
parser.add_argument("--login",action="store_true")
parser.add_argument("-u","--username",default=None)
parser.add_argument("-p","--password",default=None)
args = parser.parse_args()

p = PlayBooks()
p.boot(driver="Chrome")
if args.login:p.login(args.username,args.password)
url = args.url
p.fetch(url)
p.save()