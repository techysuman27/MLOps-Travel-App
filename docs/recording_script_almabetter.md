# AlmaBetter presentation — simple speaking script

This is the current recording script. It follows AlmaBetter's eight sections and covers all three models, with the flight model used for the detailed serving example. It replaces the earlier regression-only 30-minute plan for this recording.

The guideline totals 15 minutes. Adding at most 30 seconds to each of eight sections gives a maximum of 19 minutes. Aim for 17–18 minutes after rehearsal. The times below are maximum budgets, including screen navigation; finish early if you complete a section. Do not add the interview answers to the main recording unless requested.

Read only the quoted paragraphs aloud. SHOW tells you what to open. REMEMBER is a short memory cue; it is not extra narration.

## Preparation — not spoken

- Open the architecture image, GitHub README, executed notebooks and public app before recording.
- Make one flight prediction and one hotel request before recording to check that the public app is ready. If a service is unavailable, resolve it before recording or use a saved screenshot and explicitly say it is a previously captured result.
- Use saved execution screenshots for infrastructure sections so you do not need to run all local services together. Do not describe screenshots as live executions.
- Open the images in a viewer at a readable size. Keep the script outside the recorded screen. Close passwords, private files and notifications.
- Record a short audio test, then rehearse once with a timer. If a section exceeds its limit, shorten navigation or remove a nonessential sentence; do not speed-read.

### Main links

- Public app: https://voyage-analytics-suman.streamlit.app/
- Repository: https://github.com/techysuman27/MLOps-Travel-App
- Architecture: https://github.com/techysuman27/MLOps-Travel-App/blob/main/docs/diagrams/voyage-architecture.png
- Regression notebook: https://colab.research.google.com/drive/1OzPywOfZkmzSpEqrx4p2J61Dpfjdh558
- Classification notebook: https://colab.research.google.com/drive/17kI3qL3QGaHoe4i0bCJJK4GivtpoMSfi
- Recommendation notebook: https://colab.research.google.com/drive/1u31sfhp2egolu9DR4epyRoPhZyZ-tznD

## 1. Introduction — guideline 1:30; maximum 2:00

**SHOW:** GitHub README title, then the architecture image. Keep the diagram visible as you name the tools.

**REMEMBER:** Project → three tasks → tools → full system.

> Hello everyone. My project is called Voyage Analytics. I built it for the Productionization of ML Systems module.
>
> It is a machine learning application for travel and tourism. It has three main features: estimating flight prices, classifying the recorded gender labels in the users dataset, and suggesting hotels.
>
> The flight model helps demonstrate travel-budget estimation. The hotel model ranks options using historical bookings. The classification model is an educational experiment. Its results are weak, so it should not be used to decide a person's identity or make decisions about them.
>
> I used Python for data processing and modeling, Flask for the prediction API, and Streamlit for the user interface. Docker packages the application, while Kubernetes demonstrates running multiple copies. Airflow manages the training workflow, Jenkins handles automated testing and release steps, and MLflow tracks experiments and model versions.
>
> The goal was to build more than a trained model. I wanted a complete system where a user can enter information, receive a result, and where the development and deployment steps can be repeated and checked.
>
> I will explain the business problem, data, models, application flow and MLOps tools in that order.

## 2. Problem Understanding — guideline 2:00; maximum 2:30

**SHOW:** Architecture image. Point to datasets and models, then Flask and Streamlit, then the automation tools.

**REMEMBER:** Useful predictions → usable application → repeatable process.

> Travel datasets contain patterns in routes, cabin classes, prices and booking history. Machine learning can learn these patterns and use them to estimate a price or rank hotel suggestions.
>
> For example, someone planning a trip could enter journey details and get a historical flight-price estimate. A hotel recommendation system could use their previous bookings to suggest relevant options. In this project, these are demonstrations based on the supplied data, not live airline or hotel services.
>
> The system includes prediction, classification, recommendation and automation. Each task has a different purpose and needs its own evaluation. A model should not be described as useful just because it produces an answer.
>
> A notebook is useful for exploring data and comparing models. However, a normal user cannot be expected to open a notebook and run Python cells whenever they need a prediction.
>
> That is why productionization matters. We need an interface, an API, input checks, a saved model, a repeatable environment and a reliable release process. We also need to know which model version produced a result and whether the service is working.
>
> My project connects these pieces. The trained model becomes one part of an application that can be tested, deployed and maintained.

## 3. Data Understanding and Use Case Mapping — guideline 2:00; maximum 2:30

**SHOW:** Regression notebook, sections 1 and 2, with dataset shape and variable descriptions. Briefly show the classification and recommendation notebook titles; do not tour their charts.

**REMEMBER:** Users → labels; flights → prices; hotels → suggestions; IDs → connections.

