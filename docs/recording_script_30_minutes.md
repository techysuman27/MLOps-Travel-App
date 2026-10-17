# Voyage Analytics: word-for-word recording script

Maximum video length: 30 minutes. Aim to finish in 25–28 minutes, leaving room for navigation. The timestamps below are pacing budgets, not a requirement to keep talking until each timestamp. Read naturally; rehearse once and shorten pauses if necessary. Speak only the blockquoted paragraphs. Instructions outside the quotes are actions for you, not narration.

This version follows your updated 30-minute maximum and replaces the earlier 40–45 minute recording plan for your recording. It focuses on flight-price regression. Do not claim that you have demonstrated an operation live when you show a saved screenshot.

## Before pressing Record — do not read this aloud

1. Open the public app and successfully make one prediction before recording. Free hosting may take time to wake up. Use a working combination from the form; do not promise a particular output before seeing it.
2. Open the architecture PNG locally or on GitHub. Keep it large enough for the labels to be readable.
3. Open the executed regression Colab notebook. Do not run all cells during the presentation. Its saved charts and results are the material you will explain.
4. Open the repository in your code editor. Close private files and hide notifications. Increase font size. Open only the files named below as you reach their section.
5. Use the saved execution evidence for Docker, Kubernetes, Airflow, Jenkins and MLflow. This makes the presentation reproducible without running all services at once. If you prefer live dashboards, start them and sign in before recording using demo_guide.md; change “captured evidence” to “dashboard” only when that is actually what you show.
6. Test 30 seconds of microphone and screen recording. A webcam is optional unless your course requires it. Hide passwords and unrelated tabs.
7. Keep this script on another device or in a window outside the recorded area. Do not show the script instead of the project.

### Browser tabs to prepare

- Architecture: https://github.com/techysuman27/MLOps-Travel-App/blob/main/docs/diagrams/voyage-architecture.png
- Repository: https://github.com/techysuman27/MLOps-Travel-App
- Regression notebook: https://colab.research.google.com/drive/1OzPywOfZkmzSpEqrx4p2J61Dpfjdh558
- Public application: https://voyage-analytics-suman.streamlit.app/
- Public readiness: https://voyage-analytics-api-kqju.onrender.com/health/ready

Local file paths below are relative to the project folder. Open image files in an image viewer so the audience sees the picture, not binary contents.

## 00:00–01:15 — Introduce the project

**SHOW:** The repository README, with the project title visible. Keep the page still while speaking.

> Hello everyone. In this video, I will explain Voyage Analytics, my capstone project for the Productionization of ML Systems module.
>
> The project belongs to the travel and tourism domain. It includes flight-price prediction, hotel recommendations, and an educational classification experiment using the source labels in the users dataset.
>
> Today, I will focus on the flight-price regression model and its complete lifecycle: understanding data, training and evaluating models, serving predictions through an API, deploying the application, and demonstrating the supporting MLOps workflows.
>
> The business purpose is to estimate historical flight prices from journey details. These are estimates learned from the supplied dataset, not live airline quotations. The larger engineering objective is to make the model usable through a repeatable, tested application.

**ACTION:** Open the architecture image.

## 01:15–03:15 — Explain the architecture

**SHOW:** `docs/diagrams/voyage-architecture.png`. Point to the top row, middle row, then bottom row. Do not read every box.

> This diagram separates the system into three connected activities.
>
> The top row is model development. We begin with the course datasets, validate and prepare them, train candidate models, evaluate their performance, and save an approved model bundle.
>
> The middle row contains the supporting tools. MLflow records experiments, including parameters, scores and model artifacts. GitHub stores the project history and release source. Jenkins runs automated tests, builds the Docker image, checks predictions and performs the enabled deployment steps.
>
> Airflow has a different responsibility. It runs the regression training tasks in the correct order and produces a new candidate model. A candidate is reviewed before it becomes a release; completing an Airflow run does not immediately change the public application.
>
> The bottom row is what happens when a user visits the application. Streamlit collects the inputs, Flask validates them and calls the saved model, and the result returns to the screen.
>
> The public application uses Streamlit Community Cloud and Render. Kubernetes is a separate local deployment demonstration. A normal prediction request does not retrain the model or start a Jenkins build.

## 03:15–05:15 — Explain the datasets

**SHOW:** Regression notebook: `Project Summary`, then `1. Know Your Data`, dataset shape and schema output. Briefly point to the variable descriptions in section 2.

