# Voyage Analytics: submission and implementation requirements

Status: source datasets and original modeling template downloaded; initial data audit complete. Models, applications, infrastructure, and deployments are not implemented or verified yet.

## Deliverables

- Three individual Colab-compatible modeling notebooks: regression, classification, and recommendation. Follow the supplied ML template's modeling sections, include reasoning and results, and insert the final GitHub URL and project summaries.
- One public GitHub repository containing reusable Python model code, saved models, Flask API, Streamlit interface, dependencies, Docker files, Kubernetes manifests, Airflow DAGs, Jenkins pipeline, MLflow integration, tests, and documentation.
- Google Docs workflow documentation with actual execution screenshots for REST API, Streamlit, Docker, Kubernetes, Airflow scheduling, Jenkins CI/CD, and MLflow. Exclude tool installation steps from this submission document; retain reproducible setup instructions in the repository README.
- Public application access requested by the student. Hosting destination and account access remain to be determined.
- Viewable Google Drive submission folder with three notebooks and workflow documents; separate video link.
- Regression-focused video covering modeling, serving, deployment, scaling, orchestration, CI/CD, and tracking. Supplied instructions conflict between a minimum of 40 minutes and a minimum of 15 minutes. Plan a 40–45 minute version unless the mentor clarifies the requirement.

## Modular design

The notebooks are assessed modeling narratives; they do not contain the entire production system. Reusable training, preprocessing, evaluation, and inference functions belong in a Python package and are used by both the notebooks and applications. Keep notebook execution compatible with Colab by documenting repository setup and data retrieval.

Proposed directories: notebooks/, src/voyage/, api/, app/, models/, docker/, kubernetes/, airflow/dags/, tests/, docs/, and scripts/. Keep Jenkinsfile, requirements.txt, and README.md at the repository root.

## Initial data findings

See data_audit.json for measured row counts, fields, dates, missingness, duplicates, and join checks.

- flights.csv: 271,888 rows; September 2019–July 2023.
- hotels.csv: 40,552 rows; nine distinct hotel names and nine distinct places.
- users.csv: 1,340 rows; labels male=452, female=448, none=440. The meaning of `none` is not established by the supplied schema. Preserve this category during ingestion and document any target treatment explicitly. Do not equate it with a gender identity.
- No empty cells or exact duplicate rows were found. This does not establish that all values are semantically valid.
- All flight and hotel user references match users.csv.
- Each (travelCode, userCode) has two flight rows, whereas hotel bookings have one row per such key. An unrestricted join would repeat hotel totals. Aggregate at the correct grain before joining or reporting spending.

## Evaluation requirements

- Regression: exclude identifiers from predictive features, compare a baseline with trained candidates, fit preprocessing only on training data, use a chronological holdout with trip overlap controlled, report MAE, RMSE, and R-squared. Preserve the final test set for final evaluation.
- Classification: split at user level, document label semantics, compare against a dummy baseline, report accuracy, macro precision/recall/F1, and confusion matrix. Do not claim useful gender predictability without evidence. Avoid exposing personal names in public demonstrations.
- Recommendation: treat bookings as implicit interactions rather than ratings; evaluate on held-out future interactions, compare with popularity, document repeat-booking eligibility and cold-start behavior, and report ranking metrics plus catalogue coverage. Inspect hotel-to-place mapping because a destination filter may leave little ranking choice.
- Track model parameters, metrics, artifacts, data versions, and preprocessing in MLflow. Test that saved models reproduce predictions.
- Distinguish checked configuration files from running services and genuinely verified deployment evidence.

## Sources

- Dataset: https://drive.google.com/file/d/1fd21ljY3KS3B6ZPITmSlDHVD2yff46OC/view
- Template folder: https://drive.google.com/drive/folders/12juJhrkwnCyLoWCAoglO-TzdxqDfeFVw
- Original downloaded ML template: templates/AlmaBetter_ML_Submission_Template.ipynb
- Evaluation criteria and submission requirements supplied by the student in this chat.

## Outstanding external inputs

- GitHub repository URL/account connection for publication.
- Hosting account and destination; confirm any paid resources before provisioning.
- Student name for submission attribution.
- Google Drive/Docs access for final upload and sharing, or student-managed upload of locally produced artifacts.
