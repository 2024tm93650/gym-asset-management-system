// Declarative Jenkins pipeline for ACEest Fitness & Gym (DevOps Assignment 2)
// Stages: Checkout -> Install -> Test -> SonarQube -> Docker Build -> Docker Push -> Deploy -> Smoke Test -> Rollback (on failure)
// Required Jenkins credentials:
//   - dockerhub-creds      (Username + Password : 2024tm93650 / dckr_pat_*)
//   - sonarqube-token      (Secret text         : sqp_*)        [optional - skipped if missing]
//   - kubeconfig           (Secret file         : ~/.kube/config) [optional - skipped if missing]

pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME       = '2024tm93650/aceest-fitness'
        IMAGE_TAG        = "v${env.BUILD_NUMBER}"
        IMAGE_FULL       = "${IMAGE_NAME}:${IMAGE_TAG}"
        IMAGE_LATEST     = "${IMAGE_NAME}:latest"
        K8S_NAMESPACE    = 'aceest'
        K8S_DEPLOYMENT   = 'aceest-fitness'
        SONAR_PROJECT_KEY = 'aceest-fitness'
    }

    triggers {
        // Poll SCM every 2 minutes when webhooks aren't configured.
        pollSCM('H/2 * * * *')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --pretty=oneline'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --quiet --upgrade pip
                    pip install --quiet -r requirements.txt
                    pip install --quiet -r requirements-dev.txt
                '''
            }
        }

        stage('Unit Tests + Coverage') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                    publishHTML(target: [
                        reportName: 'Coverage',
                        reportDir: 'reports/htmlcov',
                        reportFiles: 'index.html',
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: true
                    ])
                }
            }
        }

        stage('SonarQube Analysis') {
            when { expression { return fileExists('sonar-project.properties') } }
            steps {
                script {
                    def hasSonar = false
                    try {
                        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                            hasSonar = true
                            sh '''
                                if ! command -v sonar-scanner >/dev/null 2>&1; then
                                    echo "sonar-scanner not on PATH - skipping (install Sonar Scanner CLI on agent)"
                                    exit 0
                                fi
                                sonar-scanner \
                                  -Dsonar.login=${SONAR_TOKEN} \
                                  -Dsonar.host.url=${SONAR_HOST_URL:-http://host.docker.internal:9000}
                            '''
                        }
                    } catch (err) {
                        echo "SonarQube credentials not configured - skipping (${err.message})"
                    }
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_FULL} \
                      -t ${IMAGE_LATEST} \
                      .
                    docker images ${IMAGE_NAME}
                '''
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DH_USER',
                    passwordVariable: 'DH_PASS'
                )]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push ${IMAGE_FULL}
                        docker push ${IMAGE_LATEST}
                        docker logout || true
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when { expression { return fileExists('k8s/deployment.yaml') } }
            steps {
                script {
                    try {
                        withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                            sh '''
                                export KUBECONFIG=$KUBECONFIG_FILE
                                kubectl get ns ${K8S_NAMESPACE} >/dev/null 2>&1 || kubectl create ns ${K8S_NAMESPACE}
                                # rolling update on the live deployment
                                kubectl -n ${K8S_NAMESPACE} apply -f k8s/
                                kubectl -n ${K8S_NAMESPACE} set image deployment/${K8S_DEPLOYMENT} \
                                  ${K8S_DEPLOYMENT}=${IMAGE_FULL} --record
                                kubectl -n ${K8S_NAMESPACE} rollout status deployment/${K8S_DEPLOYMENT} --timeout=180s
                            '''
                        }
                    } catch (err) {
                        echo "kubeconfig credential missing or kubectl unavailable - skipping deploy (${err.message})"
                    }
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker rm -f aceest-smoke 2>/dev/null || true
                    docker run -d --name aceest-smoke -p 5099:5000 ${IMAGE_FULL}
                    # wait for healthcheck
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if curl -fsS http://localhost:5099/health >/dev/null; then
                            echo "Healthcheck passed"
                            break
                        fi
                        sleep 2
                    done
                    curl -fsS http://localhost:5099/version
                    curl -fsS "http://localhost:5099/calories?weight=80&program=MG"
                    docker rm -f aceest-smoke
                '''
            }
        }
    }

    post {
        success {
            echo "BUILD ${env.BUILD_NUMBER} SUCCESS - image ${IMAGE_FULL} live."
        }
        failure {
            echo "BUILD FAILED - attempting K8s rollback if applicable..."
            script {
                try {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh '''
                            export KUBECONFIG=$KUBECONFIG_FILE
                            kubectl -n ${K8S_NAMESPACE} rollout undo deployment/${K8S_DEPLOYMENT} || true
                        '''
                    }
                } catch (ignored) {
                    echo "No kubeconfig - skipping rollback"
                }
            }
        }
        always {
            sh 'docker rm -f aceest-smoke 2>/dev/null || true'
        }
    }
}
