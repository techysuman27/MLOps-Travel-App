# Recording preparation and local demo guide

The public app and public API run independently of your laptop. Airflow, Jenkins and Kubernetes are local demonstrations. Start Docker Desktop before using them. Keep passwords, local configuration files and unrelated browser tabs out of the recording.

## Pages to show

| Purpose | Page |
|---|---|
| Public application | https://voyage-analytics-suman.streamlit.app/ |
| Public API readiness | https://voyage-analytics-api-kqju.onrender.com/health/ready |
| Jenkins | http://127.0.0.1:8081/job/Voyage-Travel-CI/ |
| Jenkins-deployed local API | http://127.0.0.1:18081/health/ready |
| Airflow | http://127.0.0.1:8080/ |
| Scheduled training MLflow | http://127.0.0.1:15000/ |
| Original modeling MLflow, when started separately | http://127.0.0.1:5000/ |

Jenkins build 3 succeeded with 13 tests, image build, smoke checks and local deployment. Its registry-push and Kubernetes-CD stages were skipped. Airflow's successful manual run completed at 10:00 IST on 12 October 2026. The weekly schedule is configured, but the successful run was manually triggered. The earlier failed runs remain available for discussing debugging.

## Restore the local operational demonstration

Run these from the repository directory, after Docker Desktop is ready:

```powershell
docker start voyage-jenkins
docker compose -f compose.yaml -f compose.ops-local.yaml --profile ops up -d --no-build postgres mlflow airflow
docker start voyage-api-release
.venv/Scripts/python.exe scripts/smoke_test.py --url http://127.0.0.1:18081
```

These commands reuse this machine's existing containers, images and volumes. On a fresh machine, follow the repository setup instructions first. Allow the operational services a few minutes to start. The local Jenkins username is `voyage-admin`; its password is in the ignored `artifacts-local/jenkins-admin-password` file. The Airflow demo username is `admin`; its local credential file is `artifacts-local/airflow-passwords.json`. Open those files privately if needed; never upload or record them.

To run a new Jenkins demonstration from this machine:

```powershell
.venv/Scripts/python.exe scripts/jenkins_demo.py build --local-deploy
.venv/Scripts/python.exe scripts/jenkins_demo.py status
```

The script uses local credentials without printing them. A new run tests the current GitHub revision and produces a new image tag. Select the Airflow DAG and use its Trigger control to demonstrate a new candidate; it does not update the public model.

## Kubernetes segment

This laptop's Docker allocation is approximately 4 GB. For a live Kubernetes segment, stop the operational demo containers to free memory, then start `voyage-control-plane`. Preserve all volumes. Use the project-specific kubeconfig for every cluster command:

```powershell
docker stop voyage-jenkins almabettermasterproject-airflow-1 almabettermasterproject-mlflow-1
docker start voyage-control-plane
kubectl --kubeconfig artifacts-local/kubeconfig -n voyage get pods
kubectl --kubeconfig artifacts-local/kubeconfig -n voyage scale deployment/voyage-api --replicas=2
kubectl --kubeconfig artifacts-local/kubeconfig -n voyage rollout status deployment/voyage-api
kubectl --kubeconfig artifacts-local/kubeconfig -n voyage scale deployment/voyage-api --replicas=3
kubectl --kubeconfig artifacts-local/kubeconfig -n voyage rollout status deployment/voyage-api
```

The evidence in `docs/evidence/kubernetes-rollout.txt` already records the verified transition. Explain this as manual scaling. Automatic HPA behavior and Jenkins-to-Kubernetes release have not been demonstrated. Stop the project cluster before restoring the operational stack on this small machine.

## Submission

Use the public Drive folder for the Project link, and your recorded video link for the Video link. Follow [the word-for-word recording script](recording_script_30_minutes.md), prepared for your updated maximum of 30 minutes. It specifies what to open and what to say, with a target of 25–28 minutes including navigation. The older `video_walkthrough.md` is retained as an extended outline, not the current recording plan. Record a short microphone/readability test first, then record your own explanation. The video is the remaining student-created submission artifact.