> There are three datasets: users, flights and hotels.
>
> The users dataset contains a user code, company, name, gender label and age. It supports the classification task. I used age and company as features and excluded personal names and user identifiers. The source labels include male, female and an undocumented category called none. I kept that category without inventing a meaning for it.
>
> The flights dataset contains the route, cabin type, price, duration, distance, agency and date. It supports flight-price regression, with price as the target.
>
> The hotels dataset contains hotel name, location, stay duration, nightly price, total price and date. Its booking history supports recommendations and budget filtering.
>
> The users table's code connects to userCode in the booking tables. TravelCode identifies trips and helps relate flight and hotel records. These identifiers support relationships; they are not automatically useful prediction features.
>
> One trip can contain multiple flight rows. A careless join can therefore duplicate hotel information. I checked these relationships and validated the data before modeling.
>
> The initial audit checked missing values, duplicates, numerical values and dates. I also found only nine hotels, with one hotel per destination. That limits how much choice the recommendation system can offer within a city.

## 4. Model Development and Serving Design — guideline 2:30; maximum 3:00

**SHOW, in order:** Regression notebook section 7 model comparison and test metrics → `src/voyage/features.py` → public app flight estimator → `docs/evidence/public-api-response.json`.

**ACTION:** Use the already checked flight inputs and click Estimate flight price. Allow about 20 seconds for the screen demonstration. Do not read out a predicted value before seeing it.

**REMEMBER:** Compare → select → save → request → response.

> I developed a separate approach for each task.
>
> For flight prices, I compared a median baseline, Ridge regression and histogram gradient boosting. The 200-iteration gradient boosting model gave the best validation result. On the final test set, its mean absolute error was about 5.75 and its RMSE was about 7.69, in dataset currency units. These results describe the historical dataset, not today's airline prices.
>
> For classification, I compared a majority baseline, logistic regression and random forest. Random forest was selected, but test accuracy was only about 35 percent. I report that limitation clearly.
>
> For hotels, I compared popularity with personalized ranking based on booking history. The ranking approach was selected using validation results and evaluated on later bookings.
>
> For flight preprocessing, I used route, cabin, agency, duration, distance and date. Month and weekday are extracted from the date. Categories are encoded, and numerical features are scaled inside the pipeline.
>
> Flight and hotel data use time-based splits. The classification split keeps users separate. The final test data does not choose the winning model.
>
> The fitted preprocessing and model are saved together. Now, when I submit these journey details in Streamlit, the app sends a request to Flask. Flask checks the input, runs the saved pipeline and returns the estimate for display.

**ACTION:** Point to the actual displayed result, then open the saved JSON response.

> This JSON is a captured API response. It includes the prediction, model version, request ID and warnings. The model is already trained; a user request only runs prediction.

## 5. MLOps Pipeline and Deployment — guideline 2:00; maximum 2:30

**SHOW:** Architecture image. Then briefly show `docs/evidence/airflow-success.jpg`, `docs/evidence/jenkins-console.txt` near “Local deployment verified,” and `docs/evidence/mlflow-flight-run.jpg`. Have them ready so switching takes only a few seconds.

**REMEMBER:** Docker packs; Kubernetes manages; Jenkins releases; Airflow schedules; MLflow records.

> Each MLOps tool has a clear job in this project.
>
> Docker packages the API, dependencies and approved model files into a runnable image. This helps reproduce the application environment.
>
> Kubernetes manages multiple running copies of the API. In the local demonstration, the deployment reached two ready replicas and was manually scaled to three. Automatic scaling has not been verified. The public API runs separately on Render, and the public interface runs on Streamlit Community Cloud.
>
> Jenkins gets the source from GitHub, runs tests, builds the image and checks real predictions. Build three also deployed and verified a local API. Its registry-publishing and Kubernetes-deployment stages were skipped, so I do not claim those were demonstrated.
>
> Airflow runs the regression tasks in order: validate the data, train and evaluate, then approve a passing candidate. The screenshot shows all three tasks succeeding. A weekly schedule is configured, but the successful demonstration run was triggered manually.
>
> MLflow records parameters, metrics, model versions and artifacts. It helps compare experiments and trace a result back to a training run.
>
> These are captured execution results. A new Airflow candidate still requires review before release. Training a new model does not automatically replace the public version.

## 6. Recommendation Layer, App Interface and Monitoring — guideline 2:00; maximum 2:30

**SHOW:** Public app Hotel explorer. Choose a broad destination option and a budget that returns results; click Suggest stays. Then show the Insights page. Use the actual labels visible in the app.

**REMEMBER:** History → ranking; new user → popularity; interface → API; outcomes → improvement.

