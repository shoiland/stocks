import requests
import os
import datetime as dt
from twilio.rest import Client
import re

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
UP = "🔺"
DOWN = "🔻"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
previous_price = 0
current_price = 0
today = dt.datetime.now()
day = today.day
month = today.month
year = today.year

start_yesterday = f"{year}-{month}-{day - 1} 09:30:00"
end_yesterday = f"{year}-{month}-{day - 1} 16:30:00"
start_day_before = f"{year}-{month}-{day - 2} 09:30:00"
end_day_before = f"{year}-{month}-{day - 2} 16:30:00"


def get_difference():
    url = 'https://www.alphavantage.co/query'
    parameters = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": "IBM",
        "interval": "30min",
        "apikey": os.environ.get("API_ALPHA")
    }
    r = requests.get(url, params=parameters)
    data = r.json()
    time_series = data["Time Series (30min)"]

    yesterday_close = float(time_series[end_yesterday]["4. close"])
    day_before_close = float(time_series[end_day_before]["4. close"])

    percentage_change = round((yesterday_close - day_before_close) / day_before_close * 100, 2)
    if percentage_change >= 0.1:
        articles = get_news()
        send_news_text(articles, UP, percentage_change)
    elif percentage_change <= 0.1:
        articles = get_news()
        send_news_text(articles, DOWN, percentage_change)


def get_news():
    url = "https://newsapi.org/v2/everything"
    parameters = {
        "apiKey": os.environ.get("API_NEWS"),
        "q": f"{COMPANY_NAME}",
        "pageSize": 3
    }
    response = requests.get(url, params=parameters)
    data = response.json()
    articles = data["articles"]
    return articles


def send_news_text(articles, direction, percent):
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    body = f"{STOCK}: {direction} {percent}%\n\n"

    print(articles)
    for article in articles:
        title = article["title"]
        brief = article["description"]
        brief = re.sub('<[^<]*?/?>', '', brief)
        news_article = f"-----------\nHeadline: {title}\n\nBrief: {brief}\n\n"
        body = body + news_article

    message = client.messages \
        .create(
        body=body,
        from_='+15139603906',
        to='+15127573736'
    )

    print(message.sid)


get_difference()
