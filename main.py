from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tasks import analyze_sentiment_task
from celery.result import AsyncResult

class TextInput(BaseModel):
    text: str
    
class SentimentOutput(BaseModel):
    sentiment: str
    score: float
    
class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    
app = FastAPI()

@app.post("/predict/sentiment", response_model=TaskStatus)
def submint_sentiment_analysis(input_data: TextInput):
    task = analyze_sentiment_task.delay(input_data.text)
    
    return TaskStatus(
        task_id = task.id,
        status = task.status,
        result=None
    )
    
@app.get("/tasks/{task_id}", response_model = TaskStatus)
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app = analyze_sentiment_task.app)
    
    if task.status == 'PENDING':
        result_data = None
    elif task.state == 'FAILURE':
        raise HTTPException(status_code=500, detail="Task execution failed.")
    else:
        result_data = task.result    
    
    return TaskStatus(
        task_id = task.id,
        status = task.status,
        result = result_data
    )

@app.get("/")
def home():
    return {"message": "AI Sentiment Analysis API is running. Go to /docs for API details."}