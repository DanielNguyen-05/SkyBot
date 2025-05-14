import Get_Data
import Plotting
import Get_News
import Sentiment_Analysis
import LLMs_Advice
import Forecast
import pandas as pd
import numpy as np

def main(alpaca_api_key, alpaca_api_secret, symbol):
    # Lấy dữ liệu từ Alpaca
    data = Get_Data.get_data(alpaca_api_key, alpaca_api_secret, symbol)
    Get_Data.save_to_csv(data, symbol)
    
    # Lấy cảm xúc thị trường
    news = Get_News.get_news(alpaca_api_key, alpaca_api_secret, symbol)
    probability, sentiment = Sentiment_Analysis.estimate_sentiment(news)
    
    # Lấy lời khuyên từ AI
    advice = LLMs_Advice.get_advice(data, sentiment, probability)
    
    # Chuẩn bị dữ liệu forecast
    path = f"Data/{symbol}_du_lieu.csv"
    forecast_df = Forecast.forecasting(path, column_name="close", periods=7, future_only=True)
    
    # Đọc và chuẩn bị dữ liệu gốc
    df = pd.read_csv(path)
    if 'date' in df.columns:
        df['ds'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    elif 'timestamp' in df.columns:
        df['ds'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    df['y'] = df['close'].astype(float)
    
    # Tính toán các chỉ số đánh giá
    mae, rmse, mape = 0.0, 0.0, 0.0
    historical_forecast = forecast_df[forecast_df['ds'] <= df['ds'].max()].copy()
    
    if not historical_forecast.empty:
        merged = pd.merge(historical_forecast, df[['ds', 'y']], on='ds', how='inner')
        if len(merged) > 0:
            y_true = merged['y']
            y_pred = merged['yhat']
            mae = np.mean(np.abs(y_true - y_pred))
            rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    # Tạo và lưu đồ thị
    forecast_img_path = f"Data/{symbol}_forecast.png"
    Plotting.plot_forecast(forecast_df, df, save_path=forecast_img_path)
    
    return {
        "advice": advice,
        "forecast": forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
        "metrics": {
            "mae": mae,
            "rmse": rmse,
            "mape": mape
        },
        "image_path": forecast_img_path
    }

if __name__ == "__main__":
    main()