> The project uses three datasets: users, flights and hotels. The flights dataset supplies the regression target, which is price. The users dataset supports the classification experiment, and hotel booking history supports recommendations.
>
> The flights dataset contains 271,888 records. Its important prediction fields include origin, destination, cabin type, agency, duration, distance and date.
>
> The datasets also contain identifiers. User code links records to users, and travel code identifies trips. These are useful for relationships and validation, but they are not treated as numerical flight-price features.
>
> An important detail is that one trip can have multiple flight rows. Joining hotel bookings to flights without checking this relationship could duplicate hotel spending. Understanding the relationships is therefore part of preparing reliable data.
>
> The validation code checks required columns, numerical values, dates and user references. The initial audit found no missing values or exact duplicate rows in the supplied snapshot. That does not prove that the data represents today's travel market.

## 05:15–07:15 — Explain exploration

**SHOW:** Notebook section 4. Show Chart 1, Chart 9 and Chart 13 in that order. Give viewers a few seconds to read each chart and its saved observation.

> The notebook includes training-data exploration before modeling. I will highlight three views rather than read every chart.
>
> First, the price distribution shows how the target is spread out. This helps explain why both average absolute error and a metric that emphasizes larger mistakes are useful. Valid expensive flights are not removed simply because they are unusual.

**ACTION:** Scroll to Chart 9, “Price by cabin.”

> This chart compares price distributions across cabin categories. Cabin is a plausible pricing feature, but an observed difference does not prove causation. It still needs to improve predictions on data that was not used for fitting.

**ACTION:** Scroll to Chart 13, “Median route prices.”

> The route chart shows historical median prices for origin and destination combinations. A blank cell indicates missing observations, not a zero-price flight. It helps identify where the data provides support and where estimates may be less reliable.
>
> These charts are based on the training partition. The final test data is reserved for evaluation rather than repeatedly explored to improve the model.

## 07:15–09:15 — Explain splitting and preprocessing

**SHOW:** Notebook section 3 split output, then `src/voyage/features.py` in the editor. Highlight `FLIGHT_INPUTS`, `FlightFeatures` and `flight_pipeline`.

> The regression task uses a chronological split. Earlier records form the training set, a later period is used for validation, and the latest period is held out for final testing.
>
> Training is where the model learns. Validation is where candidate models are compared. The test set provides the final independent assessment. The split logic also checks for trips crossing partition boundaries; the recorded split required zero rows to be purged.
>
> This file defines the features used consistently during training and prediction. Month and weekday are extracted from the recorded date. Categorical fields are encoded, and numerical features are standardized inside the pipeline.
>
> Preprocessing is fitted on the appropriate training data, rather than learning categories or scaling information from the final test set. The complete fitted pipeline is saved with the estimator. This prevents the API from using a different transformation from the one used during model development.
>
> The project does not invent booking lead time because the supplied schema does not provide separate booking and departure dates.

## 09:15–11:45 — Explain model selection and results

**SHOW:** Notebook section 7 comparison output, or the beginning of `reports/flights.json`. Keep `validation_candidates` and then `test_metrics` visible. Do not scroll through all route slices.

> I compared a median baseline, Ridge regression, and histogram gradient boosting with two iteration budgets.
>
> The baseline predicts a typical price without learning detailed relationships. It establishes the minimum comparison: a more complex model should justify itself by doing better.
>
> On validation data, the baseline RMSE was about 366.27, Ridge was about 102.46, gradient boosting with 100 iterations was about 15.91, and the 200-iteration candidate achieved about 6.62. The validation comparison therefore selected the 200-iteration model.
>
> The selected model was refitted using training and validation data, then evaluated on the held-out test period. Its test MAE was approximately 5.75, RMSE was 7.69, and R-squared was 0.99955.
>
> MAE measures the average absolute prediction error. RMSE gives more weight to larger mistakes. R-squared describes how well the model accounts for target variation relative to a mean-based reference. It is not classification accuracy, and I would not describe it as 99.95 percent accurate.
>
> These strong results apply to this constrained historical dataset. They do not establish comparable performance on current airline prices. The source also does not confirm the currency, so the application reports dataset currency units.
>
> The flight quality gate requires validation RMSE to improve by at least ten percent over the median baseline. The final test set does not decide which candidate is selected.

## 11:45–12:45 — Explain the saved artifact

**SHOW:** `models/flights.json`: point to `version`, `artifact` and `sha256`. Show the relevant model folder in the editor sidebar; do not open a joblib file as text.

> This manifest identifies the approved model version and the location of its saved joblib bundle. The bundle contains the fitted preprocessing and estimator together.
>
> The checksum helps detect whether the artifact bytes have changed. At startup, the application verifies and loads the approved bundles. This makes a prediction traceable to a particular model version.
>
> MLflow stores experiment records and model artifacts, while the running API serves its pinned bundle. It does not automatically switch to whichever experiment is newest.

