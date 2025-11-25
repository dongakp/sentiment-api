from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

class TextInput(BaseModel):
    text: str
    
class SentimentOutput(BaseModel):
    sentiment: str
    score: float
    
app = FastAPI()

@app.on_event("startup")
async def load_model():
    global sentiment_analyzer
    print("model loading...")
    sentiment_analyzer = pipeline("sentiment-analysis", model="snunlp/KR-FinBert-SC")
    print("model load done")

@app.post("/predict/sentiment", response_model=SentimentOutput)
def analyze_sentiment(input_data: TextInput):
    if sentiment_analyzer is None:
        return {"sentiment":"Error", "score":0.0}
    
    result = sentiment_analyzer(input_data.text)[0]
    label = result['label']
    score = result['score']
    print(label)
    korean_sentiment = "긍정" if label == "positive" else "부정" if label == "negative" else "중립"
    
    return SentimentOutput(sentiment=korean_sentiment, score=score)

@app.get("/")
def home():
    return {"message": "AI Sentiment Analysis API is running. Go to /docs for API details."}