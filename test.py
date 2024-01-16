import requests as rq
from datetime import datetime, timedelta

api_key_news = "eae4c985a4594982999d1a559a400330"
COMPANY_NAME = "Tesla Inc"

def fetch_news(company, key):
    current_date = datetime.now()
    yesterday_date = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
    endpoint_news = "https://newsapi.org/v2/everything"
    parameters = {
        "qInTitle": company,
        "apiKey": key,
        "language": "en", 
        "from": yesterday_date
    }
    
    response = rq.get(url=endpoint_news, params=parameters).json()

    if 'articles' in response and len(response['articles']) > 0:
        most_popular_title = response['articles'][0]["title"]
        return most_popular_title
    else:
        return f"No articles heve been found"

