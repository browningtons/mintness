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

