import Get_Data
import Plotting
import Get_News
import Sentiment_Analysis
import LLMs_Advice
import Forecast

def main(alpaca_api_key, alpaca_api_secret, symbol):
    # Nhập API_KEY, API_SECRET và tên cổ phiếu
    # api_key = input("Nhập API_KEY của bạn: ")
    # api_secret = input("Nhập API_SECRET của bạn: ")
    # symbol = input("Nhập tên cổ phiếu (ví dụ: SPY): ")

    alpaca_api_key = alpaca_api_key
    alpaca_api_secret = alpaca_api_secret
    symbol = symbol

    # Lấy dữ liệu từ Alpaca
    data = Get_Data.get_data(alpaca_api_key, alpaca_api_secret, symbol)

    # Lưu dữ liệu vào file CSV
    Get_Data.save_to_csv(data, symbol)

    # Lấy cảm xúc
    news = Get_News.get_news(alpaca_api_key, alpaca_api_secret, symbol)
    probability, sentiment = Sentiment_Analysis.estimate_sentiment(news)

    #Lấy lời khuyên
    advice = LLMs_Advice.get_advice(data, sentiment, probability)

    #Cho lời khuyên
    print("\n Lời khuyên từ SkyBot:\n")
    print(advice)

    #Forecast từ data
    path = f"Data/{symbol}_du_lieu.csv"
    forecast_df = Forecast.forecasting(path, column_name="close", periods=14)
    Plotting.plot_forecast(forecast_df)
    print(forecast_df.tail())

if __name__ == "__main__":
    main()
