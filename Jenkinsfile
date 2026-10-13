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
                sh 'docker build -t pulseops-ci .'
            }
        }
        stage('Run Pytest') {
            steps {
                sh 'docker run --rm pulseops-ci python -m pytest test_app.py'
            }
        }
        stage('Deploy via Ansible') {
            steps {
                sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock pulseops-ci python app.py & || true'
            }
        }
    }
    post {
        success {
            echo 'PulseOps CI/CD Pipeline Completed Successfully!'
        }
    }
}