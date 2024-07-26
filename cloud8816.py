import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


JSON_FILE = 'config.json'


def demo(url, user, passwd):
    driver = webdriver.Chrome()
    driver.get(url)
  
    #username = driver.find_element((By.XPATH, "//*/select[@ng-model='login.username']"))

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginPanel")))
        username = driver.find_element(By.XPATH, "//*[@placeholder='Username']")
        username.send_keys(user)
        password = driver.find_element(By.XPATH, "//*[@placeholder='Password']")
        password.send_keys(passwd)
        login = driver.find_element(By.XPATH, "//*[@ng-click='executeLogin()']")
        login.click()

    except:
        print('Failed to set Username and Password')
  

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "connection-signal")))
    
    # I need to improve this
    time.sleep(4)

    selectall = driver.find_element(By.XPATH, "//*[@ng-click='toggleCheckAllDevices(true)']")
    selectall.click()

    statistic = driver.find_element(By.XPATH, "//*[@ng-click='viewFilteredStatistics()']")
    statistic.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "form-group")))
    
    # I need to improve this
    time.sleep(2)

    stat = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div[2]/div/ul/li[2]")
    stat.click()

    # I need to improve this
    time.sleep(1)

    show = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div[3]/div/form/button[1]")
    show.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div[4]/ng-include/div/div[1]/div/table")))

    soup = BeautifulSoup(driver.page_source)
    htmltable = soup.find('table', { 'class' : 'table table-striped' })
    
    headers = []
    rows = []
    for i, row in enumerate(htmltable.find_all('tr')):
        if i == 0:
            headers = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])

    print(headers)

    for row in rows:
        print(row)

    driver.close()


if __name__ == '__main__':
     
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
    demo(conf['cloud8816']['hostname'], conf['cloud8816']['user'], conf['cloud8816']['pass'])
