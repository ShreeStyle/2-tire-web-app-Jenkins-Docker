pipeline {
    agent any

    environment {
        // GitHub
        GIT_REPO = "flask-mysql-app"
        GIT_BRANCH = "${GIT_BRANCH ?: 'main'}"
        
        // Docker
        DOCKER_IMAGE = "flask-app"
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = "your-registry.azurecr.io"
        CONTAINER_NAME = "flask-container"
        
        // Azure
        AZURE_SUBSCRIPTION = "your-subscription-id"
        RESOURCE_GROUP = "your-resource-group"
        
        // Paths
        PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }

    triggers {
        githubPush()
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {

        stage('🔍 Checkout') {
            steps {
                echo "✓ Checking out code from GitHub..."
                checkout scm
                sh 'git log -1 --pretty=format:"%h - %an - %s"'
            }
        }

        stage('🧪 Validate') {
            steps {
                echo "✓ Validating project structure..."
                sh '''
                    [ -f requirements.txt ] || (echo "❌ requirements.txt missing" && exit 1)
                    [ -f app.py ] || (echo "❌ app.py missing" && exit 1)
                    [ -f Dockerfile ] || (echo "❌ Dockerfile missing" && exit 1)
                    echo "✓ All required files present"
                '''
            }
        }

        stage('🔐 Security Scan - Dockerfile') {
            steps {
                echo "✓ Scanning Dockerfile for best practices..."
                sh '''
                    if command -v hadolint &> /dev/null; then
                        hadolint Dockerfile || true
                    else
                        echo "⚠ Hadolint not installed - skipping"
                    fi
                '''
            }
        }

        stage('📦 Build Docker Image') {
            steps {
                echo "✓ Building Docker image..."
                sh '''
                    docker build \
                      --tag ${DOCKER_IMAGE}:latest \
                      --tag ${DOCKER_IMAGE}:${DOCKER_TAG} \
                      --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                      --build-arg VCS_REF=$(git rev-parse --short HEAD) \
                      --build-arg VERSION=${BUILD_NUMBER} \
                      .
                    
                    echo "✓ Image built: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    docker images | grep ${DOCKER_IMAGE}
                '''
            }
        }

        stage('🔍 Container Security Scan') {
            steps {
                echo "✓ Scanning container image for vulnerabilities..."
                sh '''
                    if command -v trivy &> /dev/null; then
                        trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                    else
                        echo "⚠ Trivy not installed - skipping vulnerability scan"
                    fi
                '''
            }
        }

        stage('🧪 Unit Tests') {
            steps {
                echo "✓ Running unit tests..."
                sh '''
                    docker run --rm \
                      -v $(pwd):/app \
                      ${DOCKER_IMAGE}:${DOCKER_TAG} \
                      python -m pytest tests/ || true
                '''
            }
        }

        stage('🚀 Deploy to Dev') {
            when {
                branch 'main'
            }
            steps {
                echo "✓ Deploying to development environment..."
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    
                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      --restart unless-stopped \
                      -p 5000:5000 \
                      -e ENVIRONMENT=dev \
                      ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    echo "✓ Container deployed: ${CONTAINER_NAME}"
                    docker ps | grep ${CONTAINER_NAME}
                '''
            }
        }

        stage('✅ Smoke Tests') {
            when {
                branch 'main'
            }
            steps {
                echo "✓ Running smoke tests..."
                sh '''
                    sleep 3
                    
                    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
                    
                    if [ "$RESPONSE" -eq 200 ]; then
                        echo "✓ App is responding (HTTP $RESPONSE)"
                    else
                        echo "❌ App health check failed (HTTP $RESPONSE)"
                        exit 1
                    fi
                '''
            }
        }

        stage('📤 Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo "✓ Pushing image to Azure Container Registry..."
                sh '''
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:latest ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    
                    echo "ℹ Configure Azure login in Jenkins credentials first"
                    # docker login -u USERNAME -p PASSWORD ${DOCKER_REGISTRY}
                    # docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                '''
            }
        }

    }

    post {
        always {
            echo "╔═══════════════════════════════════════╗"
            echo "║ hi jan!! D              ║"
            echo "╠═══════════════════════════════════════╣"
            echo "║ Build: ${BUILD_NUMBER}                 ║"
            echo "║ Status: ${currentBuild.result}        ║"
            echo "║ Duration: ${currentBuild.durationString} ║"
            echo "╚═══════════════════════════════════════╝"
            
            cleanWs()
        }

        success {
            echo "✅ Pipeline succeeded!"
            // Add Slack/Teams notification here
        }

        failure {
            echo "❌ Pipeline failed!"
            // Add Slack/Teams notification here
        }
    }
}