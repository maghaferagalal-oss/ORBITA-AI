# ORBITA 2.0 — The Living Health Twin
**Software-only | HTML/CSS/JavaScript + Python FastAPI | Multi-model AI**

## Project decision
ORBITA is a browser-based software prototype. It requires **no hardware**: no sensors, Arduino, ESP32, wearable, or physical device. All current inputs and training examples are synthetic demonstration data.

## Architecture
- **Frontend:** semantic HTML, responsive CSS, vanilla JavaScript.
- **Backend:** Python + FastAPI REST API.
- **AI model 1:** Isolation Forest — screens for unusual multivariable patterns.
- **AI model 2:** Random Forest Regressor — illustrative next-step forecast from the latest three synthetic records.
- **AI model 3:** K-Means — groups profiles into synthetic pattern clusters.
- **Storage:** SQLite local database for saved simulation records.
- **Validation:** Pydantic request schemas and input bounds.

## Run on Windows
1. Install Python 3.10+.
2. Open this folder in VS Code.
3. In Terminal:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Open `http://127.0.0.1:8000`.
5. API documentation: `http://127.0.0.1:8000/docs`.

If `py` does not work, try `python`. Keep the terminal open while using the website.

## Main API routes
- `GET /api/health` — server status.
- `GET /api/demo` — one synthetic demo profile.
- `POST /api/analyze` — multi-model profile analysis.
- `POST /api/forecast` — next-step synthetic forecast from 3–90 records.
- `POST /api/readings` — save a local demo record.
- `GET /api/readings` — retrieve saved records.
- `GET /api/models` — model descriptions.

## Input fields
`sleep_hours`, `activity_index`, `stress_index`, `radiation_index`, `hr_deviation_index`.

## Scientific and safety limitations
- The current dataset is synthetic; it is not astronaut or clinical data.
- The radiation field is an abstract index, **not a physical radiation dose** such as mSv.
- The anomaly flag means only that the input differs from the synthetic model baseline.
- Forecast ranges are illustrative and are not calibrated confidence intervals.
- No output is a diagnosis, disease probability, treatment recommendation, or emergency decision.
- Do not claim NASA/CSA endorsement or operational flight readiness.
- Real research would require suitable documented datasets, domain-expert review, external validation, privacy controls, and safety assessment.

## Suggested development sequence
1. Confirm API and front-end run locally.
2. Test each endpoint and input validation.
3. Add unit tests and held-out synthetic evaluation.
4. Replace demo-only data only if a suitable, licensed, scientifically relevant dataset is identified.
5. Add authentication, access control, audit logs, and encryption before any sensitive data use.
