import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("clinvar_predictive_base_clean.csv")

df["ClinicalSignificance_old"] = df["ClinicalSignificance_old"].astype(str).str.lower()

df["is_conflicting"] = df["ClinicalSignificance_old"].str.contains("conflict").astype(int)

rates = df.groupby("is_conflicting")["reclassified"].mean()

print(rates)

plt.figure()
rates.plot(kind="bar")
plt.title("Reclassification Rate: Conflicting vs Non-Conflicting Variants")
plt.ylabel("Reclassification Rate")
plt.xticks([0,1], ["Non-conflicting", "Conflicting"], rotation=0)

plt.savefig("reclassification_conflict_plot.png")
plt.show()
