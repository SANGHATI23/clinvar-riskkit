import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

df = pd.read_csv("clinvar_reclassification_results.csv")

df = df.dropna(subset=["risk_score","reclassified"])

df["reclassified"] = df["reclassified"].astype(str).str.lower().map({
    "true":1,
    "false":0,
    "1":1,
    "0":0
})

df = df.dropna(subset=["reclassified"])
df["reclassified"] = df["reclassified"].astype(int)

y_true = df["reclassified"]
y_score = df["risk_score"]

fpr, tpr, thresholds = roc_curve(y_true, y_score)
roc_auc = auc(fpr, tpr)

print("AUC Score:", roc_auc)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
plt.plot([0,1],[0,1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ClinVar Reclassification ROC")
plt.legend(loc="lower right")

plt.savefig("clinvar_roc_curve.png")
plt.show()