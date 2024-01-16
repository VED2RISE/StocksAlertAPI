import requests as rq
from datetime import datetime, timedelta
from twilio.rest import Client
import keys

def fetch_stock_data(key, name):
    endpoint_st = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY", 
        "symbol": name, 
        "interval": "30min", 
        "apikey": key, 
        "extended_hours": "false"
    }
    
    try:
        response = rq.get(url=endpoint_st, params=params)
        response.raise_for_status()
        return response.json()
    except rq.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {}
    except Exception as e:
        print(f"Error occurred: {e}")
        return {}

def get_stock_change(data):
    try:
        current_date = datetime.now()
        yesterday_date = current_date - timedelta(days=1)
        formatted_yesterday = yesterday_date.strftime("%Y-%m-%d")
        
        if "Time Series (30min)" not in data:
            print("Data for 'Time Series (30min)' not found.")
            return 0, 0  
        
        open_timestamp = f"{formatted_yesterday} 09:30:00"
        close_timestamp = f"{formatted_yesterday} 15:30:00"
        
        # Check if necessary timestamps are available
        if open_timestamp not in data["Time Series (30min)"] or close_timestamp not in data["Time Series (30min)"]:
            print(f"Data for timestamps {open_timestamp} or {close_timestamp} not found.")
            return 0, 0  # Return default values 
        
        day_open = float(data["Time Series (30min)"][open_timestamp]["4. close"])
        day_closed = float(data["Time Series (30min)"][close_timestamp]["4. close"])
        
        change_more = (day_closed / day_open) * 100 - 100
        change_less = (day_open / day_closed) * 100 - 100
        
        return change_more, change_less
    except Exception as e:
        print(f"Error calculating stock change: {e}")
        return 0, 0

def fetch_news(company, key):
    current_date = datetime.now()
    yesterday_date = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
    endpoint_news = "https://newsapi.org/v2/everything"
    params = {
        "qInTitle": company,
        "apiKey": key,
        "language": "en", 
        "from": yesterday_date
    }
    
    response = rq.get(url=endpoint_news, params=params)
    news_data = response.json()

    if 'articles' in news_data and len(news_data['articles']) > 0:
        articles = news_data['articles'][:3]  # Fetching the first 3 articles
        return articles
    else:
        return []

def format_news_articles(articles):
    formatted_articles = []
    for article in articles:
        title = article["title"]
        brief = article["description"]
        formatted_articles.append(f"Title: {title}\nBrief: {brief}\n")
    return formatted_articles

def deploy_sms(sender, receiver, news, stock_change):
    """Send sms about stock's change"""
    client = Client(keys.account_sid, keys.auth_token)
    message_body = f"Stock Change: {'🔺' if stock_change >= 5 else '🔻'}{abs(stock_change)}%\n\n"
    
    for article in news:
        message_body += f"{article}\n"

    try:
        message = client.messages.create(body=message_body, from_=sender, to=receiver)
        print(f"Message sent! Message SID: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def main():
    STOCK = "TSLA"
    COMPANY_NAME = "Tesla Inc"
    from_number = keys.twilio_number
    to_number = keys.target_number

    try:
        api_key_stocks = keys.api_key_stocks
        api_key_news = keys.api_key_news

        stock_data = fetch_stock_data(api_key_stocks, STOCK)
        stock_change_more, stock_change_less = get_stock_change(stock_data)

        if stock_change_more >= 5 or stock_change_less >= 5:
            news_articles = fetch_news(COMPANY_NAME, api_key_news)
            formatted_articles = format_news_articles(news_articles)
            deploy_sms(from_number, to_number, formatted_articles, max(stock_change_more, stock_change_less))
    except rq.RequestException as req_err:
        print(f"Request Error: {req_err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()