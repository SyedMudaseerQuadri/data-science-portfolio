# Analysis scripts behind the case studies

These scripts re-run the two data projects and produce every chart on the case-study pages
(`assets/telco/*.webp`, `assets/netflix/*.webp`) plus the numbers quoted there (`*_results.json`).

| Script | Source project | Data |
| --- | --- | --- |
| `telco.py` | [telco-churn-project](https://github.com/SyedMudaseerQuadri/telco-churn-project) | IBM Telco Customer Churn, 7,043 rows ([CSV](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv)) |
| `netflix.py` | [Netflix_Tvshows-_prediction](https://github.com/SyedMudaseerQuadri/Netflix_Tvshows-_prediction) + [Streaming_princing_prediction](https://github.com/SyedMudaseerQuadri/Streaming_princing_prediction) | `netflix_titles.csv` (8,807 titles) and `streaming_service.csv` (777 monthly prices) from those repos |

The model in `telco.py` follows the original notebook step for step (numeric `TotalCharges`,
drop blanks, one-hot with `drop_first`, 80/20 split, `RandomForestClassifier(n_estimators=100, random_state=42)`)
and reproduces its confusion matrix exactly: `[[927, 106], [196, 178]]`.

```bash
pip install pandas numpy scikit-learn matplotlib pillow
python telco.py   Telco-Customer-Churn.csv  ../assets/telco
python netflix.py netflix_titles.csv streaming_service.csv ../assets/netflix
```
