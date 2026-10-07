import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from generate_data import DATA_PATH, generate_data
from scoring import SCORE_MAX, SCORE_MIN, WEIGHTS, explain, score_worker

st.set_page_config(page_title="Invisible Credit Score", page_icon="💳", layout="wide")

BAND_COLORS = {
    "Low risk": "#2e9e5b",
    "Moderate risk": "#d4a017",
    "Elevated risk": "#e07b39",
    "High risk": "#c0392b",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return generate_data()
    return pd.read_csv(DATA_PATH)


def gauge(score: int, band: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis": {"range": [SCORE_MIN, SCORE_MAX]},
            "bar": {"color": BAND_COLORS[band]},
            "steps": [
                {"range": [300, 550], "color": "rgba(192,57,43,0.15)"},
                {"range": [550, 650], "color": "rgba(224,123,57,0.15)"},
                {"range": [650, 750], "color": "rgba(212,160,23,0.15)"},
                {"range": [750, 900], "color": "rgba(46,158,91,0.15)"},
            ],
        },
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=10))
    return fig


df = load_data()
results = {name: score_worker(group) for name, group in df.groupby("worker")}

st.title("💳 The Invisible Credit Score")
st.caption(
    "An explainable, alternative credit score for gig workers and freelancers, "
    "built from income stability, savings habits, and track record "
    "instead of a traditional credit history."
)
st.info(
    "**Prototype notice:** all data here is synthetic (randomly generated). "
    "No real people, platforms, or financial records are used."
)

tab_profile, tab_compare, tab_how = st.tabs(["Worker profile", "Compare workers", "How it works"])

# ---------- Tab 1: single worker ----------
with tab_profile:
    name = st.selectbox("Choose a gig worker", sorted(results))
    res = results[name]
    worker_df = df[df["worker"] == name].sort_values("month")

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(gauge(res["score"], res["band"]))
        st.markdown(f"### {res['band']}")
        st.metric("Average monthly income", f"₹{worker_df['income'].mean():,.0f}")
        st.metric("Total saved (6 months)", f"₹{worker_df['savings'].sum():,.0f}")
    with right:
        st.subheader("Why this score?")
        for line in explain(res):
            st.markdown(f"- {line}")
        pts = pd.Series(res["points"]).sort_values()
        fig = go.Figure(go.Bar(x=pts.values, y=pts.index, orientation="h"))
        fig.update_layout(
            title=f"Points added above the base of {SCORE_MIN}",
            height=260, margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig)

    st.subheader("Income and savings by month")
    fig = go.Figure()
    fig.add_bar(x=worker_df["month"], y=worker_df["income"], name="Income")
    fig.add_bar(x=worker_df["month"], y=worker_df["savings"], name="Savings")
    fig.update_layout(barmode="group", height=320, yaxis_title="₹")
    st.plotly_chart(fig)

# ---------- Tab 2: comparison ----------
with tab_compare:
    st.subheader("All workers side by side")
    table = pd.DataFrame(
        {
            n: {"Score": r["score"], "Risk band": r["band"],
                **{k: round(v) for k, v in r["factors"].items()}}
            for n, r in results.items()
        }
    ).T.sort_values("Score", ascending=False)
    st.dataframe(table)

    ranked = table["Score"].sort_values()
    fig = go.Figure(go.Bar(
        x=ranked.values, y=ranked.index, orientation="h",
        marker_color=[BAND_COLORS[results[n]["band"]] for n in ranked.index],
    ))
    fig.update_layout(height=320, xaxis=dict(range=[SCORE_MIN, SCORE_MAX]))
    st.plotly_chart(fig)
    st.caption(
        "Notice that a worker with high but unstable income can score lower than "
        "a lower earner who is steady and saves regularly. That is the point."
    )

# ---------- Tab 3: methodology ----------
with tab_how:
    st.subheader("Scoring method")
    st.markdown(
        f"Each factor is scored from 0 to 100, multiplied by its weight, and scaled "
        f"onto a **{SCORE_MIN}-{SCORE_MAX}** range."
    )
    st.table(pd.DataFrame({
        "Factor": list(WEIGHTS),
        "Weight": [f"{w:.0%}" for w in WEIGHTS.values()],
        "What it measures": [
            "Month-to-month income variation (lower variation scores higher)",
            "Savings rate and how regularly the worker saves",
            "Number of platforms and months of history",
            "Whether income is rising or falling",
        ],
    }))
    st.markdown("#### Limitations")
    st.markdown(
        "- Uses synthetic data; a real system needs consented access to real accounts.\n"
        "- Weights are hand-picked, not learned. They would need validating against "
        "real repayment outcomes.\n"
        "- Six months is a short window, and any scoring system needs a fairness audit "
        "before real use."
    )
