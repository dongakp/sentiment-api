from celery import Celery
from transformers import pipeline

app = Celery(
    'sentiment_tasks',
    broker = 'redis://127.0.0.1:6379/0',
    backend = 'redis://127.0.0.1:6379/0',
)

@app.on_after_configure.connect
def setup_model(sender, **kwargs):
    global sentiment_analyzer
    print("model loading...")
    sentiment_analyzer = pipeline("sentiment-analysis", model="snunlp/KR-FinBert-SC")
    print("model load done")
 
@app.task(name='analyze_sentiment_task')
def analyze_sentiment(text):
    if sentiment_analyzer is None:
        return {"sentiment":"Error", "score":0.0}
    
    result = sentiment_analyzer(text)[0]
    label = result['label']
    score = result['score']
    korean_sentiment = "긍정" if label == "positive" else "부정" if label == "negative" else "중립"
    
    return {
        "sentiment": korean_sentiment,
        "score": score,
        "status": "COMPLETED"
    }