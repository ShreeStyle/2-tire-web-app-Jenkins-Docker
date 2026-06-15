pipeline {
    agent any

    environment {
        PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }

    stages {

        stage('Build Image') {
            steps {
                sh 'docker build -t flask-app .'
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker rm -f flask-container || true

                docker run -d \
                  --name flask-container \
                  -p 5000:5000 \
                  flask-app
                '''
            }
        }
    }
}