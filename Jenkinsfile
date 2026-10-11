// Linux agent prerequisites: Python 3.13, Docker, kubectl and registry credentials.
pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  parameters {
    booleanParam(name: 'PUBLISH', defaultValue: false, description: 'Push tested API image to the configured registry')
    booleanParam(name: 'DEPLOY', defaultValue: false, description: 'Publish and roll out to the configured Kubernetes cluster')
    string(name: 'IMAGE_REPOSITORY', defaultValue: 'ghcr.io/techysuman27/voyage-api', description: 'Container repository you own')
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Dependencies') {
      steps { sh 'python3 -m venv .ci-venv && .ci-venv/bin/pip install -r requirements-ci.txt && .ci-venv/bin/pip install --no-deps .' }
    }
    stage('Tests') {
      steps { sh '.ci-venv/bin/python -m pytest -q --junitxml=reports/tests.xml' }
      post { always { junit 'reports/tests.xml' } }
    }
    stage('Build') {
      steps {
        script { env.RELEASE_TAG = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim() + '-' + env.BUILD_NUMBER }
        sh 'docker build -f docker/Dockerfile.api -t "$IMAGE_REPOSITORY:$RELEASE_TAG" .'
      }
    }
    stage('Container prediction check') {
      steps {
        sh '''
          set -eu
          container=$(docker run -d "$IMAGE_REPOSITORY:$RELEASE_TAG")
          trap 'docker rm -f "$container"' EXIT
          docker cp scripts/wait_ready.py "$container:/tmp/wait_ready.py"
          docker cp scripts/smoke_test.py "$container:/tmp/smoke_test.py"
          docker exec "$container" python /tmp/wait_ready.py --url http://127.0.0.1:8000
          docker exec "$container" python /tmp/smoke_test.py --url http://127.0.0.1:8000
        '''
      }
    }
    stage('Publish') {
      when { expression { params.PUBLISH || params.DEPLOY } }
      steps {
        withCredentials([usernamePassword(credentialsId: 'voyage-registry', usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_TOKEN')]) {
          sh '''
            set -eu
            registry=$(echo "$IMAGE_REPOSITORY" | cut -d/ -f1)
            printf '%s' "$REGISTRY_TOKEN" | docker login "$registry" -u "$REGISTRY_USER" --password-stdin
            docker push "$IMAGE_REPOSITORY:$RELEASE_TAG"
          '''
        }
      }
    }
    stage('Deploy and verify') {
      when { expression { params.DEPLOY } }
      steps {
        withCredentials([file(credentialsId: 'voyage-kubeconfig', variable: 'KUBECONFIG')]) {
          sh '''
            set -eu
            export RELEASE_IMAGE=$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE_REPOSITORY:$RELEASE_TAG")
            .ci-venv/bin/python scripts/render_deployment.py
            kubectl apply -f reports/release-deployment.yml
            kubectl -n voyage rollout status deployment/voyage-api --timeout=180s
            kubectl -n voyage port-forward service/voyage-api 18080:80 > reports/port-forward.log 2>&1 &
            pf=$!
            trap 'kill "$pf"' EXIT
            .ci-venv/bin/python scripts/wait_ready.py --url http://127.0.0.1:18080
            .ci-venv/bin/python scripts/smoke_test.py --url http://127.0.0.1:18080
          '''
        }
      }
    }
  }
  post { always { archiveArtifacts artifacts: 'reports/*.json,models/*.json', allowEmptyArchive: true } }
}
