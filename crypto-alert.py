import requests
from bs4 import BeautifulSoup
import smtplib
import lxml
import sqlite3
import config
import datetime
from colorama import Fore
import time
import sys

URL = 'https://finance.yahoo.com/quote/BTC-USD'
headers = {"User-Agent": 
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
target_price = 50000
exchange_rate_URL = 'https://api.exchangeratesapi.io/latest?base=USD' 

# Getting Real Time Exchange Rate from USD to CAD
r = requests.get(exchange_rate_URL)
data = r.json()
CAD = data['rates']['CAD']

def get_prices():
    date = datetime.datetime.now()
    current_time = date.strftime('%x %X')
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    title = soup.find('h1', class_="D(ib) Fz(18px)").get_text()
    price = soup.find('span', class_='Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)').get_text()
    converted_price = float(price.replace(",", ""))
    database_add(current_time, converted_price)
    if (converted_price * CAD < target_price):
        subject = 'Bitcoin Under Target Price'
        body = f"""/
        Bitcoin Price: ${'{:,}'.format(round(converted_price * CAD, 2))}
        Check the Chart {URL}"""
        msg = f"Subject: {subject}\n\n{body}"
        send_email(msg)
    else:
        print(f"Not Below Price Target! Current Price is ${'{:,}'.format(round(converted_price * CAD, 2))}")
        print(Fore.GREEN + "Check Again Soon!")

def database_add(date, price):
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute("INSERT INTO prices VALUES (?, ?)", (date, price))
    conn.commit()
    conn.close()

def send_email(msg):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(config.email, config.password)
        server.sendmail(config.email, config.email, msg)
    except Exception as e:
        print(e)
    server.quit()
    print(Fore.LIGHTYELLOW_EX + "Happy Buying")
    sys.exit()

if __name__ == "__main__":
    while (True):
        time.sleep(1)
        get_prices()
        time.sleep(60)
