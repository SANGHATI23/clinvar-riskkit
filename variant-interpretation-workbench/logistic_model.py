import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# Load dataset
df = pd.read_csv("clinvar_reclassification_results.csv")

print("\nColumns in file:")
print(df.columns.tolist())

# Convert label
df["reclassified"] = df["reclassified"].astype(str).str.lower().map({
    "true": 1,
    "false": 0,
    "1": 1,
    "0": 0
})

df = df.dropna(subset=["reclassified"]).copy()
df["reclassified"] = df["reclassified"].astype(int)

# CHANGE THESE after checking the printed columns
candidate_features = [
    "risk_score"
]

# Keep only features that actually exist
features = [c for c in candidate_features if c in df.columns]

if not features:
    raise ValueError("No matching feature columns found. Check printed column names above.")

# Drop missing rows only for needed columns
df = df.dropna(subset=features + ["reclassified"]).copy()

X = df[features]
y = df["reclassified"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

preds = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, preds)

print("\nFeatures used:", features)
print("Logistic Regression AUC:", auc)

importance = pd.DataFrame({
    "feature": features,
    "coefficient": model.coef_[0]
})

print("\nFeature Importance:")
print(importance.sort_values("coefficient", ascending=False))