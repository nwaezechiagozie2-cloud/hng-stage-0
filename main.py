from fastapi import FastAPI, HTTPException
import requests
import datetime
import json
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()
genderizeUrl = 'https://api.genderize.io'

@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    if exc.status_code == 500:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An unexpected error occurred."})
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail})

app.add_exception_handler(HTTPException, http_exception_handler)


@app.get('/api/classify')
def predictGender(name: Optional[str] = None):
    if not name:
        raise HTTPException(status_code=400, detail="Name parameter is required")
    if not name.isalpha():
        raise HTTPException(status_code=422, detail="Name must contain only alphabetic characters")
    try:
        response = requests.get(genderizeUrl, params={"name": name})
        data = response.json()
        if data.get('gender') is None or data.get('count', 0) == 0:
            raise HTTPException(status_code=404, detail="No prediction available for the provided name")
        return {
            "name": data['name'],
            "gender": data['gender'],
            "probability": data['probability'],
            "sample_size": data['count'],
            "is_confident": (data['probability'] >= 0.7 and data['count'] >= 100),
            "processed_at": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
