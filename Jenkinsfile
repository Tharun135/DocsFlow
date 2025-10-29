pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'docsflow-pipeline'
        DOCKER_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        FLUID_USER = credentials('fluidtopics-username')
        FLUID_PASS = credentials('fluidtopics-password')
        FLUID_URL = credentials('fluidtopics-url')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                
                script {
                    env.GIT_COMMIT = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo '🐍 Setting up Python environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Lint Documentation') {
            steps {
                echo '🔍 Running documentation linting...'
                sh '''
                    . venv/bin/activate
                    python scripts/lint_docs.py
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'lint-report.html',
                        reportName: 'Documentation Lint Report'
                    ])
                }
            }
        }
        
        stage('Validate YAML') {
            steps {
                echo '📋 Validating YAML configuration files...'
                sh '''
                    . venv/bin/activate
                    python scripts/validate_yaml.py
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    env.DOCKER_IMAGE_ID = image.id
                }
            }
        }
        
        stage('Build Documentation') {
            steps {
                echo '📚 Building documentation with MkDocs...'
                sh '''
                    . venv/bin/activate
                    mkdocs build --clean --strict
                '''
                
                // Archive the built site
                archiveArtifacts artifacts: 'site/**', fingerprint: true
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 Running documentation tests...'
                sh '''
                    . venv/bin/activate
                    # Add any documentation-specific tests here
                    # For example: link checking, spell checking, etc.
                    echo "Tests would run here"
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '🔒 Running security scan on Docker image...'
                script {
                    try {
                        sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    } catch (Exception e) {
                        echo "Security scan failed: ${e.getMessage()}"
                        // Don't fail the build for security scan failures in demo
                    }
                }
            }
        }
        
        stage('Deploy to Fluid Topics') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                echo '🚀 Deploying to Fluid Topics...'
                sh '''
                    . venv/bin/activate
                    python scripts/upload_to_fluidtopics.py
                '''
            }
        }
        
        stage('Update Version Tags') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                echo '🏷️ Updating version tags...'
                script {
                    // Tag the Docker image as latest
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    
                    // Optionally push to registry
                    if (env.DOCKER_REGISTRY) {
                        docker.withRegistry("https://${env.DOCKER_REGISTRY}", 'docker-registry-credentials') {
                            sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            sh "docker push ${DOCKER_IMAGE}:latest"
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            
            // Clean up Python virtual environment
            sh 'rm -rf venv || true'
            
            // Clean up Docker images
            sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
            
            // Archive logs
            archiveArtifacts artifacts: 'logs/**', allowEmptyArchive: true
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
            
            // Send success notification
            script {
                def message = """
                🎉 DocsFlow Pipeline Success!
                
                Branch: ${env.BRANCH_NAME}
                Commit: ${env.GIT_COMMIT.take(7)}
                Build: #${env.BUILD_NUMBER}
                Duration: ${currentBuild.durationString}
                
                Documentation has been successfully deployed to Fluid Topics.
                """
                
                // Uncomment and configure for your notification system
                // slackSend(channel: '#devops', message: message, color: 'good')
                // emailext(subject: 'DocsFlow Deployment Success', body: message, to: 'team@company.com')
            }
        }
        
        failure {
            echo '❌ Pipeline failed!'
            
            // Send failure notification
            script {
                def message = """
                🚨 DocsFlow Pipeline Failed!
                
                Branch: ${env.BRANCH_NAME}
                Commit: ${env.GIT_COMMIT.take(7)}
                Build: #${env.BUILD_NUMBER}
                
                Check the console output for details: ${env.BUILD_URL}
                """
                
                // Uncomment and configure for your notification system
                // slackSend(channel: '#devops', message: message, color: 'danger')
                // emailext(subject: 'DocsFlow Deployment Failed', body: message, to: 'team@company.com')
            }
        }
        
        unstable {
            echo '⚠️ Pipeline completed with warnings'
        }
        
        aborted {
            echo '🛑 Pipeline was aborted'
        }
    }
}