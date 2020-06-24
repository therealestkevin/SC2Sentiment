from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
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



profile = webdriver.FirefoxProfile()

profile.set_preference("browser.download.dir", 'H:/Code/SC2Sentiment/TempReplays')
profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/octet-stream')

browser = webdriver.Firefox(firefox_profile=profile)

browser.get("https://gggreplays.com/matches#?map_name=Acid%20Plant%20LE&page=1")

print(browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[2]/td[6]').text)

#WebDriverWait(browser, 1000).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[2]'))).click()


curElement = browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[2]')
actions = ActionChains(browser)
actions.move_to_element(curElement)
actions.click(curElement)

actions.perform()


#browser.find_element_by_xpath('//*[@id="matches"]/div[3]/div[3]/table/tbody/tr[2]')

button = WebDriverWait(browser,3).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div[5]/div[1]/div[1]/div[3]/a/span')))
button.click()

print(MyClass.getDownLoadedFileName(3, browser))