## 12:45–15:45 — Demonstrate Streamlit and Flask

**SHOW:** Public application → flight estimator. Use the inputs you checked before recording. Pause narration while entering values. Click “Estimate flight price.”

> I will now demonstrate the user-facing prediction flow. The user supplies journey details through this form. When I click the prediction button, Streamlit sends those values to the Flask API.

**ACTION:** Wait for the actual result. Point to the value that appears. Do not read an old expected number if the screen shows a different result.

> The estimate is now displayed. The interface also explains that it is a historical estimate in dataset units. Where the requested date is outside the training period, the application warns that current-market accuracy has not been verified.

**SHOW:** `api/app.py`. Use editor search for `/api/v1/flights/predict`; show the endpoint and its surrounding validation/prediction code.

> This is the Flask endpoint behind the screen. It checks required fields, supported categories and numerical values before calling the saved pipeline. The response includes a prediction, a model version and a request identifier.
>
> Invalid input should produce a clear client error rather than an unreliable prediction. The tests cover malformed requests and unknown categories, as well as valid inference.

**SHOW:** Public `/health/ready` browser tab. Then `docs/evidence/public-api-response.json` in the editor.

> Readiness checks whether the required models loaded successfully. Liveness asks whether the process can respond. These are different checks: a running process may still be unable to make predictions.
>
> This saved JSON is a captured response from a verified public prediction request. It shows the estimate, model version, request ID and warnings. The request flow is Streamlit to Flask to the saved model, then back to Streamlit. Training is not part of this interaction.

**If the public app does not respond:** Stop recording, resolve or warm up the app, then record this section again. If you choose to use `docs/evidence/public-flight-estimate.jpg` instead, say “This is the captured result of a previously verified public prediction.” Do not say “now displayed” as if it just ran.

## 15:45–17:15 — Explain Docker

**SHOW:** `docker/Dockerfile.api`, then `docs/evidence/docker-status.txt`.

> Docker packages the API with its Python environment, dependencies and approved model files. This helps the same release run consistently in different environments.
>
> The Dockerfile starts from a Python image, installs runtime requirements, copies the shared package and API, and includes the model artifacts. It runs the application through a production WSGI server and uses a non-root application user.
>
> Its health check calls the readiness endpoint. This is useful because the container should be considered usable only after the models are available.
>
> During testing, the first image exposed a missing dependency required by a serialized artifact. Adding that dependency and repeating the container checks fixed the problem. This demonstrates why testing a notebook alone is insufficient.
>
> The file on screen is captured container-state evidence. Real checks also exercised prediction, invalid-input handling and recommendations against the running API image.

## 17:15–19:15 — Explain Kubernetes and scaling

**SHOW:** `kubernetes/deployment.yml`, then `docs/evidence/kubernetes-rollout.txt`. Locate the two-replica and three-replica results in advance.

> Docker packages the application. Kubernetes manages running copies of that application.
>
> The Deployment describes the desired API replicas and their resource budgets. The Service provides a stable endpoint for reaching available replicas. Startup and readiness probes allow models to initialize before the pod is considered ready. Liveness checks help identify an unresponsive process.
>
> This is saved output from the local cluster demonstration. The deployment initially reached two ready replicas and passed prediction checks. It was then manually scaled to three ready replicas.
>
> This is manual scaling, not a demonstration of automatic scaling. The optional Horizontal Pod Autoscaler configuration needs a working metrics dependency and observed scaling behavior before I could claim that it is verified.
>
> A bounded test also completed 200 predictions successfully with eight concurrent workers. That test used a port-forward to one selected pod. It demonstrates concurrent inference reliability, but it does not prove load balancing or improved throughput from the extra replicas.
>
> The public Render service and this local Kubernetes cluster are separate deployment environments.

## 19:15–21:15 — Explain Airflow

**SHOW:** `docs/evidence/airflow-success.jpg`, then `airflow/dags/regression_lifecycle.py`.

> Airflow automates the regression training workflow. The successful execution shown here has three tasks: validate the source, train and evaluate candidates, and approve a candidate that passes the gate.
>
> The arrows define the dependencies. Training should not proceed after failed data validation, and a failed candidate should not replace the approved model.
>
> The DAG calls the same shared Python package used by the modeling workflow. Each run writes to a separate candidate directory, making its output identifiable and keeping it apart from the deployed bundle. PostgreSQL stores Airflow's workflow state.
>
> The configured schedule is weekly, at 02:00 UTC on Sundays, with catch-up disabled. The successful run in this screenshot was manually triggered; the screenshot is not proof of an unattended weekly run.
>
> An earlier attempt failed because a relative code path was resolved from Airflow's temporary working directory. The fix used an absolute package path and an explicit task working directory. The failed history was retained.
>
> Airflow produces an approved candidate. A person still reviews and selects it for release; this workflow does not automatically overwrite the public model.

