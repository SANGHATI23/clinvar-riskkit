# Benchmark Summary

- Dataset: `data/sample_clinvar.csv`
- Output: `outputs/isr_results.csv`
- Rows processed: 5
- Runtime (seconds): 0.1292
- Throughput (rows/sec): 38.7
- Python version: 3.13.5
- Platform: macOS-10.16-x86_64-i386-64bit-Mach-O
# Variant Interpretation Workbench

Interactive research prototype for uncertainty-aware clinical variant interpretation.

Features:
- ClinVar-inspired challenge dataset
- Evidence signal extraction
- Risk tier modeling
- Human interpretation interface
- Calibration scoring engine

Built with:
- Python
- Streamlit
- Pandas

Run locally:

streamlit run app.py
