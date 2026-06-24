pipeline {
    agent any

    environment {
        GITHUB_CREDS = credentials('github-creds')
        REGISTRY_IMAGE = 'stratologia-api:latest'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Τράβηγμα κώδικα από το GitHub...'
                git branch: 'main', url: 'https://github.com/giannoskom/stratologia-devops.git', credentialsId: 'github-creds'
            }
        }

        stage('2. Syntax Check') {
            steps {
                echo 'Έλεγχος συντακτικού της Python...'
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('3. Docker Package') {
            steps {
                echo 'Δοκιμαστικό χτίσιμο του Docker Image...'
                sh 'docker build -t ${REGISTRY_IMAGE} .'
            }
        }
    }
}