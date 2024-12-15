import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Update
from telegram import constants as botconst
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup
import datetime


JSON_FILE = 'config.json'

telegramcmd = {
    "oggi" : "today" ,
    "ieri" : "yestarday",
    "ultimi7gg" : "last7",
    "ultimi30gg" : "last30",
}

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

ch_id = ''

def getCloud8816Credentials():
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
        conf = json.load(in_file)
    user = conf['cloud8816']['user']
    passwd = conf['cloud8816']['pass']
    hostname = conf['cloud8816']['hostname']

    return user, passwd, hostname

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
            # I need to improve this
            time.sleep(1)
            password = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/input")
            password.send_keys(self.password)
            login = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[2]/div/div/div[3]/div/button")
            login.click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "connection-signal")))
            # I need to improve this
            time.sleep(4)
        except Exception as e:
            print('Failed to Login {}'.format(e))
  
    def gotostat(self):
         #select All
        selectall = self.driver.find_element(By.XPATH, "//*[@ng-click='toggleCheckAllDevices(true)']")
        selectall.click()
        #view statistics
        statistic = self.driver.find_element(By.XPATH, "//*[@ng-click='viewFilteredStatistics()']")
        statistic.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "form-group")))
        
        # I need to improve this
        time.sleep(2)


    def getstat(self, selectopt: enumoption, selectdate: enumdate):

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
        
        if selectopt == 'sum':
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            htmltable = soup.find('table', { 'class' : 'table table-striped' })
            return self.handlesum(html=htmltable)
        elif selectopt == 'products':
            # order data
            xpath = "/html/body/div[1]/div/div/div/div/div[2]/div[4]/ng-include/div/div/div[1]/table/thead/tr[2]/th[1]"
            order = self.driver.find_element(By.XPATH, xpath)
            order.click()
            # I need to improve this
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            htmltable = soup.find('table', { 'class' : 'table table-bordered table-striped table-hover' })
            htmltable = htmltable.tbody
            return self.handleproducts(html=htmltable)

    @staticmethod
    def handlesum(html):
        headers = []
        rows = []
        for i, row in enumerate(html.find_all('tr')):
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
    def handleproducts(html):
        rows = []
        for i, row in enumerate(html.find_all('tr')):
            #skip first lines
            itemtoremove = 8
            items = [el.text.strip() for el in row.find_all('td')]
            del items[-itemtoremove:]
            rows.append(items)
        return rows
    
    def close(self):
        self.driver.close()

def end_of_month(dt):
    todays_month = dt.month
    tomorrows_month = (dt + datetime.timedelta(days=1)).month
    return tomorrows_month != todays_month

def showprintablesum(statsum):
    for key, value in statsum.items():
        if 'device name' in key.lower():
            drink = value[0]
            snack = value[1]
        elif "sold" in key.lower():
            drinktotal = value[0]
            snacktotal = value[1]
    return "{} : totale {} \n{} : totale {}".format(drink, drinktotal, snack, snacktotal) 

def showprintableprod(prodstat):
    displaydata = "Prodotto \t- Quantita \t- Totale\n\n"
    for idx in prodstat:
        displaydata += "{} \t- {} \t- {}\n".format(idx[0], idx[1], idx[2])

    return displaydata 

# Define a few command handlers. These usually take the two arguments update and
# context.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
async def cmdhandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    msginput = update.message.text.replace('/','')
    input = telegramcmd[msginput]
    
    user, passwd, hostname = getCloud8816Credentials()

    await update.message.reply_text("Attendi qualche secondo, sto collezionando la somma degli incassi ...")
    await context.bot.send_message(chat_id=ch_id, text=input)
    conn = cloud8816(host=hostname, username=user, password=passwd)
    conn.gotostat()
    statsum = conn.getstat('sum',input)
    txttodisplay = showprintablesum(statsum)
    await update.message.reply_text("{}".format(txttodisplay))
    await context.bot.send_message(chat_id=ch_id, text=txttodisplay)

    
    await update.message.reply_text("Attendi qualche secondo, sto collezionando i 10 prodotti piu' venduti ...")
    prodsum = conn.getstat('products',input)
    txttodisplay = showprintableprod(prodsum)
    await update.message.reply_text("{}".format(txttodisplay))
    await context.bot.send_message(chat_id=ch_id, text=txttodisplay)

    conn.close()

async def callback_once(context: ContextTypes.DEFAULT_TYPE):

    user, passwd, hostname = getCloud8816Credentials()

    query_list = []
    keys = list(telegramcmd.keys())
    query_list.append(keys[0])    # only today

    now = datetime.datetime.now()
    weekno = now.weekday()

    if end_of_month(now):
        print("is last day of the month")
        query_list.append(keys[3])  # 30 latest day 
    if weekno == 6:
        print("is sunday")
        query_list.append(keys[2])  # 7 latest day
     
    for key in query_list:
        await context.bot.send_message(chat_id=ch_id, text="Sto collezionando i dati per: *{}*".format(key), 
                                       parse_mode=botconst.ParseMode.MARKDOWN_V2)  
     
        option = telegramcmd[key]
        conn = cloud8816(host=hostname, username=user, password=passwd)
        conn.gotostat()
        statsum = conn.getstat('sum', option)
        txttodisplay = showprintablesum(statsum)
        await context.bot.send_message(chat_id=ch_id, text=txttodisplay)  
        await context.bot.send_message(chat_id=ch_id, text="Attendi qualche secondo, sto collezionando i 10 prodotti piu' venduti ...")
        prodsum = conn.getstat('products',option)
        txttodisplay = showprintableprod(prodsum)
        await context.bot.send_message(chat_id=ch_id, text=txttodisplay)
        await context.bot.send_message(chat_id=ch_id, text="___________________")  

class Cloud8816H24Bot:
    def __init__(self, tokenid):
        # Create the Updater and pass it your bot's token.
        self.app = ApplicationBuilder().token(tokenid).build()

        self.app.add_handler(CommandHandler("oggi", cmdhandler))
        self.app.add_handler(CommandHandler("ieri", cmdhandler))
        self.app.add_handler(CommandHandler("ultimi7gg", cmdhandler))

        job_queue = self.app.job_queue
        job_queue.run_once(callback_once, when=5)

        # Start the Bot
        self.app.run_polling()

def testseleniumparser():

    now = datetime.datetime.now()
    weekno = now.weekday()

    if end_of_month(now):
        print("is last")
    if weekno == 6:
        print("is sunday")
        
    user, passwd, hostname = getCloud8816Credentials()
    conn = cloud8816(host=hostname, username=user, password=passwd)
    conn.gotostat()
    statsum = conn.getstat('sum','today')
    print(statsum)
    statsum = conn.getstat('products','today')
    print(statsum)
    conn.close()


if __name__ == '__main__':
     
    with open(os.path.join(sys.path[0], JSON_FILE), 'r') as in_file:
         conf = json.load(in_file)

    tokenid = conf['cloud8816_wowh24_config']['token_id']
    #global ch_id
    ch_id = conf['cloud8816_wowh24_config']['channel_id']
    bot = Cloud8816H24Bot(tokenid)


