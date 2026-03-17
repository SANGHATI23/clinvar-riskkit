import pandas as pd


def load_clinvar(path: str) -> pd.DataFrame:
    """
    Load a ClinVar-style TSV or CSV file.

    Parameters
    ----------
    path : str
        Path to the ClinVar dataset file.

    Returns
    -------
    pd.DataFrame
        Loaded dataframe.
    """

    if path.endswith(".tsv"):
        df = pd.read_csv(path, sep="\t")
    else:
        df = pd.read_csv(path)

    return df