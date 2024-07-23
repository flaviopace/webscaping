import os
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

JSON_FILE = 'config.json'


def demo(url):
    driver = webdriver.Chrome()
    driver.get(url)
  
    #username = driver.find_element((By.XPATH, "//*/select[@ng-model='login.username']"))

    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginPanel")))
        username = driver.find_element(By.XPATH, "//*[@placeholder='Username']")
        password = driver.find_element(By.XPATH, "//*[@placeholder='Password']")
    finally:
        driver.quit()
  
    print(username)

    driver.close()


if __name__ == '__main__':
     
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
    demo(conf['cloud8816']['hostname'])
