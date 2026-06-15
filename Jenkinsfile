pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/ShreeStyle/2-tire-web-app-Jenkins-Docker.git'
            }
        }

        stage('Build Image') {
            steps {
                sh '/opt/homebrew/bin/docker build -t flask-app .'
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                /opt/homebrew/bin/docker rm -f flask-container || true

                /opt/homebrew/bin/docker run -d \
                  --name flask-container \
                  -p 5000:5000 \
                  flask-app
                '''
            }
        }
    }
}