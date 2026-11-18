// MIDTERM-FA23-BDS-057 : GitHub push -> retrain -> test -> Docker build -> deploy on EC2 -> e-mail
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    // Fires on the GitHub webhook (http://<EC2>:8080/github-webhook/).
    // pollSCM is only a safety net in case a webhook delivery is ever lost.
    triggers {
        githubPush()
        pollSCM('H/2 * * * *')
    }

    environment {
        STUDENT_ID = 'FA23-BDS-057'
        IMAGE      = 'midterm-api'
        CONTAINER  = 'midterm-api'
        MAIL_TO    = 'qasimalik@gmail.com'
    }

    stages {
        stage('Fetch latest data') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                }
                sh 'echo "Building commit $GIT_COMMIT"; wc -l dataset/train.csv; cat config.json'
            }
        }

        stage('Build image (runs train.py)') {
            steps {
                sh '''
                    docker build --build-arg GIT_COMMIT=$GIT_COMMIT \
                        -t $IMAGE:$GIT_COMMIT -t $IMAGE:latest .
                '''
            }
        }

        stage('Test') {
            steps {
                sh 'docker run --rm $IMAGE:$GIT_COMMIT python -m pytest -q tests'
                sh 'docker run --rm $IMAGE:$GIT_COMMIT cat artifacts/metrics.json'
            }
        }

        stage('Deploy on EC2') {
            steps {
                sh '''
                    docker rm -f $CONTAINER 2>/dev/null || true
                    docker run -d --name $CONTAINER --restart unless-stopped -p 8000:8000 $IMAGE:$GIT_COMMIT
                    for i in $(seq 1 30); do
                        if curl -fs http://localhost:8000/metrics | grep -q "$GIT_COMMIT"; then
                            echo "Deployed commit $GIT_COMMIT:"; curl -s http://localhost:8000/metrics; echo
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "New container did not serve commit $GIT_COMMIT"; docker logs $CONTAINER | tail -30; exit 1
                '''
            }
        }
    }

    post {
        always {
            script {
                env.STATUS = currentBuild.currentResult
                try {
                    withCredentials([usernamePassword(credentialsId: 'gmail-smtp',
                                                      usernameVariable: 'SMTP_USER',
                                                      passwordVariable: 'SMTP_PASS')]) {
                        sh 'python3 scripts/notify.py'
                    }
                } catch (err) {
                    echo "E-mail step failed: ${err}"
                }
            }
            sh 'docker image prune -f >/dev/null 2>&1 || true'
        }
    }
}
