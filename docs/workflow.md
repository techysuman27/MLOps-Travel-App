# Voyage Analytics — MLOps workflow narrative

**Author:** techysuman27  
**Course:** AlmaBetter, Productionization of ML Systems  
**Repository:** https://github.com/techysuman27/MLOps-Travel-App

This is the source narrative for the separate Google Docs submission. It intentionally omits tool installation instructions. Screenshots must show our actual successful executions; pending stages below must be completed before final submission.

## 1. Modeling and release preparation

We validate the three course CSV schemas, reject invalid numeric/date values, verify user references and fingerprint the source snapshot. The flight model uses route, cabin, agency, duration, distance and calendar features. Identifiers and price-derived features are excluded. A chronological split reserves later flights for validation and final evaluation; trips crossing split boundaries are purged.

The validation comparison selects histogram gradient boosting with 200 iterations. Final held-out MAE is 5.75, RMSE 7.69 and R-squared 0.99955. These scores describe the constrained historical dataset, not current airline pricing. The course schema does not establish currency, so the application uses dataset currency units.

The complete preprocessing pipeline is persisted together with the estimator. A manifest identifies the run and artifact checksum. The local model gate requires at least a 10% validation RMSE improvement over a median baseline. A failed gate cannot overwrite the currently approved manifest.

## 2. REST API

The Flask application loads approved artifacts at startup. Clients send a JSON flight request; validation checks fields, categories, date and numeric bounds. The shared fitted pipeline transforms inputs and produces a prediction. Responses contain a request ID and model version so predictions can be traced to an artifact.

Liveness means the process can respond. Readiness means all required models loaded successfully. We tested a valid prediction, an invalid request returning HTTP 400, and missing-model readiness returning HTTP 503. The first Docker check caught a missing artifact dependency, demonstrating why readiness matters.

**Evidence:** flight-estimate.jpg shows the user-facing result of the API request. A dedicated API response screenshot remains to be captured.

## 3. Streamlit application

The interface calls the Flask API rather than training models or duplicating preprocessing. The flight estimator accepts journey details and displays an estimate with its limitations. The hotel explorer supports historical booking preferences and budget filters. The insights page displays measured model results. The classification lab clearly labels its weak predictive value and source-category semantics.

![Actual local flight estimate](evidence/flight-estimate.jpg)

The hotel dataset contains one hotel per destination. Therefore the UI distinguishes broad catalogue ranking from a destination-filtered lookup and never claims real-time room availability.

## 4. Docker deployment

Separate images package the API and UI. The API uses a production WSGI server, a non-root user and an HTTP readiness check. Model bundles are included with the release so every replica receives the same approved artifacts. The runtime dependency list must include dependencies used by serialized data objects, not just imports visible in the API file.

**Evidence pending:** healthy container state and successful prediction from the rebuilt API image. Do not replace this with a screenshot of a Dockerfile.

## 5. Kubernetes deployment and scaling

The Deployment starts two API replicas. A Service directs requests to ready pods. Startup probes allow model initialization; readiness prevents routing to unavailable models; liveness detects an unresponsive process. Resource requests/limits make scheduling and capacity explicit. Rollout history supports reverting to a previous release.

**Evidence pending:** ready pods, Service prediction, scaling from two to three replicas and bounded load-test results. The optional HPA requires metrics-server and separate observed scaling evidence. Manual scaling must not be described as automatic scaling.

## 6. Scheduling with Airflow

The regression DAG validates the source, trains and evaluates candidates, and approves only candidates that pass the gate. Code runs inside tasks, not during DAG parsing. The schedule is weekly, 02:00 UTC on Sundays; catch-up is disabled. Each run writes to a distinct candidate folder. Source data is fixed, so this demonstrates reproducible orchestration rather than a live travel feed.

**Evidence pending:** DAG graph, successful task instances and candidate output. The live service is not overwritten by this DAG; a release handoff is deliberate.

## 7. CI/CD with Jenkins

The pipeline checks out source, installs dependencies, executes real tests, builds an image and starts that image to verify a prediction. Explicit parameters control publishing and Kubernetes deployment. Registry and cluster credentials are stored in Jenkins, not in source files. Deployment uses a registry digest and verifies rollout and inference.

**Evidence pending:** a Jenkins build completing the applicable stages. The Jenkinsfile by itself is implementation evidence only. The initial Airflow-to-release handoff is manual selection of an approved candidate; automatic triggering is future work.

## 8. MLflow tracking and monitoring

MLflow contains separate experiments for flights, classification and hotels, with child candidate runs and final evaluation metrics. It records the dataset hash, Git commit and whether the working tree had uncommitted changes. Complete models/bundles and evaluation reports are logged. Early failed experiment exports remain visible as failed runs; they are not removed to make the history look cleaner.

Request logs record latency, status and request ID. The historical drift report compares feature distributions between training and held-out periods. Drift is not predictive error; accuracy monitoring needs actual subsequent outcomes.

**Evidence pending:** MLflow experiment comparison screenshot and operational report screenshots.

## 9. Limitations and next steps

The classification task has approximately 35% holdout accuracy and is an educational benchmark. The recommendation improvement over popularity is modest and does not prove satisfaction uplift. Public free hosting has cold starts and does not provide a production reliability guarantee. Newer data, clearer field semantics, outcome feedback and a richer hotel catalogue are prerequisites for credible business deployment.

Use verification.md as the final evidence checklist. Upload this narrative, with completed screenshots, to a separate viewable Google Doc as required by the course.
