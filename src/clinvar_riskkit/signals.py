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