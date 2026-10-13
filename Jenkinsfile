
pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'master',
                    url: 'https://github.com/Krishnapriyait/UptimeMonitoring.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"C:\\Users\\krish\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" build -t pulseops-ci .'
            }
        }

        stage('Run Pytest') {
            steps {
                bat '"C:\\Users\\krish\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run --rm pulseops-ci python -m pytest test_app.py'
            }
        }

        stage('Deploy Container') {
            steps {
                bat '"C:\\Users\\krish\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" rm -f pulseops-ansible'
                bat '"C:\\Users\\krish\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" run -d --name pulseops-ansible -p 5000:5000 -v pulseops_data:/app/data pulseops-ci'
            }
        }
    }

    post {
        success {
            echo 'PulseOps CI/CD Pipeline Completed Successfully!'
        }
    }
}
