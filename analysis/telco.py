import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from vizstyle import *

csv, out = sys.argv[1], sys.argv[2]
setup()
df = pd.read_csv(csv)
R = {"rows": len(df), "cols": df.shape[1]}
R["churn_counts"] = df["Churn"].value_counts().to_dict()
R["churn_rate"] = round((df["Churn"] == "Yes").mean() * 100, 1)
R["tenure_mean"] = df.groupby("Churn")["tenure"].mean().round(2).to_dict()
R["tenure_median"] = df.groupby("Churn")["tenure"].median().to_dict()
R["monthly_median"] = df.groupby("Churn")["MonthlyCharges"].median().round(2).to_dict()
R["blank_totalcharges"] = int(pd.to_numeric(df["TotalCharges"], errors="coerce").isna().sum())
yes = lambda s: (s == "Yes").mean() * 100
churners = df[df["Churn"] == "Yes"]
R["churner_share_tenure_le3"] = round((churners["tenure"] <= 3).mean() * 100, 1)
R["churner_share_month_to_month"] = round((churners["Contract"] == "Month-to-month").mean() * 100, 1)
R["internet_rate"] = df.groupby("InternetService")["Churn"].apply(yes).round(1).to_dict()
R["payment_rate"] = df.groupby("PaymentMethod")["Churn"].apply(yes).round(1).to_dict()

# 1. Churn rate by contract
rate = df.groupby("Contract")["Churn"].apply(yes).reindex(["Month-to-month", "One year", "Two year"])
cnt = df["Contract"].value_counts().reindex(rate.index)
R["contract_rate"] = rate.round(1).to_dict(); R["contract_n"] = cnt.to_dict()
fig, ax = plt.subplots(figsize=(8, 4.6))
b = ax.bar(rate.index, rate.values, width=0.5, color=[VERM, MUTED, MUTED], zorder=3)
for r, v, n in zip(b, rate.values, cnt.values):
    ax.text(r.get_x() + r.get_width()/2, v + 1.2, f"{v:.1f}%", ha="center", color=INK, fontweight="bold", fontsize=12)
ax.set_ylim(0, 50); ax.yaxis.set_major_formatter(PercentFormatter(decimals=0)); ax.grid(axis="x", visible=False)
ax.set_title("Churn rate by contract type"); ax.set_ylabel("Customers who churned")
ax.set_xticks(range(3), [f"{c}\n{n:,} customers" for c, n in zip(rate.index, cnt.values)])
save(fig, f"{out}/contract.webp")

# 2. Support services
fig, ax = plt.subplots(figsize=(8, 4.6))
cats = ["No", "Yes", "No internet service"]; labels = ["Doesn't have it", "Has it", "No internet"]
x = np.arange(len(cats)); w = 0.34
for i, (col, colr) in enumerate([("TechSupport", BLUE), ("OnlineSecurity", GREEN)]):
    r = df.groupby(col)["Churn"].apply(yes).reindex(cats)
    R[f"{col}_rate"] = r.round(1).to_dict()
    bars = ax.bar(x + (i - 0.5) * (w + 0.02), r.values, width=w, color=colr, zorder=3,
                  label="Tech support" if col == "TechSupport" else "Online security")
    for bb, v in zip(bars, r.values):
        ax.text(bb.get_x() + bb.get_width()/2, v + 1, f"{v:.0f}%", ha="center", color=INK, fontsize=10)
ax.set_xticks(x, labels); ax.set_ylim(0, 50); ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.grid(axis="x", visible=False); ax.legend(loc="upper right")
ax.set_title("Churn rate with and without support add-ons"); ax.set_ylabel("Customers who churned")
save(fig, f"{out}/support.webp")

# 3. Tenure distribution
fig, ax = plt.subplots(figsize=(8, 4.6))
bins = np.arange(0, 76, 4)
for lab, colr, name in [("No", BLUE, "Stayed"), ("Yes", VERM, "Churned")]:
    v = df.loc[df.Churn == lab, "tenure"]
    ax.hist(v, bins=bins, weights=np.ones(len(v)) / len(v) * 100, histtype="step", linewidth=2, color=colr, label=name, zorder=3)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
