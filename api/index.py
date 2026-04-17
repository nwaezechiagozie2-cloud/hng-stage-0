from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
genderize_url = "https://api.genderize.io"
http_client: Optional[httpx.AsyncClient] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.on_event("startup")
async def startup_event() -> None:
    global http_client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(20.0, connect=20.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global http_client
    if http_client is not None:
        await http_client.aclose()
        http_client = None

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 500:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An unexpected error occurred."},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred."},
    )


@app.get('/api/classify')
async def predictGender(name: Optional[str] = None):
    if not name:
        raise HTTPException(status_code=400, detail="Name parameter is required")
    if not name.isalpha():
        raise HTTPException(status_code=422, detail="Name must contain only alphabetic characters")

    if http_client is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        response = await http_client.get(genderize_url, params={"name": name})
        response.raise_for_status()
        data = response.json()
        if data.get('gender') is None or data.get('count', 0) == 0:
            raise HTTPException(status_code=404, detail="No prediction available for the provided name")

        probability = float(data.get("probability", 0))
        sample_size = int(data.get("count", 0))
        return {
            "name": data['name'],
            "gender": data['gender'],
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": (probability >= 0.7 and sample_size >= 100),
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Upstream request timed out")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Upstream service unavailable")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Upstream service error")

