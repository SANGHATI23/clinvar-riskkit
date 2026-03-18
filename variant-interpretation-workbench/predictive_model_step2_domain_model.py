import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    classification_report,
    confusion_matrix
)

print("Loading cleaned dataset...", flush=True)
df = pd.read_csv("clinvar_predictive_base_clean.csv")

print("Initial shape:", df.shape, flush=True)

# --------------------------------------------------
# Basic cleanup
# --------------------------------------------------
needed = [
    "VariationID",
    "ClinicalSignificance_old",
    "ReviewStatus_old",
    "LastEvaluated_old",
    "reclassified"
]

df = df[needed].copy()
df = df.dropna(subset=["ClinicalSignificance_old", "ReviewStatus_old", "reclassified"])

# Standardize strings
df["ClinicalSignificance_old"] = df["ClinicalSignificance_old"].astype(str).str.strip().str.lower()
df["ReviewStatus_old"] = df["ReviewStatus_old"].astype(str).str.strip().str.lower()
df["LastEvaluated_old"] = df["LastEvaluated_old"].astype(str).str.strip()

print("After cleanup:", df.shape, flush=True)

# --------------------------------------------------
# Domain Feature Engineering
# --------------------------------------------------
print("Creating domain-aware features...", flush=True)

# 1) Review status score (higher = stronger review confidence)
def map_review_status(text):
    text = str(text).lower()

    if "practice guideline" in text:
        return 5
    elif "reviewed by expert panel" in text:
        return 4
    elif "multiple submitters" in text and "no conflicts" in text:
        return 3
    elif "multiple submitters" in text and "conflicts" in text:
        return 2
    elif "single submitter" in text:
        return 1
    elif "no assertion" in text:
        return 0
    else:
        return 0

df["review_score"] = df["ReviewStatus_old"].apply(map_review_status)

# 2) Clinical significance domain flags
cs = df["ClinicalSignificance_old"]

df["is_pathogenic"] = cs.str.contains("pathogenic", na=False).astype(int)
df["is_likely_pathogenic"] = cs.str.contains("likely pathogenic", na=False).astype(int)
df["is_benign"] = cs.str.contains("benign", na=False).astype(int)
df["is_likely_benign"] = cs.str.contains("likely benign", na=False).astype(int)
df["is_vus"] = cs.str.contains("uncertain significance", na=False).astype(int)
df["is_conflicting"] = cs.str.contains("conflict", na=False).astype(int)

# 3) Last evaluated recency feature
# We measure how old the evaluation was as of a fixed reference date near the old snapshot.
reference_date = pd.Timestamp("2019-01-31")
df["LastEvaluated_old_dt"] = pd.to_datetime(df["LastEvaluated_old"], errors="coerce")
df["days_since_last_eval"] = (reference_date - df["LastEvaluated_old_dt"]).dt.days

# Handle missing/negative values safely
df["days_since_last_eval"] = df["days_since_last_eval"].fillna(df["days_since_last_eval"].median())
df["days_since_last_eval"] = df["days_since_last_eval"].clip(lower=0)

# 4) Optional simple ISR-like proxy based on instability factors
# This is not yet your final ISR, but gives a domain-informed composite feature.
df["instability_score"] = (
    (5 - df["review_score"]) * 2
    + df["is_conflicting"] * 3
    + df["is_vus"] * 2
    + (df["days_since_last_eval"] > 365 * 3).astype(int) * 1
)

# --------------------------------------------------
# Final feature matrix
# --------------------------------------------------
feature_cols = [
    "review_score",
    "is_pathogenic",
    "is_likely_pathogenic",
    "is_benign",
    "is_likely_benign",
    "is_vus",
    "is_conflicting",
    "days_since_last_eval",
    "instability_score"
]

X = df[feature_cols].copy()
y = df["reclassified"].astype(int)

print("Feature preview:", flush=True)
print(X.head(), flush=True)

print("Target distribution:", flush=True)
print(y.value_counts(dropna=False), flush=True)

# --------------------------------------------------
# Train/test split
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Train shape:", X_train.shape, flush=True)
print("Test shape:", X_test.shape, flush=True)

# --------------------------------------------------
# Model
# --------------------------------------------------
print("Training logistic regression...", flush=True)

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# --------------------------------------------------
# Evaluation
# --------------------------------------------------
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)

print("\n=== MODEL EVALUATION ===", flush=True)
print(f"AUC: {auc:.4f}", flush=True)

print("\nClassification Report:", flush=True)
print(classification_report(y_test, y_pred), flush=True)

print("Confusion Matrix:", flush=True)
print(confusion_matrix(y_test, y_pred), flush=True)

# --------------------------------------------------
# Feature importance (logistic coefficients)
# --------------------------------------------------
coef_df = pd.DataFrame({
    "feature": feature_cols,
    "coefficient": model.coef_[0]
}).sort_values("coefficient", ascending=False)

print("\n=== FEATURE EFFECTS (Logistic Coefficients) ===", flush=True)
print(coef_df, flush=True)

coef_df.to_csv("domain_model_feature_coefficients.csv", index=False)

# Save scored test predictions
test_results = X_test.copy()
test_results["actual_reclassified"] = y_test.values
test_results["predicted_label"] = y_pred
test_results["predicted_probability"] = y_prob
test_results.to_csv("domain_model_test_predictions.csv", index=False)

print("\nSaved outputs:", flush=True)
print("- domain_model_feature_coefficients.csv", flush=True)
print("- domain_model_test_predictions.csv", flush=True)
