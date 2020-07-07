from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os
import time

class MyClass:
  @staticmethod
  def getDownLoadedFileName(waitTime, driver):
    driver.execute_script("window.open()")
    WebDriverWait(driver, 10).until(EC.new_window_is_opened)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:downloads")

    endTime = time.time() + waitTime
    while True:
      try:
        fileName = driver.execute_script(
          "return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value")
        if fileName:
          return fileName
      except:
        pass
      time.sleep(1)
      if time.time() > endTime:
        break

options = Options()
#options.headless = True

profile = webdriver.FirefoxProfile()

profile.set_preference("browser.download.dir", 'H:/Code/SC2Sentiment/TempReplays')
profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/octet-stream')

browser = webdriver.Firefox(options=options, firefox_profile=profile)

browser.get("https://gggreplays.com/matches#?map_name=Acid%20Plant%20LE&page=1")

print(browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[2]/td[6]').text)

matchLink = browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[2]/td[2]/a').get_attribute('href')

browser.get(matchLink)

before = os.listdir('H:/Downloads')

downURL = browser.current_url+"/replay"

browser.get(downURL)


after = os.listdir('H:/Downloads')

#print(MyClass.getDownLoadedFileName(3, browser))
change = set(after) - set(before)
file_name = change.pop()
print(file_name)

browser.close()



