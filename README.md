# 💳 The Invisible Credit Score

An explainable, alternative credit-scoring prototype for gig workers and freelancers.

## The problem
Gig workers (drivers, freelancers, creators) have volatile income, so traditional credit
scoring often labels them "high risk" even when they are financially responsible. This
makes loans and rentals harder to get.

## The idea
Score creditworthiness from signals traditional bureaus ignore, and **explain every point**:

| Factor | Weight | What it measures |
|---|---|---|
| Income consistency | 35% | Month-to-month variation in earnings |
| Savings behaviour | 30% | Savings rate and how regularly the worker saves |
| Platform diversity & tenure | 20% | Number of platforms and months of history |
| Income trend | 15% | Whether income is rising or falling |

Each factor is scored 0-100, weighted, and scaled to a 300-900 score with a risk band.

## Features
- Score gauge with risk band for each worker
- "Why this score?" breakdown in plain English plus points per factor
- Side-by-side comparison of all workers
- Methodology and limitations tab

## Run locally
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```
app.py            # Streamlit UI
scoring.py        # Scoring logic (testable on its own)
generate_data.py  # Synthetic data generator
data/workers.csv  # Generated sample data
```

## Honest limitations
- **All data is synthetic.** The seed was chosen so the five sample profiles show
  clearly different cases. No real people or platforms are used.
- Weights are hand-picked, not learned from repayment data.
- Six months is a short window. Any real deployment needs consented data access,
  security review, and a fairness audit.

## Future work
- Consent-based bank/wallet data connections
- Validate and tune weights against real repayment outcomes
- Fairness and bias audit
- Compare the formula against an ML model
- "What-if" simulator for improving a score

## Tech
Python, pandas, NumPy, Plotly, Streamlit
