"""Generate synthetic gig-worker data (no real personal data is used)."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "workers.csv"

# name, base income (INR), volatility, monthly trend, savings rate, platforms, tenure (months)
WORKERS = [
    ("Asha",  40000, 0.08,  0.03, 0.15, 3, 30),
    ("Ravi",  35000, 0.35,  0.00, 0.05, 1, 8),
    ("Meera", 50000, 0.20,  0.05, 0.10, 2, 18),
    ("Kabir", 30000, 0.45, -0.04, 0.02, 1, 5),
    ("Priya", 45000, 0.12,  0.00, 0.20, 2, 24),
]


def generate_data(seed: int = 88) -> pd.DataFrame:
    rng = np.random.default_rng(seed)  # fixed seed = same data every run
    months = pd.date_range("2026-04-01", periods=6, freq="MS")
    rows = []
    for name, base, vol, trend, save_rate, platforms, tenure in WORKERS:
        for i, month in enumerate(months):
            income = base * (1 + trend * i) * (1 + rng.normal(0, vol))
            income = max(income, 0)
            savings = max(0, income * save_rate * (1 + rng.normal(0, 0.3)))
            rows.append({
                "worker": name,
                "month": month.strftime("%Y-%m"),
                "income": income,
                "savings": savings,
                "platforms": platforms,
                "tenure_months": tenure,
            })
    df = pd.DataFrame(rows).round(0)
    DATA_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df


if __name__ == "__main__":
    print(generate_data().head(10))
