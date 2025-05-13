import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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

def plot_forecast(forecast: pd.DataFrame):
    plt.figure(figsize=(10, 6))

    plt.plot(forecast['ds'], forecast['yhat'], label='Dự báo (yhat)', color='blue')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2, label='Khoảng tin cậy')

    plt.title('Dự báo giá (Forecast)')
    plt.xlabel('Ngày')
    plt.ylabel('Giá đóng cửa')

    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    plt.legend()
    plt.tight_layout()
    plt.show()
