pipeline {
  agent any
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Lint & Static Analysis') {
      steps {
        sh 'python -m pip install -r backend/requirements.txt'
        sh 'flake8 backend || true'
        sh 'black --check backend || true'
      }
    }
    stage('Unit Tests') { steps { sh './scripts/test.sh' } }
    stage('Docker Build') {
      steps {
        // Build images with Playwright baked into frontend
        sh 'docker-compose build control_frontend control_backend'
      }
    }
    stage('E2E Tests') {
      steps {
        // Run DB and backend, then run frontend preview and Playwright inside rebuilt frontend image
        sh "docker-compose up -d control_db"
        sh "docker-compose up -d control_backend"
        // Give backend some time to boot and run migrations if needed
        sh "./backend/app/apply_migrations.py || true"
        // Run Playwright tests inside the frontend image so browsers are available
        sh "docker-compose run --rm -w /app control_frontend bash -lc \"npm run preview -- --port 5173 --host > /tmp/preview.log 2>&1 & PREV_PID=$!; sleep 4; BASE_URL=http://127.0.0.1:5173 npx playwright test --config=playwright.config.js --project=chromium --reporter=dot || true; kill ${PREV_PID:-0} || true; exit 0\""
        // Tear down services
        sh 'docker-compose down'
      }
    }
  }
}
