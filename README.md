# 💳 The Invisible Credit Score

An explainable, alternative credit-scoring prototype for gig workers and freelancers.

**Live demo:** (https://credit-score-e25b3adeb8tvagfbjmuja4.streamlit.app/)_

> **Educational estimate only.** This is not an official credit score and is not
> accepted by banks or lenders.

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
- **Worker profiles:** score gauge, risk band, and plain-English "why this score?"
- **Compare workers:** five sample profiles side by side
- **Try your own numbers:** enter 6 months of income and savings to get your own estimate
- **How to improve:** tips targeting the weakest factors
- **What-if sliders:** see how extra savings or an extra client would change the score
- **Methodology, privacy and limitations** tab

## Privacy
Numbers typed into the "Try your own numbers" tab are used only for the current session.
Nothing is stored in a database or sent anywhere else.

## Run locally
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run the tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Project structure
```
app.py                  # Streamlit UI
scoring.py              # Scoring logic, validation and tips (testable on its own)
generate_data.py        # Synthetic data generator
data/workers.csv        # Generated sample data
tests/test_scoring.py   # Unit tests for the scoring logic
```

## Honest limitations
- **Sample workers use synthetic data.** The seed was chosen so the five sample profiles
  show clearly different cases. No real people or platforms are used.
- Weights are hand-picked, not learned from repayment data.
- Six months is a short window. Any real deployment needs consented data access,
  security review, and a fairness audit.

## Roadmap: from prototype to useful app
- [x] Interactive input for custom numbers, tips and what-if sliders
- [x] Unit tests for the scoring logic
- [ ] Validate and tune weights against real repayment outcomes
- [ ] Fairness and bias audit
- [ ] CSV upload of a bank or wallet statement summary
- [ ] Consent-based data access instead of manual entry
- [ ] Downloadable one-page summary
- [ ] Feedback form and testing with real freelancers

## Tech
Python, pandas, NumPy, Plotly, Streamlit, pytest
