import os
from dotenv import load_dotenv
import requests
import pandas as pd
from typing import Tuple

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


def generate_prompt(df: pd.DataFrame, sentiment: str, probability: float) -> str:
    recent_data = df.tail(5).to_string(index=False)
    prompt = (
        f"Bạn là SkyBot - chuyên gia phân tích đầu tư chứng khoán. Hãy đưa ra khuyến nghị ngắn gọn, sắc bén về mã cổ phiếu dựa trên:\n"
        f"- Dữ liệu 5 ngày gần nhất:\n{recent_data}\n"
        f"- Cảm xúc thị trường: {sentiment} (độ tin cậy {probability:.0%})\n\n"
        f"**Yêu cầu:**\n"
        f"1. Phân tích chi tiết\n"
        f"2. Khuyến nghị rõ ràng (Mua/Giữ/Bán) với lý do\n"
        f"3. Dự đoán độ chính xác của lời khuyên"
    )
    return prompt

def get_advice(df: pd.DataFrame, sentiment: str, probability: float) -> str:
    prompt = generate_prompt(df, sentiment, probability)

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            raw_advice = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            # Xử lý để đảm bảo format đồng nhất
            if "không thể đưa ra lời khuyên tài chính" in raw_advice:
                raw_advice = raw_advice.replace("không thể đưa ra lời khuyên tài chính", "đưa ra khuyến nghị")
                
            return raw_advice
        except (KeyError, IndexError):
            return "[SkyBot] Hiện không thể phân tích. Vui lòng thử lại sau."
