import pandas as pd
import matplotlib.pyplot as plt

FILE_2019 = "clinvar_data/variant_summary_2019-01.txt"
FILE_2024 = "clinvar_data/variant_summary.txt"

cols = [
    "VariationID",
    "GeneSymbol",
    "Name",
    "ClinicalSignificance",
    "ReviewStatus",
    "NumberSubmitters",
    "LastEvaluated"
]

valid_labels = {
    "Pathogenic",
    "Likely pathogenic",
    "Uncertain significance",
    "Likely benign",
    "Benign"
}

print("Loading 2019...")
df19 = pd.read_csv(FILE_2019, sep="\t", usecols=cols, low_memory=False)
df19 = df19[df19["ClinicalSignificance"].isin(valid_labels)].copy()
print("Filtered 2019 rows:", len(df19))

print("Loading current in chunks...")
chunks = []
for i, chunk in enumerate(pd.read_csv(FILE_2024, sep="\t", usecols=cols, chunksize=200000, low_memory=False)):
    chunk = chunk[chunk["ClinicalSignificance"].isin(valid_labels)]
    chunks.append(chunk)
    if (i + 1) % 5 == 0:
        print(f"Processed {(i + 1) * 200000:,} rows...")

df24 = pd.concat(chunks, ignore_index=True)
print("Filtered current rows:", len(df24))

df19["LastEvaluated"] = pd.to_datetime(df19["LastEvaluated"], errors="coerce")
baseline_date = pd.Timestamp("2019-01-01")
df19["review_age_years"] = (baseline_date - df19["LastEvaluated"]).dt.days / 365.25
df19["review_age_years"] = df19["review_age_years"].fillna(0).clip(lower=0)

df19["has_conflict"] = df19["ReviewStatus"].fillna("").str.contains("conflict", case=False).astype(int)

def review_strength(status):
    s = str(status).lower()
    if "practice guideline" in s:
        return 4
    elif "reviewed by expert panel" in s:
        return 3
    elif "criteria provided, multiple submitters, no conflicts" in s:
        return 2
    elif "criteria provided, single submitter" in s:
        return 1
    else:
        return 0

df19["review_strength"] = df19["ReviewStatus"].apply(review_strength)
df19["NumberSubmitters"] = pd.to_numeric(df19["NumberSubmitters"], errors="coerce").fillna(0)

df19["risk_score"] = (
    1.5 * df19["has_conflict"] +
    0.8 * df19["review_age_years"] +
    1.0 * (2 - df19["review_strength"]).clip(lower=0) +
    0.3 * (1 / (df19["NumberSubmitters"] + 1))
)

q1 = df19["risk_score"].quantile(0.33)
q2 = df19["risk_score"].quantile(0.66)

def risk_tier(x):
    if x <= q1:
        return "Low"
    elif x <= q2:
        return "Medium"
    else:
        return "High"

df19["risk_tier"] = df19["risk_score"].apply(risk_tier)

merged = df19.merge(
    df24[["VariationID", "ClinicalSignificance"]],
    on="VariationID",
    how="inner",
    suffixes=("_2019", "_2024")
)

print("Matched variants:", len(merged))

merged["reclassified"] = (
    merged["ClinicalSignificance_2019"] != merged["ClinicalSignificance_2024"]
)

summary = merged.groupby("risk_tier").agg(
    total_variants=("VariationID", "count"),
    reclassified_count=("reclassified", "sum"),
    reclassification_rate=("reclassified", "mean")
).reset_index()

summary["reclassification_rate"] = summary["reclassification_rate"] * 100

print("\n=== Reclassification by Risk Tier ===")
print(summary)

merged.to_csv("clinvar_reclassification_results.csv", index=False)
summary.to_csv("clinvar_reclassification_summary.csv", index=False)

order = ["Low", "Medium", "High"]
summary["risk_tier"] = pd.Categorical(summary["risk_tier"], categories=order, ordered=True)
summary = summary.sort_values("risk_tier")

plt.figure(figsize=(8, 5))
plt.bar(summary["risk_tier"], summary["reclassification_rate"])
plt.title("ClinVar Reclassification Rate by Risk Tier")
plt.xlabel("Risk Tier")
plt.ylabel("Reclassification Rate (%)")
plt.tight_layout()
plt.savefig("clinvar_reclassification_plot.png", dpi=200)

print("\nSaved files:")
print("- clinvar_reclassification_results.csv")
print("- clinvar_reclassification_summary.csv")
print("- clinvar_reclassification_plot.png")