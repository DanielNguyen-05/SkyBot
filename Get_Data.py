from alpaca_trade_api import REST
import pandas as pd
from datetime import datetime

def get_data(alpaca_api_key: str, alpaca_api_secret: str, symbol: str, timeframe: str = "1Month", start: str = "2024-01-01"):
    # Tạo kết nối với Alpaca API
    base_url = "https://paper-api.alpaca.markets"
    alpaca_api = REST(alpaca_api_key, alpaca_api_secret, base_url=base_url)

    # Lấy dữ liệu và lưu vào dataframe
    bars = alpaca_api.get_bars(symbol, timeframe=timeframe, start=start).df
    return bars

def save_to_csv(dataframe: pd.DataFrame, symbol: str):
    # Lưu dữ liệu vào file CSV
    file_path = f"Data/{symbol}_du_lieu.csv"
    dataframe.to_csv(file_path, index=False)
    # print(f"Dữ liệu đã được lưu vào {file_path}")