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