ax.set_xlabel("Tenure (months)"); ax.set_ylabel("Share of group")
ax.set_title("How long customers stayed before the snapshot")
ax.annotate(f"32% of churners left within\ntheir first 3 months (median tenure: {R['tenure_median']['Yes']:.0f})", xy=(4, 30), xytext=(14, 24), color=INK, fontsize=10, arrowprops=dict(arrowstyle="-", color=INK2, lw=1))
ax.legend(loc="upper right")
save(fig, f"{out}/tenure.webp")

# 4. Monthly charges box
fig, ax = plt.subplots(figsize=(8, 3.6))
data = [df.loc[df.Churn == "No", "MonthlyCharges"], df.loc[df.Churn == "Yes", "MonthlyCharges"]]
bp = ax.boxplot(data, vert=False, widths=0.45, patch_artist=True, tick_labels=["Stayed", "Churned"],
                medianprops=dict(color=INK, linewidth=2), whiskerprops=dict(color=INK2), capprops=dict(color=INK2))
for patch, c in zip(bp["boxes"], [BLUE, VERM]):
    patch.set_facecolor(c); patch.set_alpha(0.85); patch.set_edgecolor(c)
for i, d in enumerate(data):
    ax.text(d.median(), i + 1.32, f"median ${d.median():.0f}", ha="center", color=INK, fontsize=9)
ax.set_xlabel("Monthly charges ($)"); ax.grid(axis="y", visible=False)
ax.set_title("Monthly charges: churners pay more")
save(fig, f"{out}/charges.webp")

# ---- model, as in the original notebook ----
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df.dropna(inplace=True)
R["rows_after_clean"] = len(df)
y = df["Churn"].map({"Yes": 1, "No": 0})
X = pd.get_dummies(df.drop(["customerID", "Churn"], axis=1), drop_first=True)
R["features"] = X.shape[1]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(Xtr, ytr)
pred = rf.predict(Xte)
cm = confusion_matrix(yte, pred); R["cm"] = cm.tolist()
R["report"] = classification_report(yte, pred, output_dict=True)
R["auc"] = round(roc_auc_score(yte, rf.predict_proba(Xte)[:, 1]), 3)
print(classification_report(yte, pred))

# experiment: same forest with balanced class weights
rfb = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced", min_samples_leaf=5).fit(Xtr, ytr)
pb = rfb.predict(Xte)
R["balanced_cm"] = confusion_matrix(yte, pb).tolist()
R["balanced_report"] = classification_report(yte, pb, output_dict=True)
R["balanced_auc"] = round(roc_auc_score(yte, rfb.predict_proba(Xte)[:, 1]), 3)
print(classification_report(yte, pb))

def cmplot(cm, title, path, colr):
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    tot = cm.sum(axis=1, keepdims=True)
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("s", [SURFACE, colr])
    ax.imshow(cm / tot, cmap=cmap, vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            frac = cm[i, j] / tot[i, 0]
            ax.text(j, i, f"{cm[i,j]:,}\n{frac:.0%} of row", ha="center", va="center",
                    color="white" if frac > 0.55 else INK, fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1], ["Predicted stay", "Predicted churn"]); ax.set_yticks([0, 1], ["Actually stayed", "Actually churned"])
    ax.grid(False); [s.set_visible(False) for s in ax.spines.values()]
    ax.set_title(title, fontsize=12)
    save(fig, path)
cmplot(cm, "Baseline Random Forest (test set, n=1,407)", f"{out}/cm_baseline.webp", BLUE)
cmplot(np.array(R["balanced_cm"]), "With class_weight='balanced'", f"{out}/cm_balanced.webp", VERM)

# feature importance, top 10
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)[::-1]
R["importance"] = imp[::-1].round(4).to_dict()
nice = lambda s: s.replace("_", " = ").replace("InternetService", "Internet").replace("PaymentMethod", "Payment")
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.barh([nice(i) for i in imp.index], imp.values, color=[VERM if ("tenure" in i or "Contract" in i) else BLUE for i in imp.index], height=0.55, zorder=3)
for i, v in enumerate(imp.values): ax.text(v + 0.003, i, f"{v:.3f}", va="center", fontsize=9, color=INK2)
ax.grid(axis="y", visible=False); ax.set_xlabel("Mean decrease in impurity")
ax.set_title("What the model leans on (top 10 features)")
save(fig, f"{out}/importance.webp")

json.dump(R, open(f"{out}/results.json", "w"), indent=1, default=str)
