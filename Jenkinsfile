pipeline {
    agent any

    environment {
        IMAGE_NAME = "acefitness"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Pulling latest code from GitHub..."
                checkout scm
            }
        }

        stage('Build Environment') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Lint') {
            steps {
                echo "Running flake8 lint checks..."
                sh """
                    docker run --rm \\
                        -v \$(pwd)/app.py:/app/app.py \\
                        ${IMAGE_NAME}:${IMAGE_TAG} \\
                        sh -c "pip install flake8 -q && flake8 app.py --max-line-length=100"
                """
            }
        }

        stage('Unit Tests') {
            steps {
                echo "Running Pytest suite inside Docker container..."
                sh """
                    docker build -t ${IMAGE_NAME}-test:${IMAGE_TAG} -f Dockerfile.test .
                    docker run --rm ${IMAGE_NAME}-test:${IMAGE_TAG} \\
                        pytest test_app.py -v --tb=short
                """
            }
        }

        stage('Quality Gate') {
            steps {
                echo "All stages passed. Image ${IMAGE_NAME}:${IMAGE_TAG} is validated."
            }
        }
    }

    post {
        success {
            echo "BUILD SUCCESSFUL — ${IMAGE_NAME}:${IMAGE_TAG} passed all quality gates."
        }
        failure {
            echo "BUILD FAILED — Check the logs above for errors."
        }
        always {
            sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true"
            sh "docker rmi ${IMAGE_NAME}-test:${IMAGE_TAG} || true"
        }
    }
}
