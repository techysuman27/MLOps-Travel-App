# Verification ledger

This file separates implementation from execution evidence. Update entries only after a successful check; a configuration file alone is not deployment proof.

| Component | Current evidence | Status |
|---|---|---|
| Source data | Contract validation passed; SHA-256 fingerprints in reports/source_validation.json | Verified locally |
| Three trained models | Saved joblib bundles and evaluation reports; MLflow run IDs in models/*.json | Verified locally |
| Modeling notebooks | All three execute without cell errors; 16 embedded charts verified in each notebook | Verified locally |
| Automated tests | 13 tests passed | Verified locally |
| Flask HTTP service | Readiness, prediction, invalid input and recommendation smoke checks passed | Verified locally |
| Streamlit | All four public pages checked; flight prediction (718.75), three hotel suggestions, insights and classification probabilities displayed | Public flows verified |
| Docker images | Corrected API image passes readiness, flight prediction, invalid input and hotel smoke checks; API uses about 143 MiB locally | API verified; UI image built |
| Kubernetes | Two replicas rolled out, API smoke passed, manually scaled to three Ready replicas; docs/evidence/kubernetes-rollout.txt | Local rollout and manual scaling verified |
| Airflow | Parse-safe DAG and Compose service written | Pending runtime verification |
| Jenkins | Pipeline stages and real smoke checks written | Pending Jenkins execution |
| MLflow UI | Experiments persisted in local SQLite; flight/classification pipelines registered as version 1 | UI screenshots pending |
| Monitoring | Historical drift report; 200/200 successful requests with 8 workers, p50 693 ms and p95 1183 ms | Verified locally; not a capacity guarantee |
| GitHub | main published to techysuman27/MLOps-Travel-App, including all three executed notebooks and model bundles | Published |
| Public hosting | Render free API and Streamlit Community Cloud deployed; public API readiness/prediction/validation/recommendation smoke checks passed | Verified publicly |
| Google Docs/Drive | Local documentation and notebooks prepared | Upload/sharing pending |
| Video | Outline prepared; no recording claimed | Student recording pending |

No friend's code, model artifacts or write-ups were used in this implementation. The source review informed design decisions only.

Public application: https://voyage-analytics-suman.streamlit.app/  
Public readiness: https://voyage-analytics-api-kqju.onrender.com/health/ready  
Public smoke verification: 2026-10-11. Free-host cold starts are expected; local Kubernetes is a separate scaling demonstration.

The load test used `kubectl port-forward service/voyage-api`, which forwards to one selected pod. It verifies concurrent inference reliability, not Service traffic balancing or throughput improvement from additional replicas. HPA automatic scaling is not yet verified.
