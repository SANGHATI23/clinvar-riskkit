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
    import json
import os
import sys
import time
import platform
from pathlib import Path

from clinvar_riskkit.io import load_clinvar
from clinvar_riskkit.signals import derive_signals
from clinvar_riskkit.scoring import compute_isr_score


def run_pipeline(input_path, output_path):
    print("[1/6] Loading ClinVar data")
    df = load_clinvar(input_path)

    print("[2/6] Deriving signals")
    signals_df = derive_signals(df)

    print("[3/6] Computing risk scores")
    scored_df = compute_isr_score(signals_df)

    print("[4/6] Writing output CSV")
    scored_df.to_csv(output_path, index=False)

    return scored_df


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m clinvar_riskkit.bench <input_csv> <output_csv>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    benchmark_dir = Path("benchmarks")
    benchmark_dir.mkdir(exist_ok=True)

    start = time.perf_counter()
    scored_df = run_pipeline(input_path, output_path)
    end = time.perf_counter()

    runtime_seconds = round(end - start, 4)
    row_count = len(scored_df)
    throughput = round(row_count / runtime_seconds, 2) if runtime_seconds > 0 else 0

    benchmark_data = {
        "dataset_path": input_path,
        "output_path": output_path,
        "rows_processed": row_count,
        "runtime_seconds": runtime_seconds,
        "throughput_rows_per_second": throughput,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }

    with open(benchmark_dir / "latest.json", "w") as f:
        json.dump(benchmark_data, f, indent=2)

    with open(benchmark_dir / "latest.md", "w") as f:
        f.write("# Benchmark Summary\n\n")
        f.write(f"- Dataset: `{input_path}`\n")
        f.write(f"- Output: `{output_path}`\n")
        f.write(f"- Rows processed: {row_count}\n")
        f.write(f"- Runtime (seconds): {runtime_seconds}\n")
        f.write(f"- Throughput (rows/sec): {throughput}\n")
        f.write(f"- Python version: {platform.python_version()}\n")
        f.write(f"- Platform: {platform.platform()}\n")

    print("[5/6] Writing benchmark artifacts")
    print(f"Runtime: {runtime_seconds} seconds")
    print(f"Rows processed: {row_count}")
    print(f"Throughput: {throughput} rows/sec")
    print("[6/6] Benchmark complete")


if __name__ == "__main__":
    main()