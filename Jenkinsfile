pipeline {
    agent any
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'master', url: 'https://github.com/Jayasree273/DigitalCanteen.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t pulseops-ci .'
            }
        }
        stage('Run Pytest') {
            steps {
                bat 'docker run --rm pulseops-ci python -m pytest test_app.py'
            }
        }
        stage('Deploy Container') {
            steps {
                bat 'docker rm -f pulseops-ansible || true'
                bat 'docker run -d --name pulseops-ansible -p 5000:5000 -v pulseops_data:/app/data pulseops-ci'
            }
        }
    }
    post {
        success {
            echo 'PulseOps CI/CD Pipeline Completed Successfully!'
        }
    }
}