import pandas as pd


def compute_basic_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a simple instability risk score.

    Current signals used:
    - conflict in interpretation

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    df = df.copy()

    score = 0

    if "has_conflict" in df.columns:
        df["conflict_score"] = df["has_conflict"].astype(int)
    else:
        df["conflict_score"] = 0

    df["risk_score"] = df["conflict_score"]

    return df
def compute_isr_score(df):
    """
    Compute Interpretation Stability Risk (ISR) score.

    Signals used:
    - conflict
    - staleness
    - review confidence
    """

    df = df.copy()

    # conflict contribution
    if "has_conflict" in df.columns:
        df["conflict_score"] = df["has_conflict"].astype(int)
    else:
        df["conflict_score"] = 0

    # staleness contribution (older = higher risk)
    if "years_since_eval" in df.columns:
        df["staleness_score"] = df["years_since_eval"].fillna(0) / 10
    else:
        df["staleness_score"] = 0

    # review confidence contribution (lower stars = higher risk)
    if "review_score" in df.columns:
        df["review_risk"] = 4 - df["review_score"]
    else:
        df["review_risk"] = 0

    df["ISR_score"] = (
        df["conflict_score"]
        + df["staleness_score"]
        + df["review_risk"]
    )

    return df