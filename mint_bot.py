#import required libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import gspread as gc
import csv
import random
import glob
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pygsheets
import datetime

class mintbot:

    def __init__(self, username, password):
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.driver = webdriver.Chrome(executable_path='/Users/paul.brown/Documents/Python/chromedriver')
        self.username = username
        self.password = password
        self.login()
        self.transactions()
        self.download()

    def login(self):
        driver = self.driver
        driver.get("https://accounts.intuit.com/index.html?offering_id=Intuit.ifs.mint&namespace_id=50000026&redirect_url=https%3A%2F%2Fmint.intuit.com%2Foverview.event%3Futm_medium%3Ddirect%26cta%3Dnav_login_dropdown%26adobe_mc%3DMCMID%253D04675441068150549043681284837924793455%257CMCAID%253D2E7BA5828503036A-4000119040000541%257CMCORGID%253D969430F0543F253D0A4C98C6%252540AdobeOrg%257CTS%253D1567660497%26ivid%3D1e2cf7a7-0b9b-4d88-95cf-abc7f846e052")
        time.sleep(random.randint(3, 4) + (random.randint(1, 2) / 10))
        user_name_elem = driver.find_element_by_xpath("//*[@id=\"ius-userid\"]")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)
        time.sleep(random.randint(3, 4) + (random.randint(1, 2) / 10))
        password_elem = driver.find_element_by_xpath("//*[@id=\"ius-password\"]")
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        time.sleep(random.randint(3, 4) + (random.randint(1, 2) / 10))

    def transactions(self):
        driver = self.driver
        driver.get("https://mint.intuit.com/transaction.event")
        time.sleep(random.randint(3, 4) + (random.randint(1, 2) / 10))

    def download(self):
        url = "https://mint.intuit.com/transactionDownload.event?queryNew=&offset=0&filterType=cash&comparableType=8"
        driver = self.driver
        driver.get(url)
        time.sleep(random.randint(3, 4) + (random.randint(1, 2) / 10))

transactions = mintbot(USERNAME, PASSWORD)

# Look for the file that was most recently downloaded

down_path = '/Users/paul.brown/Downloads/*'
list_of_files = glob.glob(down_path)
latest_file = max(list_of_files, key=os.path.getctime)

#now that you have the csv, bring it into pandas and have fun!

df = pd.read_csv(latest_file)
df.columns = df.columns.str.lower()
df.date = pd.to_datetime(df['date'])
#only transactions that are from beginning of 2012
df = df[df.date > '2011-12-31'].sort_values(by='date')
#only transactions that are greater than 0
df = df[df['amount'] > 0]
#change the account names to be shorter
acct_dict = {'AFCU Checking':'Checking','BankAmericard Cash Rewards Signature Visa':'BAC','Share Savings':'Savings',
            'Bank of America':'BAC','Home Equity Line  ****6254':'HELOC','Checking  ****6254':'Checking'}
df = df.replace({'account name':acct_dict})

#create df that has all the dates we care about
today = datetime.datetime.today().strftime("%m/%d/%Y")
drange = pd.date_range('2012-01-01', today)
date_df = pd.DataFrame({'date':drange})

#left join transactions to date in order to get sequential dates
df2 = date_df.merge(df, on='date', how='left')

#once you have the final dataframe, now it is time to paste it into google sheets
pycred = pygsheets.authorize(service_file='/Users/paul.brown/Documents/Python/credentials.json')
#opening the gsheet and sheet you want to work with
ss = pycred.open_by_key('1-8Ua0dlazv-edC1a-2R9lgyMavUCZ_2NR4tUj28N4VQ')[0]
#overwrite what is in the sheet with your df
ss.set_dataframe(df2,(1,1))

