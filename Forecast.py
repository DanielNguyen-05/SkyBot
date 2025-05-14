from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def forecasting(csv_path: str, column_name: str = "close", periods: int = 7, future_only: bool = True):
    # Đọc dữ liệu CSV
    df = pd.read_csv(csv_path)

    # Kiểm tra và chuyển đổi cột ngày, loại bỏ timezone nếu có
    if 'date' in df.columns:
        df['ds'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    elif 'timestamp' in df.columns:
        df['ds'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    else:
        raise ValueError("Không tìm thấy cột 'date' hoặc 'timestamp' trong file CSV")

    # Tạo cột y từ cột giá
    df['y'] = df[column_name].astype(float)
    
    # Lưu lại ngày cuối cùng trong dữ liệu để phân biệt quá khứ vs tương lai
    last_date = df['ds'].max()

    model = Prophet()
    model.fit(df[['ds', 'y']].dropna())

    # Dự báo trong tương lai (theo tháng)
    future = model.make_future_dataframe(periods=periods, freq='D')  
    forecast = model.predict(future)

    # Làm tròn kết quả
    forecast[['yhat', 'yhat_lower', 'yhat_upper']] = forecast[['yhat', 'yhat_lower', 'yhat_upper']].round(2)
    
    # Nếu chỉ muốn dự báo tương lai
    if future_only:
        forecast = forecast[forecast['ds'] > last_date]
    
    # Tính các chỉ số đánh giá mô hình nếu có dữ liệu quá khứ
    historical_forecast = forecast[forecast['ds'] <= last_date].copy()
    if not historical_forecast.empty:
        # Merge với dữ liệu thực tế
        merged = pd.merge(historical_forecast, df[['ds', 'y']], on='ds', how='inner')
        
        if len(merged) > 0:
            mae = np.mean(np.abs(merged['y'] - merged['yhat']))
            rmse = np.sqrt(np.mean((merged['y'] - merged['yhat']) ** 2))
            mape = np.mean(np.abs((merged['y'] - merged['yhat']) / merged['y'])) * 100
            
            print(f"Đánh giá mô hình trên dữ liệu quá khứ:")
            print(f"MAE: {mae:.2f}")
            print(f"RMSE: {rmse:.2f}")
            print(f"MAPE: {mape:.2f}%")

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


