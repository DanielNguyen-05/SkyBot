from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple, List

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

def estimate_sentiment(news: List[str]) -> Tuple[float, str]:
    if news:
        tokens = tokenizer(news, return_tensors="pt", padding=True, truncation=True).to(device)
        with torch.no_grad():
            result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"]).logits
        result = torch.nn.functional.softmax(torch.sum(result, dim=0), dim=-1)
        probability = result[torch.argmax(result)].item()
        sentiment = labels[torch.argmax(result)]
        return probability, sentiment
    else:
        return 0.0, "neutral"
