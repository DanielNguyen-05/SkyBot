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
        f"Tôi là một nhà đầu tư chứng khoán.\n"
        f"Dưới đây là dữ liệu 5 ngày gần nhất của mã cổ phiếu:\n{recent_data}\n\n"
        f"Cảm xúc thị trường hiện tại là: {sentiment} (xác suất {float(probability):.2f}).\n"
        f"Bạn có thể đưa ra lời khuyên đầu tư dựa trên dữ liệu và cảm xúc thị trường này không?"
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
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Không thể trích xuất phản hồi từ Gemini API."
    else:
        return f"Lỗi khi gọi Gemini API: {response.status_code}, {response.text}"
