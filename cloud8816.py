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

enumdate = {
    "today"     : 1,
    "yestarday" : 2,
    "last7"     : 3,
    "last30"    : 4,
    "thismonth" : 5,
    "lastmonth" : 6
}

enumoption = {
    "sum"         : 2,
    "allmovement" : 3,
    "trend"       : 4,
    "cashflow"    : 5,
    "products"    : 8,
    "aliquota"    : 7
}

class cloud8816:

    def __init__(self, host, username, password):
        self.username = username
        self.password = password
        self.hostname = host
    
        self.driver = webdriver.Chrome()

        self.login()
    
    def login(self):

        self.driver.get(self.hostname)
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "loginPanel")))
            username = self.driver.find_element(By.XPATH, "//*[@placeholder='Username']")
            username.send_keys(self.username)
            password = self.driver.find_element(By.XPATH, "//*[@placeholder='Password']")
            password.send_keys(self.password)
            login = self.driver.find_element(By.XPATH, "//*[@ng-click='executeLogin()']")
            login.click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "connection-signal")))
            # I need to improve this
            time.sleep(4)
        except:
            print('Failed to Login')
  

    def getstat(self, selectopt: enumoption, selectdate: enumdate):

        #select All
        selectall = self.driver.find_element(By.XPATH, "//*[@ng-click='toggleCheckAllDevices(true)']")
        selectall.click()
        #view statistics
        statistic = self.driver.find_element(By.XPATH, "//*[@ng-click='viewFilteredStatistics()']")
        statistic.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "form-group")))
        
        # I need to improve this
        time.sleep(2)

        #select Summary
        xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[2]/div/ul/li[{}]".format(enumoption[selectopt])
        stat = self.driver.find_element(By.XPATH, xpath)
        stat.click()

        # I need to improve this
        time.sleep(1)

        #select date
        xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[3]/div/form/div/input"
        date = self.driver.find_element(By.XPATH, xpath)
        date.click()
        #today
        #today = self.driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/ul/li[1]")
        #today.click()
        #yestarday
        xpath = "/html/body/div[2]/div[1]/ul/li[{}]".format(enumdate[selectdate])
        today = self.driver.find_element(By.XPATH, xpath)
        today.click()              
        # View datas
        xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[3]/div/form/button[1]"
        show = self.driver.find_element(By.XPATH, xpath)
        show.click()

        xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[4]/ng-include/div/div[1]/div/table/tbody/tr[1]"
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        if selectopt == 'sum':
            htmltable = soup.find('table', { 'class' : 'table table-striped' })
            return self.handlesum(htmltable)
        elif selectopt == 'products':
            # order data
            xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[4]/ng-include/div/div/div[1]/table/thead/tr[2]/th[1]"
            order = self.driver.find_element(By.XPATH, xpath)
            order.click()
            htmltable = soup.find('table', { 'class' : 'table table-bordered table-striped table-hover' })
            return self.handleproducts(htmltable)

    @staticmethod
    def handlesum(self, htmltable):
        headers = []
        rows = []
        for i, row in enumerate(htmltable.find_all('tr')):
            if i == 1:
                headers = [el.text.strip() for el in row.find_all('th')]
            elif i == 2 or i == 3:
                #print([el.text.strip() for el in row.find_all('td')])
                rows.append([el.text.strip() for el in row.find_all('td')])
#        print(headers)
#        print(rows)
        sumstat = {}
        for i, header in enumerate(headers):
            mergeval = []
            for idx in range(len(rows)):
                mergeval.append(rows[idx][i])
            sumstat[header]=mergeval
        
        return sumstat
    

    @staticmethod
    def handleproducts(self, htmltable):

        headers = []
        rows = []
        for i, row in enumerate(htmltable.find_all('tr')):
            if i == 1:
                headers = [el.text.strip() for el in row.find_all('th')]
            elif i == 2 or i == 3:
                #print([el.text.strip() for el in row.find_all('td')])
                rows.append([el.text.strip() for el in row.find_all('td')])

        return None
    
    def close(self):
        self.driver.close()


if __name__ == '__main__':
     
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
    user = conf['cloud8816']['user']
    passwd = conf['cloud8816']['pass']
    hostname = conf['cloud8816']['hostname']
    conn = cloud8816(host=hostname, username=user, password=passwd)
    statsum = conn.getstat('products','today')
    print(statsum)
    conn.close()
