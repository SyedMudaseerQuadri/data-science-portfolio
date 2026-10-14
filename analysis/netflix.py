import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from vizstyle import *

titles_csv, price_csv, out = sys.argv[1:4]
setup(); R = {}
n = pd.read_csv(titles_csv)
R["titles"] = len(n); R["types"] = n["type"].value_counts().to_dict()
R["missing"] = n.isnull().sum()[lambda s: s > 0].to_dict()
n["date_added"] = pd.to_datetime(n["date_added"].str.strip(), format="%B %d, %Y", errors="coerce")
n["year_added"] = n["date_added"].dt.year
R["added_range"] = [str(n.date_added.min().date()), str(n.date_added.max().date())]

# 1. titles added per year by type
g = n.dropna(subset=["year_added"]).groupby(["year_added", "type"]).size().unstack(fill_value=0).loc[2015:2021]
R["added_by_year"] = g.to_dict()
fig, ax = plt.subplots(figsize=(8, 4.6))
for t, c in [("Movie", BLUE), ("TV Show", VERM)]:
    ax.plot(g.index, g[t], color=c, linewidth=2, marker="o", markersize=7, markeredgecolor=SURFACE, markeredgewidth=2, zorder=3)
    ax.text(g.index[-1] + 0.12, g[t].iloc[-1], t + "s", color=INK, va="center", fontsize=10)
pk = g["Movie"].idxmax()
ax.annotate(f"Peak: {g.loc[pk,'Movie']:,} movies added in {pk:.0f}", xy=(pk, g.loc[pk, "Movie"]), xytext=(2015.2, g["Movie"].max() * 0.92), color=INK, fontsize=10)
ax.set_xlim(2014.7, 2021.9); ax.grid(axis="x", visible=False)
ax.set_title("Titles added to Netflix each year"); ax.set_ylabel("Titles added")
ax.text(2021, -0.13 * g.values.max(), "2021 data ends in September", ha="center", color=MUTED, fontsize=8.5)
save(fig, f"{out}/added.webp")

# 2. top genres
gen = n["listed_in"].str.split(", ").explode().value_counts().head(10)[::-1]
R["top_genres"] = gen[::-1].to_dict()
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.barh(gen.index, gen.values, color=BLUE, height=0.55, zorder=3)
for i, v in enumerate(gen.values): ax.text(v + 30, i, f"{v:,}", va="center", fontsize=9, color=INK2)
ax.grid(axis="y", visible=False); ax.set_xlabel("Titles tagged with the genre (a title can have up to 3)")
ax.set_title("Most common genre tags")
save(fig, f"{out}/genres.webp")

# 3. top countries
cty = n["country"].dropna().str.split(", ").explode().str.strip().replace("", np.nan).dropna().value_counts().head(10)[::-1]
R["top_countries"] = cty[::-1].to_dict()
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.barh(cty.index, cty.values, color=[VERM if c == "India" else BLUE for c in cty.index], height=0.55, zorder=3)
for i, v in enumerate(cty.values): ax.text(v + 30, i, f"{v:,}", va="center", fontsize=9, color=INK2)
ax.grid(axis="y", visible=False); ax.set_xlabel("Titles produced (co-productions count for each country)")
ax.set_title("Where Netflix titles come from")
save(fig, f"{out}/countries.webp")

# 4. movie runtime distribution
mv = n[n.type == "Movie"]["duration"].dropna().str.replace(" min", "").astype(int)
R["runtime_median"] = int(mv.median()); R["runtime_iqr"] = [int(mv.quantile(.25)), int(mv.quantile(.75))]
ts = n[n.type == "TV Show"]["duration"].dropna().str.extract(r"(\d+)")[0].astype(int)
R["tv_one_season_share"] = round((ts == 1).mean() * 100, 1)
R["top_ratings"] = n["rating"].value_counts().head(5).to_dict()

# ---- pricing (original notebook: Netflix, Disney+, Prime Video) ----
p = pd.read_csv(price_csv)
p["date"] = pd.to_datetime(p["date"], format="%b-%Y")
sel = ["Netflix", "Disney+", "Prime Video"]
fig, ax = plt.subplots(figsize=(8, 4.6))
for s, c in zip(sel, [VERM, BLUE, GREEN]):
    d = p[p.service == s].sort_values("date")
    ax.step(d["date"], d["price"], where="post", color=c, linewidth=2, zorder=3)
    ax.text(d["date"].iloc[-1] + pd.Timedelta(days=60), d["price"].iloc[-1], f"{s}  \${d['price'].iloc[-1]:.2f}", color=INK, va="center", fontsize=10)
    ch = d[d["price"].diff() != 0]
    ax.plot(ch["date"], ch["price"], "o", color=c, markersize=7, markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)
ax.set_xlim(pd.Timestamp("2011-01-01"), pd.Timestamp("2025-09-01")); ax.set_ylim(0, 18)
ax.yaxis.set_major_formatter(lambda v, _: f"\${v:.0f}"); ax.grid(axis="x", visible=False)
ax.set_title("Monthly plan price over time (dots mark each price change)"); ax.set_ylabel("Price (USD / month)")
save(fig, f"{out}/prices.webp")

# 5. % increase since launch in dataset, all services
rows = []
for s, d in p.sort_values("date").groupby("service"):
    a, b = d["price"].iloc[0], d["price"].iloc[-1]
    rows.append((s, a, b, (b / a - 1) * 100, d["date"].iloc[0].year, int((d["price"].diff() > 0).sum())))
inc = pd.DataFrame(rows, columns=["service", "start", "end", "pct", "since", "hikes"]).sort_values("pct")
R["price_change"] = inc.round(2).to_dict("records")

# every price hike, with the size of the jump
hikes = []
for s, d in p.sort_values("date").groupby("service"):
    d = d.assign(prev=d["price"].shift())
    for _, h in d[d["price"] > d["prev"]].iterrows():
        hikes.append({"service": s, "date": h["date"].strftime("%Y-%m"), "from": h["prev"], "to": h["price"]})
R["hikes"] = hikes
R["hikes_total"] = len(hikes)
R["hikes_since_2022"] = sum(h["date"] >= "2022-01" for h in hikes)
nf = [h for h in hikes if h["service"] == "Netflix"]
R["netflix_flat_months_before_first_hike"] = (pd.Timestamp(nf[0]["date"]) - p[p.service == "Netflix"]["date"].min()).days // 30
R["netflix_pct_2019_to_end"] = round((nf[-1]["to"] / nf[0]["to"] - 1) * 100, 1)
R["netflix_biggest_jump"] = max(nf, key=lambda h: h["to"] - h["from"])
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.barh([f"{s} (since {y})" for s, y in zip(inc.service, inc.since)], inc.pct, color=[VERM if v >= 90 else MUTED for v in inc.pct], height=0.55, zorder=3)
for i, (v, a, b) in enumerate(zip(inc.pct, inc.start, inc.end)):
    ax.text(v + 2, i, f"+{v:.0f}%   \${a:.2f} → \${b:.2f}", va="center", fontsize=9, color=INK2)
ax.set_xlim(0, 135); ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%"); ax.grid(axis="y", visible=False)
ax.set_title("Total price increase, first record to Jan 2024")
save(fig, f"{out}/increase.webp")

json.dump(R, open(f"{out}/results.json", "w"), indent=1, default=str)
