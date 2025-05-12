from alpaca_trade_api import REST
from datetime import datetime, timedelta
from typing import List

def get_news(api_key: str, api_secret: str, symbol: str, base_url: str = "https://paper-api.alpaca.markets", days_ago: int = 3) -> List[str]:
    api = REST(api_key, api_secret, base_url=base_url)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_ago)
    
    news = api.get_news(symbol=symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    headlines = [article.__dict__["_raw"]["headline"] for article in news]
    return headlines
