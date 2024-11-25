pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t samgeo-project .'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'docker run --rm samgeo-project python3 -m unittest discover tests'
            }
        }
        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-registry', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]) {
                    sh '''
                        echo "$PASSWORD" | docker login -u "$USER" --password-stdin
                        docker tag samgeo-project your-registry/samgeo-project:latest
                        docker push your-registry/samgeo-project:latest
                    '''
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f k8s-deployment.yaml'
            }
        }
    }
}