## 21:15–23:15 — Explain Jenkins

**SHOW:** `Jenkinsfile`, then `docs/evidence/jenkins-console.txt`. Search the log for `13 passed`, then `Local deployment verified`, and finally `Finished: SUCCESS`.

> Jenkins automates application checks and release steps. It has a different role from Airflow: Airflow organizes model training, while Jenkins tests and releases the application.
>
> The pipeline checks out a GitHub revision, prepares its environment, runs tests, builds a Docker image and starts that image for real prediction checks.
>
> The test suite covers important behavior, including artifact loading, preprocessing consistency, invalid inputs, missing-model readiness and preservation of the current release when promotion fails. Thirteen tests passed in the demonstrated build.
>
> Build three also enabled the local deployment stage. It deployed the tested image as a persistent API on localhost port 18081 and verified readiness, prediction, validation and recommendation behavior.
>
> The log ends with success. Registry publishing and Kubernetes deployment were skipped in this run. Those stages are configurable options, and I am not presenting them as executed evidence.
>
> The local deployment script preserves the previous container until the replacement passes its checks. Its failure-restoration path is implemented, although I have not demonstrated a deliberately injected deployment failure. The recorded pipeline build was explicitly triggered; a GitHub webhook is not claimed here.

## 23:15–24:45 — Explain MLflow

**SHOW:** `docs/evidence/mlflow-flight-run.jpg`. Zoom enough to read the metrics and version. Optionally show `models/flights.json` beside it.

> MLflow is the experiment record for this project. It connects a training run to its settings, evaluation metrics and saved artifacts.
>
> This screenshot shows the recorded flight-model run, including its test metrics and registered model version. The scores match the evaluation report we saw earlier.
>
> The tracking code also records the dataset fingerprint and available code-version information. This helps answer questions such as: which data produced this model, what settings were used, and which artifact belongs to the result?
>
> Version tracking makes comparison and investigation more systematic. It does not, by itself, prove that a version is deployed or that it is accurate on new real-world data. The application manifest identifies the bundle actually served.
>
> The original modeling experiments and the container-hosted Airflow demonstration use separate tracking stores, so they should not be confused when reviewing the dashboards.

## 24:45–27:15 — Monitoring, learnings and conclusion

**SHOW:** `reports/drift.json`, then the architecture diagram. End on the GitHub README or public application.

> Monitoring has two different questions: is the service working, and are its predictions still useful?
>
> The API records request identifiers, status and latency. These help investigate errors and slow responses. Model versions make it possible to identify the release associated with a prediction.
>
> This drift report compares historical feature distributions. A distribution change can suggest that a model needs investigation, but drift is not the same as prediction error. Measuring real predictive accuracy requires actual later outcomes.
>
> The main engineering lessons came from connecting the components. A model that works in a notebook can fail when packaged because of dependencies. A training command can fail under a scheduler because its working directory is different. Separating shared model logic from notebooks and serving code made these problems easier to fix consistently.
>
> There are also clear limitations. The flight results are from a constrained historical dataset. The hotel catalogue has only nine hotels, with one hotel per destination. The classification experiment has weak predictive value and is presented as an educational source-label benchmark. Free public hosting also has cold starts.
>
> Future improvements would include newer data, outcome-based accuracy monitoring, stronger authentication, a richer hotel catalogue, and verified automatic scaling and Kubernetes release automation.
>
> This project demonstrates the path from validated data to a tested prediction application, with experiment tracking, containerization, deployment, scheduling and a verified local release pipeline. The repository contains the code, executed notebooks, reports and execution evidence. Thank you for watching.

**ACTION:** Leave the repository URL visible for three seconds, then stop recording. Aim to stop by minute 29; do not add an unplanned tour of the other models.

## If your rehearsal is too long

- Show two charts instead of three in the exploration section.
- Read only the best validation RMSE and the final test metrics, rather than all four validation values.
- Keep the captured evidence open in advance; do not search for files while recording.
- Remove optional dashboard navigation rather than removing the explanation of a required tool.
- Do not include tool installation, full training waits, package installation output or login screens.

## Final recording check

Confirm the video is under 30 minutes, the screen and narration are understandable, no secrets are visible, and every screenshot is described as captured evidence. Watch the result before uploading. Test the video sharing link from a signed-out browser. Submit the project folder and video under their separate dashboard fields.
