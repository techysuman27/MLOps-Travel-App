# Reference repository review

Reviewed on 11 October 2026. Scope: read-only review of downloaded source, tracked files, notebook code, and dataset row counts. No reference code, serialized models, or containers were executed. Runtime deployments and claimed performance were not independently reproduced. These findings describe the checked commits, not the authors' private deployments or work outside GitHub.

## San7122/Travel_Mlops

Reviewed commit: `96b1d4a5a55e7fec31ffa7040e8daea53524fe55`.

Strengths: clear separation of model, API, dashboard, Docker, Kubernetes, Airflow, Jenkins, and tracking files; an extensive Jenkins pipeline; explicit API routes; saved model bundles that include preprocessing objects; Kubernetes resource settings and probes. These are useful examples of the breadth expected by the rubric.

Verified limitations:

1. **Different training data.** The checked CSVs have 500 users, 2,000 flights, and 1,500 hotel bookings. `data/generate_data.py` explicitly generates synthetic data. These results cannot establish performance on our supplied 1,340-user, 271,888-flight, 40,552-booking dataset. [Source](https://github.com/San7122/Travel_Mlops/blob/96b1d4a5a55e7fec31ffa7040e8daea53524fe55/data/generate_data.py#L13-L16)
2. **Container startup does not initialize models.** `api/app.py` initializes model globals to `None`; its only `load_models()` call is inside the main-script guard at line 384. The Dockerfile starts Gunicorn by importing `api.app:app`, so that call is skipped. Prediction routes return 503 when models are absent. The health route still returns HTTP 200 with `status: healthy`. This is a static startup-path finding, not a reproduced deployment failure. [API](https://github.com/San7122/Travel_Mlops/blob/96b1d4a5a55e7fec31ffa7040e8daea53524fe55/api/app.py#L382-L394), [Dockerfile](https://github.com/San7122/Travel_Mlops/blob/96b1d4a5a55e7fec31ffa7040e8daea53524fe55/docker/Dockerfile#L47)
3. **Tests are referenced but absent.** The README describes `tests/test_models.py`, and Jenkins invokes `pytest tests/`. No test Python files or test directory are present in the checkout. Jenkins' model-validation stage checks that objects exist, rather than checking measured quality. [Pipeline](https://github.com/San7122/Travel_Mlops/blob/96b1d4a5a55e7fec31ffa7040e8daea53524fe55/jenkins/Jenkinsfile#L68-L81)
4. **Training and serving transformations are separate.** Flight training extracts date features from a date, whereas inference iterates through stored feature names and defaults missing numerical values to zero. Unknown categorical values are mapped to zero, conflating them with a known category. The categorical encoders are also fitted before the split. [Model](https://github.com/San7122/Travel_Mlops/blob/96b1d4a5a55e7fec31ffa7040e8daea53524fe55/models/flight_price_model.py#L144-L170)
5. **No submission notebooks found.** The checked tree contains no `.ipynb` files. Our submission explicitly needs three.

## sanaa-04/MLOPS-Project-Almabetter

Reviewed commit: `6227aa30b626f2c53ebafe7316d82c109e9d1617`.

Strengths: supplied-scale datasets, substantial regression and classification notebooks, Flask and Streamlit applications, model artifacts, Kubernetes configuration, and an MLflow training script. The regression notebook compares multiple models and includes hyperparameter searches.

Verified limitations:

1. **Airflow is not self-contained in this checkout.** Both flight DAG files import `utils.data_ingestion`, `utils.data_transformation`, and `utils.model_training`; those modules are absent. Data loading and transformation also occur at module scope, during DAG parsing, before scheduled tasks run. External files could make the author's environment work, but they are not supplied here. [DAG](https://github.com/sanaa-04/MLOPS-Project-Almabetter/blob/6227aa30b626f2c53ebafe7316d82c109e9d1617/Airflow_Travel_System/flight_price_prediction_dag.py#L6-L18)
2. **Company encoding changes at prediction time.** The classification API creates a new LabelEncoder and fits it to the incoming company. For a one-row request this becomes zero regardless of company. It also includes user code as a model input. A persisted preprocessing pipeline and identifier exclusion would avoid these issues. [Classification API](https://github.com/sanaa-04/MLOPS-Project-Almabetter/blob/6227aa30b626f2c53ebafe7316d82c109e9d1617/Gender%20Classification%20Model/app.py#L36-L62)
3. **Classification preprocessing sees held-out data.** Notebook cell 33 fits PCA to all name embeddings before train/test splitting. Test rows therefore influence the representation. This does not quantify the score inflation; it means the holdout is not fully isolated. [Notebook](https://github.com/sanaa-04/MLOPS-Project-Almabetter/blob/6227aa30b626f2c53ebafe7316d82c109e9d1617/Gender%20Classification%20Model/Python%20files/Gender_Classification_Model_SK.ipynb)
4. **Recommendation signal needs justification.** The hotel app aggregates the sum of nightly prices by user/hotel as its interaction value, then factorizes the matrix at application execution. Higher nightly prices are not a direct measure of satisfaction, and expensive model preparation is coupled to the UI. [Recommender](https://github.com/sanaa-04/MLOPS-Project-Almabetter/blob/6227aa30b626f2c53ebafe7316d82c109e9d1617/Hotel%20Recommender%20System/streamlit_app.py#L57-L102)
5. **Submission/reproducibility gaps.** Two notebooks were found, no recommendation notebook, no Jenkinsfile, and no automated Python tests. The README mentions Jenkins and describes paths that differ from the actual directory structure. Kubernetes specifies replicas, but the reviewed flight deployment contains neither readiness/liveness probes nor an autoscaling policy. These findings concern supplied files, not whether Jenkins or scaling was demonstrated elsewhere.

## Lessons for our independent implementation

Use these repositories as examples of assignment scope only. Do not copy their functions, UI, notebooks, artifacts, metrics, or narrative. Use our downloaded course dataset, new code, original diagrams and explanations, fresh trained artifacts, and real incremental commits. Shared required technologies and conventional folder names are expected; originality should be evident in the decisions, evidence, implementation, and explanation.

Our strongest improvements should be: reproducible data and splits, shared preprocessing, actual model quality gates, import-safe serving and scheduling, operational tests, traceable releases, honest recommendation evaluation, and screenshots from our own successful runs. We cannot claim better accuracy until independent evaluation supports it.
