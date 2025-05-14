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

def plot_forecast(forecast: pd.DataFrame, original_data: pd.DataFrame = None, save_path: str = None):
    plt.figure(figsize=(12, 6))
    
    # Vẽ đường dự báo
    plt.plot(forecast['ds'], forecast['yhat'], label='Dự báo (yhat)', color='blue')
    
    # Vẽ khoảng tin cậy
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                     color='gray', alpha=0.2, label='Khoảng tin cậy')

    # Vẽ dữ liệu thực tế nếu có
    if original_data is not None:
        plt.plot(original_data['ds'], original_data['y'], 'ko-', 
                 label='Dữ liệu thực tế', alpha=0.7, markersize=4)

    plt.title('Dự báo giá (Forecast)')
    plt.xlabel('Ngày')
    plt.ylabel('Giá')
    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
