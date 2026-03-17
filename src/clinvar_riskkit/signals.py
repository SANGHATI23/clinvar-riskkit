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
def derive_review_signal(df):
    """
    Convert ClinVar review status to a numeric confidence score.
    """

    df = df.copy()

    if "ReviewStatus" in df.columns:

        review_map = {
            "practice guideline": 4,
            "reviewed by expert panel": 3,
            "criteria provided, multiple submitters, no conflicts": 2,
            "criteria provided, single submitter": 1,
            "no assertion criteria provided": 0,
        }

        df["review_score"] = (
            df["ReviewStatus"]
            .str.lower()
            .map(review_map)
            .fillna(0)
        )

    else:
        df["review_score"] = 0

    return df
def derive_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all signal derivation steps in sequence.
    """
    df = derive_conflict_signal(df)
    df = derive_staleness_signal(df)
    df = derive_review_signal(df)
    return df