from fastapi import FastAPI, Query
from main import analyze_logs
import time
# from pydantic import BaseModel

app = FastAPI()


# class HealthResponse(BaseModel):
#     status: str


@app.get("/version")
def get_version():
    return {"version": "1.0"}


# @app.get("/health", response_model=HealthResponse)
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hello/{name}")
def hello(name: str):
    return {"message": "Привет, " + name}


@app.get("/status/{code}")
def get_status(code: int):
    if 400 <= code <= 599:
        return {"code": code, "is_error": True}
    else:
        return {"code": code, "is_error": False}


@app.get("/status")
def get_status_query(code: int):
    return {"code": code, "is_error": 400 <= code <= 599}


@app.get("/check-duration")
def check_duration(duration_ms: int, limit_ms: int = 200):
    return {"duration_ms": duration_ms, "limit_ms": limit_ms, "slow": duration_ms > limit_ms}


@app.post("/analyze")
def analyze_ms(logs: list[dict], limit_ms: int = Query(default=200, ge=0)):
    return analyze_logs(logs, limit_ms)


@app.get("/slow")
def slow():
    time.sleep(2)
    return {"status": "ok"}
