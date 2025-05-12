import Get_Data
import Plotting
import Get_News
import Sentiment_Analysis
import LLMs_Advice

def main():
    # Nhập API_KEY, API_SECRET và tên cổ phiếu
    api_key = input("Nhập API_KEY của bạn: ")
    api_secret = input("Nhập API_SECRET của bạn: ")
    symbol = input("Nhập tên cổ phiếu (ví dụ: SPY): ")

    # Lấy dữ liệu từ Alpaca
    data = Get_Data.get_data(api_key, api_secret, symbol)

    # Lưu dữ liệu vào file CSV
    Get_Data.save_to_csv(data, symbol)

    # Lấy cảm xúc
    news = Get_News.get_news(api_key, api_secret, symbol)
    probability, sentiment = Sentiment_Analysis.estimate_sentiment(news)

    #Lấy lời khuyên
    advice = LLMs_Advice.get_advice(data, sentiment, probability)

    #Cho lời khuyên
    print("\n Lời khuyên từ AI:\n")
    print(advice)

if __name__ == "__main__":
    main()