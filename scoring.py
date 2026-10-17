"""Explainable alternative credit-scoring logic for gig workers.

Each factor is scored 0-100, then combined with fixed weights into a
300-900 score. Every factor reports how many points it added, so the
final score can always be explained.
"""
import numpy as np
import pandas as pd

SCORE_MIN, SCORE_MAX = 300, 900

# Weights must add up to 1.0
WEIGHTS = {
    "Income consistency": 0.35,
    "Savings behaviour": 0.30,
    "Platform diversity & tenure": 0.20,
    "Income trend": 0.15,
}


def _clip(value: float) -> float:
    return float(np.clip(value, 0, 100))


def income_consistency(income: pd.Series) -> float:
    """Lower variation relative to the average = higher score."""
    mean = income.mean()
    if mean <= 0:
        return 0.0
    cv = income.std(ddof=0) / mean  # coefficient of variation
    return _clip(100 * (1 - cv / 0.5))  # cv of 0.5 or more scores 0


def income_trend(income: pd.Series) -> float:
    """Rising income scores above 50, falling income below 50."""
    mean = income.mean()
    if mean <= 0 or len(income) < 2:
        return 50.0
    slope = np.polyfit(range(len(income)), income, 1)[0]  # change per month
    return _clip(50 + (slope / mean) * 1000)


def savings_behaviour(income: pd.Series, savings: pd.Series) -> float:
    """Reward both the savings rate and saving regularly."""
    total_income = income.sum()
    if total_income <= 0:
        return 0.0
    rate_score = _clip((savings.sum() / total_income) / 0.20 * 100)  # 20% = full marks
    regularity = (savings > 0).mean() * 100
    return _clip(0.7 * rate_score + 0.3 * regularity)


def diversity_and_tenure(platforms: int, tenure_months: int) -> float:
    """More platforms and a longer track record = more trustworthy."""
    platform_score = min(platforms, 3) / 3 * 100  # 3+ platforms = full marks
    tenure_score = min(tenure_months, 24) / 24 * 100  # 2+ years = full marks
    return _clip(0.4 * platform_score + 0.6 * tenure_score)


def risk_band(score: float) -> str:
    if score >= 750:
        return "Low risk"
    if score >= 650:
        return "Moderate risk"
    if score >= 550:
        return "Elevated risk"
    return "High risk"


def score_worker(df: pd.DataFrame) -> dict:
    """df holds one worker's monthly rows. Returns the score and a full breakdown."""
    df = df.sort_values("month")
    factors = {
        "Income consistency": income_consistency(df["income"]),
        "Savings behaviour": savings_behaviour(df["income"], df["savings"]),
        "Platform diversity & tenure": diversity_and_tenure(
            int(df["platforms"].iloc[0]), int(df["tenure_months"].iloc[0])
        ),
        "Income trend": income_trend(df["income"]),
    }
    span = SCORE_MAX - SCORE_MIN
    points = {name: WEIGHTS[name] * factors[name] / 100 * span for name in factors}
    score = SCORE_MIN + sum(points.values())
    return {
        "score": round(score),
        "band": risk_band(score),
        "factors": factors,   # 0-100 per factor
        "points": points,     # points each factor added above the 300 base
    }


def explain(result: dict) -> list[str]:
    """Plain-English reasons, strongest factor first."""
    notes = {
        "Income consistency": ("Earnings are steady month to month.",
                               "Earnings swing a lot between months."),
        "Savings behaviour": ("Saves a healthy share of income, regularly.",
                              "Saves little or irregularly."),
        "Platform diversity & tenure": ("Long track record across several platforms.",
                                        "Short history or dependence on one platform."),
        "Income trend": ("Income is growing over time.",
                         "Income is flat or declining."),
    }
    lines = []
    for name, value in sorted(result["factors"].items(), key=lambda kv: -kv[1]):
        good, bad = notes[name]
        lines.append(f"**{name}** ({value:.0f}/100): {good if value >= 60 else bad}")
    return lines


# ---------------------------------------------------------------------------
# Custom inputs (for the "Try your own numbers" tab)
# ---------------------------------------------------------------------------

TIPS = {
    "Income consistency": (
        "Try to smooth out income swings: keep a retainer or repeat client, "
        "spread big projects across months, and send invoices on a regular schedule."
    ),
    "Savings behaviour": (
        "Set up an automatic transfer on payday, even a small fixed amount. "
        "Saving every month counts as much as the amount you save."
    ),
    "Platform diversity & tenure": (
        "Earn from more than one client or platform so one loss does not hurt you. "
        "Tenure grows with time, so keep records of how long you have been earning."
    ),
    "Income trend": (
        "Raise your rates gradually, offer a higher-value service, or upsell "
        "existing clients so income grows instead of staying flat."
    ),
}


def validate_inputs(incomes: list[float], savings: list[float]) -> list[str]:
    """Return a list of problems with the entered numbers (empty list = valid)."""
    errors = []
    if any(x < 0 for x in incomes) or any(x < 0 for x in savings):
        errors.append("Income and savings cannot be negative.")
    for i, (inc, sav) in enumerate(zip(incomes, savings), start=1):
        if sav > inc:
            errors.append(f"Month {i}: savings are higher than income.")
    if sum(incomes) <= 0:
        errors.append("Enter income for at least one month.")
    return errors


def score_from_inputs(incomes, savings, platforms: int, tenure_months: int) -> dict:
    """Score one person from typed-in numbers (oldest month first)."""
    df = pd.DataFrame({
        "month": [f"M{i}" for i in range(1, len(incomes) + 1)],
        "income": list(incomes),
        "savings": list(savings),
        "platforms": platforms,
        "tenure_months": tenure_months,
    })
    return score_worker(df)


def improvement_tips(result: dict, limit: int = 2) -> list[tuple[str, float, str]]:
    """The weakest factors (below 80/100) with a practical tip for each."""
    weakest = sorted(result["factors"].items(), key=lambda kv: kv[1])
    return [(name, value, TIPS[name]) for name, value in weakest if value < 80][:limit]
