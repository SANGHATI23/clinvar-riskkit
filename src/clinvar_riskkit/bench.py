import os
import sys

from clinvar_riskkit.io import load_clinvar
from clinvar_riskkit.signals import (
    derive_conflict_signal,
    derive_staleness_signal,
    derive_review_signal,
)
from clinvar_riskkit.scoring import compute_isr_score


def run_pipeline(input_path: str, output_path: str) -> None:
    df = load_clinvar(input_path)
    df = derive_conflict_signal(df)
    df = derive_staleness_signal(df)
    df = derive_review_signal(df)
    df = compute_isr_score(df)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved results to: {output_path}")


if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    run_pipeline(input_path, output_path)