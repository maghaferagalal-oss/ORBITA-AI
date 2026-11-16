from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .models import MODELS, FEATURES, synthetic_baseline
from .schemas import IndicatorInput, ForecastInput
from .storage import init_db, save_reading, latest_readings

# Ensure the local demo database exists for both server runs and API tests.
init_db()

ROOT = Path(__file__).resolve().parent
app = FastAPI(
    title="ORBITA API",
    description="Software-only synthetic space-health pattern research prototype.",
    version="2.0.0"
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "project": "ORBITA", "data_mode": "synthetic_demo"}

@app.get("/api/demo")
def demo():
    row = synthetic_baseline(1).iloc[0].to_dict()
    return {k: round(float(v), 2) for k, v in row.items()}

@app.post("/api/analyze")
def analyze(payload: IndicatorInput):
    values = payload.model_dump()
    result = MODELS.analyze(values)
    return {"input": values, "analysis": result, "data_label": "synthetic_demo"}

@app.post("/api/forecast")
def forecast(payload: ForecastInput):
    try:
        result = MODELS.forecast([row.model_dump() for row in payload.history])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return result

@app.post("/api/readings")
def create_reading(payload: IndicatorInput, crew_id: str = "CREW-DEMO", scenario: str = "Custom"):
    values = payload.model_dump()
    save_reading(crew_id[:40], scenario[:80], values)
    return {"saved": True, "message": "Synthetic demo reading saved locally."}

@app.get("/api/readings")
def get_readings(limit: int = 50):
    return {"items": latest_readings(max(1, min(limit, 200)))}

@app.get("/api/models")
def model_info():
    return {
        "models": [
            {"name": "Isolation Forest", "purpose": "Unusual-pattern screening"},
            {"name": "Random Forest Regressor", "purpose": "Illustrative next-step forecasting"},
            {"name": "K-Means", "purpose": "Grouping similar demo patterns"},
        ],
        "disclaimer": "All models use synthetic demonstration data and are not medically validated."
    }
