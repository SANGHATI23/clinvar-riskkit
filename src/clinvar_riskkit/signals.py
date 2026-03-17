import pandas as pd


def derive_conflict_signal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify variants with conflicting interpretations.

    Parameters
    ----------
    df : pd.DataFrame
        ClinVar dataframe

    Returns
    -------
    pd.DataFrame
        DataFrame with conflict flag column
    """

    df = df.copy()

    if "ClinicalSignificance" in df.columns:
        df["has_conflict"] = df["ClinicalSignificance"].str.contains(
            "conflict", case=False, na=False
        )
    else:
        df["has_conflict"] = False

    return df
from datetime import datetime


def derive_staleness_signal(df):
    """
    Compute years since last evaluation.

    Variants not evaluated recently are more likely to be unstable.
    """

    df = df.copy()

    if "DateLastEvaluated" in df.columns:
        df["DateLastEvaluated"] = pd.to_datetime(
            df["DateLastEvaluated"], errors="coerce"
        )

        current_year = datetime.now().year

        df["years_since_eval"] = current_year - df["DateLastEvaluated"].dt.year

    else:
        df["years_since_eval"] = None

    return df