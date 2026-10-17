# Recording outline — regression lifecycle, 40–45 minutes

This is the earlier extended outline. For the student's updated 30-minute maximum, use [the current word-for-word recording script](recording_script_30_minutes.md), including its screen-by-screen directions.

The course text contains conflicting minimum durations. This outline targets the stricter 40-minute requirement; confirm with the mentor before shortening it. Record only after the evidence checklist is complete. This is a speaking outline, not a claim that pending services already ran.

| Time | Topic | What to show and explain |
|---|---|---|
| 0:00–3:00 | Introduction and business problem | Name, course, repository, public demo; explain historical flight-price estimation and limits |
| 3:00–7:00 | Data and relationships | Three CSV roles, user/trip joins, two flight legs per trip, source validation and fingerprints |
| 7:00–12:00 | Exploration and preparation | Regression notebook charts; meaningful observations; why identifiers are excluded; chronological split and purged trips |
| 12:00–18:00 | Models and evaluation | Median baseline, Ridge, two boosting budgets, validation selection, final holdout metrics, route/cabin errors and feature importance |
| 18:00–23:00 | Serving through Flask | Request contract, persisted preprocessing, real JSON prediction, malformed request, model version, liveness versus readiness |
| 23:00–26:00 | User interface | Enter a journey in Streamlit; show the estimate and explain that it calls the API |
| 26:00–30:00 | Docker | Working images and containers; show prediction inside the deployed container; explain the missing-dependency issue caught during testing |
| 30:00–34:00 | Kubernetes | Ready replicas, Service, scale demonstration and rollout; distinguish manual scaling from HPA evidence |
| 34:00–37:00 | Airflow | DAG graph, task ordering, logs, per-run artifacts, gate and schedule; explain that data is historical |
| 37:00–40:00 | Jenkins | Actual build stages, failed-test behavior, container smoke check and deployment settings |
| 40:00–43:00 | MLflow, monitoring and learnings | Candidate comparisons, artifact version, latency/error logs, drift limitations, rollback and future improvements |

## Suggested opening

“This is Voyage Analytics, my individual capstone for Productionization of ML Systems. I built a travel application with a flight-price estimator, a hotel recommendation feature, and an educational classification experiment. In this video, I will focus on the flight-price model and show how it moves from historical data through training, testing, serving and deployment. I will also explain how the workflow is scheduled and how model versions are tracked.”

## Statements to explain accurately

- The reported 5.75 MAE is in dataset currency units, not verified rupees or dollars.
- High historical accuracy does not prove current airline-price accuracy; the catalogue and data-generating process may be highly constrained.
- The final test set did not choose the model. Validation selected it; the test set assessed it.
- Flask receives raw supported inputs; its serialized pipeline applies exactly the fitted training transformation.
- Docker reproduces an environment; Kubernetes operates replicas. They solve different problems.
- Airflow orchestrates model work; Jenkins validates and releases software. The current candidate handoff must be described as implemented, not embellished.
- MLflow records experiments and artifacts. The application serves a pinned local bundle; it does not dynamically switch to whichever experiment scored best.
- A Kubernetes YAML file does not prove scaling. Show the actual replica transition and label manual versus automatic behavior correctly.
- A free public demo may sleep and is separate from local Kubernetes evidence.

## Interview prompts

**How would you productionize real-time pricing?** Validate supported input, serve a complete fitted pipeline, version its artifact, test the container, check readiness, measure latency/errors and collect outcomes for later accuracy checks.

**Why Docker and Kubernetes?** Docker packages code and dependencies. Kubernetes manages deployment, traffic to ready replicas, resource allocation and scaling policies.

**How does MLflow help?** It connects parameters, metrics, datasets and artifacts to specific runs so experiments can be compared and releases traced.

**How would retraining work?** Validate a new snapshot, use time-correct evaluation, compare the candidate with a baseline/current model, approve it only after checks, then deploy a versioned image with rollback available.

**How would you scale further?** Measure the bottleneck first, load-test with representative traffic, tune workers/replicas and memory, introduce asynchronous training and outcome monitoring, and avoid adding infrastructure without a measured need.

## Before pressing Record

Open the public demo, repository, regression notebook, API example, Docker, Kubernetes, Airflow, Jenkins and MLflow evidence in the order used above. Hide credentials and personal browser content. Warm a sleeping free service before the demo. Verify microphone and screen readability with a short test recording. Upload the final recording separately from the Drive folder containing the three notebooks and workflow document.
