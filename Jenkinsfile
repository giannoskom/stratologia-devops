pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "giannoskomninos/stratologia-api"
        TAG = "latest"
    }

    stages {
        stage('1. Κατέβασμα Κώδικα (Checkout)') {
            steps {
                echo '=== [Stage 1] Pulling latest code from GitHub ==='
                checkout scm
            }
        }

        stage('2. Χτίσιμο Εικόνας (Docker Build)') {
            steps {
                echo '=== [Stage 2] Building Docker Image ==='
                sh 'docker build -t ${DOCKER_IMAGE}:${TAG} .'
            }
        }

        stage('3. Αποστολή στο Cloud (Docker Push)') {
            steps {
                echo '=== [Stage 3] Pushing to DockerHub ==='
                sh 'docker push ${DOCKER_IMAGE}:${TAG}'
            }
        }

        stage('4. Εγκατάσταση στο Kubernetes (Ansible Deploy)') {
            steps {
                echo '=== [Stage 4] Running Ansible Playbook ==='
                sh 'ansible-playbook -i ansible/inventory.ini ansible/playbook.yml'
            }
        }
    }
    
    post {
        success {
            echo '🎉 ΕΠΙΤΥΧΙΑ: Το νέο API χτίστηκε και είναι Live στο Microk8s!'
        }
        failure {
            echo '❌ ΑΠΟΤΥΧΙΑ: Το Pipeline έσκασε. Δείτε τα Console Output logs.'
        }
    }
}