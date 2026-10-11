# Verification ledger

This file separates implementation from execution evidence. Update entries only after a successful check; a configuration file alone is not deployment proof.

| Component | Current evidence | Status |
|---|---|---|
| Source data | Contract validation passed; SHA-256 fingerprints in reports/source_validation.json | Verified locally |
| Three trained models | Saved joblib bundles and evaluation reports; MLflow run IDs in models/*.json | Verified locally |
| Modeling notebooks | All three execute without cell errors; chart embedding verification in progress | Executed locally |
| Automated tests | 13 tests passed | Verified locally |
| Flask HTTP service | Readiness, prediction, invalid input and recommendation smoke checks passed | Verified locally |
| Streamlit | Flight prediction tested in browser; screenshot in docs/evidence | Partly browser-verified |
| Docker images | API/UI builds completed; missing pyarrow in initial serving image detected, corrected build in progress | Verification in progress |
| Kubernetes | kind cluster provisioning started; manifests written | Pending rollout verification |
| Airflow | Parse-safe DAG and Compose service written | Pending runtime verification |
| Jenkins | Pipeline stages and real smoke checks written | Pending Jenkins execution |
| MLflow UI | Experiments persisted in local SQLite store | UI evidence pending |
| Monitoring | Historical drift script and bounded load-test script written | Execution evidence pending |
| GitHub | Local history linked to techysuman27/MLOps-Travel-App; initial remote commit preserved | Publication pending |
| Public hosting | Render API + Streamlit Community Cloud selected | Account-authorized deployment pending |
| Google Docs/Drive | Local documentation and notebooks prepared | Upload/sharing pending |
| Video | Outline prepared; no recording claimed | Student recording pending |

No friend's code, model artifacts or write-ups were used in this implementation. The source review informed design decisions only.
