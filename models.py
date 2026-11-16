"""ORBITA demo ML models. All data generated here are synthetic."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "sleep_hours", "activity_index", "stress_index",
    "radiation_index", "hr_deviation_index"
]
CENTERS = np.array([7.5, 76.0, 25.0, 18.0, 5.0])
SCALES = np.array([1.1, 16.0, 18.0, 15.0, 5.0])

def synthetic_baseline(n: int = 1800, seed: int = 42) -> pd.DataFrame:
    """Create clearly synthetic demo data; not astronaut or clinical records."""
    rng = np.random.default_rng(seed)
    sleep = np.clip(rng.normal(7.5, 0.85, n), 4.5, 10.5)
    activity = np.clip(rng.normal(76, 13, n), 20, 100)
    stress = np.clip(rng.normal(25, 13, n), 0, 75)
    radiation = np.clip(rng.normal(18, 10, n), 0, 65)
    hr_dev = np.clip(rng.normal(5, 3.5, n), 0, 22)
    return pd.DataFrame({
        "sleep_hours": sleep,
        "activity_index": activity,
        "stress_index": stress,
        "radiation_index": radiation,
        "hr_deviation_index": hr_dev,
    })

def synthetic_sequences(n_series: int = 260, length: int = 18, seed: int = 123):
    """Generate synthetic short sequences for next-step demonstration forecasts."""
    rng = np.random.default_rng(seed)
    x_rows, y_rows = [], []
    for _ in range(n_series):
        base = CENTERS + rng.normal(0, [0.4, 7, 7, 5, 2], 5)
        phase = rng.uniform(0, 2*np.pi)
        seq = []
        for t in range(length + 1):
            wave = np.array([
                0.35*np.sin(t/3 + phase),
                5*np.sin(t/4 + phase),
                4*np.cos(t/4 + phase),
                2*np.sin(t/5 + phase),
                1.0*np.cos(t/3 + phase),
            ])
            noise = rng.normal(0, [0.22, 2.5, 2.5, 1.8, 0.8], 5)
            row = base + wave + noise
            row[0] = np.clip(row[0], 4, 10)
            row[1:] = np.clip(row[1:], [0,0,0,0], [100,100,100,30])
            seq.append(row)
        for t in range(length - 2):
            # Recent 3-day window -> following-day feature vector
            x_rows.append(np.concatenate(seq[t:t+3]))
            y_rows.append(seq[t+3])
    return np.asarray(x_rows), np.asarray(y_rows)

class OrbitaModels:
    def __init__(self):
        baseline = synthetic_baseline()
        self.anomaly = IsolationForest(
            n_estimators=240, contamination=0.075, random_state=42
        ).fit(baseline[FEATURES])
        self.scaler = StandardScaler().fit(baseline[FEATURES])
        scaled = self.scaler.transform(baseline[FEATURES])
        self.cluster = KMeans(n_clusters=3, random_state=42, n_init=12).fit(scaled)

        x, y = synthetic_sequences()
        self.forecaster = RandomForestRegressor(
            n_estimators=160, max_depth=12, min_samples_leaf=3,
            random_state=42, n_jobs=-1
        ).fit(x, y)

        self.cluster_names = {
            0: "Balanced demo pattern",
            1: "Lower-activity demo pattern",
            2: "Higher-variation demo pattern",
        }
        # Re-map cluster names using cluster centers to avoid relying on IDs.
        centers = self.scaler.inverse_transform(self.cluster.cluster_centers_)
        self.cluster_names = {}
        for i, c in enumerate(centers):
            if c[1] < 68:
                name = "Lower-activity demo pattern"
            elif c[2] > 29:
                name = "Higher-stress demo pattern"
            else:
                name = "Balanced demo pattern"
            self.cluster_names[i] = name

    def analyze(self, values: dict):
        row = pd.DataFrame([[float(values[k]) for k in FEATURES]], columns=FEATURES)
        label = int(self.anomaly.predict(row)[0])
        score = float(self.anomaly.decision_function(row)[0])
        cluster_id = int(self.cluster.predict(self.scaler.transform(row))[0])
        z = (row.iloc[0].to_numpy() - CENTERS) / SCALES
        contribution = [
            {"feature": key, "value": round(float(row.iloc[0][key]), 2),
             "deviation": round(float(abs(zv)), 2),
             "direction": "above" if zv > 0 else "below"}
            for key, zv in zip(FEATURES, z)
        ]
        contribution.sort(key=lambda item: item["deviation"], reverse=True)
        return {
            "flag": "unusual_demo_pattern" if label == -1 else "within_demo_pattern",
            "screening_score": round(score, 4),
            "cluster": self.cluster_names[cluster_id],
            "top_deviations": contribution[:3],
            "model_note": "Isolation Forest screening; not a medical risk score."
        }

    def forecast(self, history: list[dict]):
        if len(history) < 3:
            raise ValueError("At least 3 sequential records are required.")
        recent = np.array([[float(row[k]) for k in FEATURES] for row in history[-3:]])
        pred = self.forecaster.predict(recent.reshape(1, -1))[0]
        pred[0] = np.clip(pred[0], 0, 12)
        pred[1:] = np.clip(pred[1:], [0,0,0,0], [100,100,100,30])
        spread = np.std(recent, axis=0)
        uncertainty = np.maximum(spread * 0.8, [0.25, 2, 2, 1.5, 0.6])
        return {
            "forecast": {k: round(float(v), 2) for k, v in zip(FEATURES, pred)},
            "illustrative_range": {
                k: [round(float(max(lo, v-u)), 2), round(float(min(hi, v+u)), 2)]
                for k, v, u, lo, hi in zip(
                    FEATURES, pred, uncertainty,
                    [0,0,0,0,0], [12,100,100,100,30]
                )
            },
            "note": "Synthetic next-step demonstration forecast, not a clinical prediction."
        }

MODELS = OrbitaModels()
