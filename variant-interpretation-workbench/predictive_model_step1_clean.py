import pandas as pd
import time

start = time.time()

needed_cols = ["VariationID", "ClinicalSignificance", "ReviewStatus", "LastEvaluated"]

print("Loading 2019...", flush=True)
df_old = pd.read_csv(
    "data/variant_summary_2019.txt",
    sep="\t",
    usecols=needed_cols,
    dtype=str,
    low_memory=True
)

print("Loading 2024 in chunks...", flush=True)
chunks = []
for i, chunk in enumerate(pd.read_csv(
    "data/variant_summary_2024.txt",
    sep="\t",
    usecols=needed_cols,
    dtype=str,
    chunksize=200000,
    low_memory=True
)):
    print(f"Read chunk {i+1}", flush=True)
    chunks.append(chunk)

df_new = pd.concat(chunks, ignore_index=True)

print("Dropping null VariationID...", flush=True)
df_old = df_old.dropna(subset=["VariationID"])
df_new = df_new.dropna(subset=["VariationID"])

print("Deduplicating by VariationID...", flush=True)
df_old = df_old.drop_duplicates(subset=["VariationID"], keep="first")
df_new = df_new.drop_duplicates(subset=["VariationID"], keep="first")

print("2019 unique rows:", df_old.shape, flush=True)
print("2024 unique rows:", df_new.shape, flush=True)

df_old = df_old.rename(columns={
    "ClinicalSignificance": "ClinicalSignificance_old",
    "ReviewStatus": "ReviewStatus_old",
    "LastEvaluated": "LastEvaluated_old"
})

df_new = df_new.rename(columns={
    "ClinicalSignificance": "ClinicalSignificance_new",
    "ReviewStatus": "ReviewStatus_new",
    "LastEvaluated": "LastEvaluated_new"
})

print("Merging...", flush=True)
df_merged = df_old.merge(df_new, on="VariationID", how="inner")

print("Merged shape:", df_merged.shape, flush=True)

print("Creating target...", flush=True)
df_merged["reclassified"] = (
    df_merged["ClinicalSignificance_old"] != df_merged["ClinicalSignificance_new"]
).astype(int)

print(df_merged["reclassified"].value_counts(dropna=False), flush=True)

print("Saving cleaned file...", flush=True)
df_merged.to_csv("clinvar_predictive_base_clean.csv", index=False)

print(f"Done in {time.time() - start:.2f} seconds", flush=True)
