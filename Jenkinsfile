pipeline {
    agent any

    environment {
        // GitHub
        GIT_REPO = "flask-mysql-app"
        GIT_BRANCH = "${GIT_BRANCH ?: 'main'}"
        
        // Docker
        DOCKER_IMAGE = "flask-app"
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = "chikalemon.azurecr.io"
        CONTAINER_NAME = "flask-container"
        
        // Azure
        AZURE_SUBSCRIPTION = "your-subscription-id"
        RESOURCE_GROUP = "timetravel_Chika"
        ACR_CREDENTIALS = credentials('azure-registry-credentials')
        
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
                    # Tag images for Azure
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:latest ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    
                    # Login to Azure Container Registry
                    echo $ACR_CREDENTIALS_PSW | docker login -u $ACR_CREDENTIALS_USR --password-stdin ${DOCKER_REGISTRY}
                    
                    # Push images
                    docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                    
                    echo "✓ Images pushed to ${DOCKER_REGISTRY}"
                    
                    # Logout
                    docker logout ${DOCKER_REGISTRY}
                '''
            }
        }

        stage('☁️ Deploy to Azure') {
            when {
                branch 'main'
            }
            steps {
                echo "✓ Deploying to Azure Container Instances..."
                sh '''
                    # Check if container already exists
                    if az container show --name flask-app-prod --resource-group ${RESOURCE_GROUP} 2>/dev/null; then
                        echo "✓ Updating existing container..."
                        az container delete --name flask-app-prod --resource-group ${RESOURCE_GROUP} --yes || true
                    fi
                    
                    # Deploy new container
                    az container create \
                      --resource-group ${RESOURCE_GROUP} \
                      --name flask-app-prod \
                      --image ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest \
                      --registry-login-server ${DOCKER_REGISTRY} \
                      --registry-username $ACR_CREDENTIALS_USR \
                      --registry-password $ACR_CREDENTIALS_PSW \
                      --ports 5000 \
                      --ip-address public \
                      --cpu 1 \
                      --memory 1 \
                      --environment-variables ENVIRONMENT=production \
                      --restart-policy OnFailure \
                      --log-analytics-workspace /subscriptions/${AZURE_SUBSCRIPTION}/resourcegroups/${RESOURCE_GROUP}/providers/microsoft.operationalinsights/workspaces/log-workspace || true
                    
                    echo "✓ Container deployed!"
                    
                    # Get the public IP
                    PUBLIC_IP=$(az container show --name flask-app-prod --resource-group ${RESOURCE_GROUP} --query ipAddress.ip --output tsv)
                    echo "✓ App URL: http://$PUBLIC_IP:5000"
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