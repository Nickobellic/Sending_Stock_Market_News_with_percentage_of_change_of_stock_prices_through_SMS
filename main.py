import requests
import datetime
import time
import os
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

t = datetime.datetime
x = datetime.timedelta
db_yest = t.date(t.now()-x(days=2))
yest = t.date(t.now()-x(days=1))

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = os.environ.get('SAK')
NEWS_API_KEY = os.environ.get('NAK')
TWILIO_KEY = os.environ.get('TK')
SID = os.environ.get('S')
AUTH = os.environ.get('A')

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
api_ep = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={STOCK}&interval=5min&outputsize=full&apikey={STOCK_API_KEY}"
data = requests.get(api_ep).json()
yest_closing_price = float(data['Time Series (5min)'][f"{yest} 20:00:00"]['4. close'])
db_yest_closing_price = float(data['Time Series (5min)'][f"{db_yest} 20:00:00"]['4. close'])
difference = round(yest_closing_price - db_yest_closing_price,2)
percentage = round((difference*100)/yest_closing_price,2)
if percentage < 0:
    message = f"🔻{abs(percentage)}"
else:
    message = f"🔺{percentage}"
if abs(percentage) >= 5.00:
    print('Get News')
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
api_news = f"https://newsapi.org/v2/everything?q={COMPANY_NAME}&from={t.date(t.now())}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
news = requests.get(api_news).json()
title = []
desc = []
for i in range(3):
    title.append(news['articles'][i]['title'])
    desc.append(news['articles'][i]['description'])
## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
for i in range(3):
    proxy = TwilioHttpClient()
    proxy.session.proxies = {'https': os.environ['http_proxy']}
    client = Client(SID, AUTH, http_client=proxy)
    sms = client.messages.create(body=f"{STOCK}: {message}%\nHeadline: {title[i]}\nBrief: {desc[i]}", from_='+15139352451', to='+917904692237')
    print(sms.status)
    time.sleep(3)




#Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?.
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

