import pandas as pd
import time

start = time.time()

needed_cols = ["VariationID", "ClinicalSignificance", "ReviewStatus", "LastEvaluated"]

print("Loading 2019 file...", flush=True)
df_old = pd.read_csv(
    "data/variant_summary_2019.txt",
    sep="\t",
    usecols=needed_cols,
    dtype=str,
    low_memory=True
)

df_old = df_old.rename(columns={
    "ClinicalSignificance": "ClinicalSignificance_old",
    "ReviewStatus": "ReviewStatus_old",
    "LastEvaluated": "LastEvaluated_old"
})

print("2019 loaded:", df_old.shape, flush=True)

print("Loading 2024 file in chunks...", flush=True)
chunks = []
chunk_size = 200000

for i, chunk in enumerate(pd.read_csv(
    "data/variant_summary_2024.txt",
    sep="\t",
    usecols=needed_cols,
    dtype=str,
    chunksize=chunk_size,
    low_memory=True
)):
    print(f"Read chunk {i+1}", flush=True)
    chunks.append(chunk)

df_new = pd.concat(chunks, ignore_index=True)

df_new = df_new.rename(columns={
    "ClinicalSignificance": "ClinicalSignificance_new",
    "ReviewStatus": "ReviewStatus_new",
    "LastEvaluated": "LastEvaluated_new"
})

print("2024 loaded:", df_new.shape, flush=True)

print("Merging...", flush=True)
df_merged = df_old.merge(df_new, on="VariationID", how="inner")

print("Creating target variable...", flush=True)
df_merged["reclassified"] = (
    df_merged["ClinicalSignificance_old"] != df_merged["ClinicalSignificance_new"]
).astype(int)

print(df_merged[
    ["VariationID", "ClinicalSignificance_old", "ClinicalSignificance_new", "reclassified"]
].head(), flush=True)

print(df_merged["reclassified"].value_counts(), flush=True)

print("Saving...", flush=True)
df_merged.to_csv("clinvar_predictive_base.csv", index=False)

print(f"Done in {time.time() - start:.2f} seconds", flush=True)