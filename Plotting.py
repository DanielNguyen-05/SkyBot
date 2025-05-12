import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

def plot_candlestick(data: pd.DataFrame, title: str = "Candlestick Chart", ylabel: str = "Giá", volume: bool = True):
    data.index = pd.to_datetime(data.index)
    mpf.plot(data, type='candle', style='charles', title=title, ylabel=ylabel, volume=volume)

def plot_candlestick_from_csv(csv_path: str, title: str = "Candlestick Chart", ylabel: str = "Giá", volume: bool = True):
    try:
        df = pd.read_csv(csv_path, index_col='date')
        plot_candlestick(df, title=title, ylabel=ylabel, volume=volume)
    except Exception as e:
        print(f"Error loading CSV or plotting candlestick: {e}")