import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report

print("Loading cleaned dataset...", flush=True)

df = pd.read_csv("clinvar_predictive_base_clean.csv")

print("Initial shape:", df.shape, flush=True)

# --------------------------
# Feature Engineering
# --------------------------

print("Creating features...", flush=True)

# ReviewStatus → numeric proxy
df["review_score"] = df["ReviewStatus_old"].astype(str).str.len()

# Clinical significance encoding (simple)
df["cs_encoded"] = df["ClinicalSignificance_old"].astype(str).str.len()

# Drop rows with missing values
df = df.dropna(subset=["review_score", "cs_encoded", "reclassified"])

print("Final shape after cleaning:", df.shape, flush=True)

# --------------------------
# Features & Target
# --------------------------

X = df[["review_score", "cs_encoded"]]
y = df["reclassified"]

# --------------------------
# Train/Test Split
# --------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------
# Model
# --------------------------

print("Training model...", flush=True)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# --------------------------
# Evaluation
# --------------------------

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

auc = roc_auc_score(y_test, y_prob)

print("\nModel Evaluation:", flush=True)
print("AUC:", auc, flush=True)

print("\nClassification Report:", flush=True)
print(classification_report(y_test, y_pred), flush=True)