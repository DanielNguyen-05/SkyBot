from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt

def forecasting(csv_path: str, column_name: str = "close", periods: int = 7):
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

    model = Prophet()
    model.fit(df[['ds', 'y']].dropna())

    # Dự báo trong tương lai (theo tháng)
    future = model.make_future_dataframe(periods=periods, freq='MS')  # MS = Month Start
    forecast = model.predict(future)

    # Làm tròn kết quả
    forecast[['yhat', 'yhat_lower', 'yhat_upper']] = forecast[['yhat', 'yhat_lower', 'yhat_upper']].round(2)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