> The recommendation model uses hotel booking history as a preference signal. For a known user, it considers how often they booked each hotel and hotels with similar booking patterns.
>
> If the user has no training history, the system falls back to popular hotels. Destination and budget choices filter the available results. These are historical prices, not current room availability.
>
> I evaluated the ranking using Recall at three and NDCG at three. In simple terms, these check whether relevant hotels appear in the top three and whether they appear near the top. The selected model improved modestly over popularity on the held-out bookings.
>
> Because there is only one hotel per destination, selecting a specific city may leave only one option. I explain that as a catalogue lookup rather than claiming a rich ranking within that city.
>
> Streamlit gives users a simple way to interact with these models. They can request flight estimates, explore hotels and view measured model results. The interface calls Flask instead of maintaining a separate copy of the prediction logic.
>
> For monitoring, the API records response time and errors. Historical drift reports compare data patterns. To measure whether predictions remain useful, we would also need actual later prices, bookings or other outcomes. A drift score alone is not an accuracy score.

## 7. Reliability, Challenges and Optimization — guideline 1:30; maximum 2:00

**SHOW:** GitHub folder structure → `docs/evidence/jenkins-console.txt` at “13 passed” → `models/flights.json` with version and checksum. Keep secret files closed.

**REMEMBER:** Data relationships → dependencies → paths → tests → traceability.

> The main challenges came from connecting the components reliably.
>
> With multiple datasets, I had to check relationships and avoid duplicated records after joins. In the API, I needed to reject invalid inputs instead of producing misleading results.
>
> The first container check caught a missing dependency used by a saved artifact. I fixed the dependency and repeated the checks. An Airflow run also failed because a relative code path was resolved from a different working directory. I fixed the path and reran the workflow successfully.
>
> I improved the structure by keeping shared data processing and model code in one package. The notebooks, API and training workflow reuse that logic. I also excluded identifiers from prediction features and kept preprocessing with the model.
>
> Thirteen automated tests passed in the demonstrated Jenkins build. The project also checks model readiness and artifact checksums. GitHub records code changes, while model versions and request IDs support tracing results.
>
> These choices make the project easier to repeat, debug and maintain. Kubernetes adds a way to manage serving replicas, although the demonstrated scaling was manual.

## 8. Learnings and Future Improvements — guideline 1:30; maximum 2:00

**SHOW:** Architecture image, then end on the GitHub README with the project URL visible.

**REMEMBER:** Training is one step → reliable system → next improvements.

> My biggest learning is that training a model is only one part of building a machine learning system.
>
> A notebook can show a good score. A usable application also needs consistent preprocessing, input validation, dependency management, testing, deployment and monitoring. Each connection has to work, not just the model itself.
>
> I also learned to separate the responsibilities of the tools. Airflow organizes training work, Jenkins checks and releases software, and MLflow records experiments. They support each other, but they are not interchangeable.
>
> Future improvements include stronger live monitoring and accuracy checks using real outcomes. I would also improve the retraining and approval process, add authentication, and expand the hotel catalogue so recommendations have more meaningful choices.
>
> On the deployment side, I would verify automatic Kubernetes scaling, complete the Kubernetes release pipeline, and improve cloud reliability. Newer travel data would be necessary before claiming real-world pricing performance.
>
> This project connects data, models and a user-facing application with a tested MLOps workflow. The repository includes the code, notebooks, reports and execution evidence. Thank you for watching.

**ACTION:** Leave the repository visible for three seconds, then stop. Do not add a long unplanned demonstration after the conclusion.

## Interview preparation — separate from the main recording

### How would you productionize an ML model for real-time travel pricing?

> I would save the fitted preprocessing and model together, expose them through an API, validate inputs and test the complete prediction path. I would package the application, deploy a versioned release, monitor latency and errors, and collect actual outcomes to check accuracy. A real pricing service would also need fresh data and clear response-time requirements.

### Why did you use Docker and Kubernetes?

> Docker packages the application and its dependencies. Kubernetes manages running copies, checks their readiness and supports scaling. Docker helps reproduce the environment; Kubernetes helps operate multiple instances.

### How does MLflow help manage model versions?

> MLflow connects each training run with its parameters, metrics and artifacts. This makes models easier to compare and trace. The serving application still needs an explicit approved version; the newest experiment should not automatically become the live model.

### How would you handle model retraining in production?

> I would validate a new data snapshot, run training through Airflow, compare the candidate with the current approach and check its quality. A passing candidate would go through review and release tests before deployment. The previous release should remain available if the new one needs to be rolled back.

### How would you scale this for a large travel platform?

> I would first measure traffic, latency and memory use to find the bottleneck. Then I would tune serving workers, add replicas, test load balancing and configure autoscaling using observed metrics. I would keep training separate from prediction traffic and validate performance with representative load tests.

## Eight-line memory card

1. Introduction: What I built, who it serves, and which tools I used.
2. Problem: Why predictions need a usable and maintainable application.
3. Data: Users for labels, flights for prices, hotels for suggestions.
4. Models: Compare, evaluate, save, then serve through Flask.
5. MLOps: Docker packs; Kubernetes manages; Jenkins releases; Airflow schedules; MLflow records.
6. App: Users enter preferences, the API returns results, and outcomes guide improvement.
7. Reliability: Fix connections, share code, test behavior, trace versions.
8. Learning: A good model needs a reliable system around it.
