pipeline {
    agent any

    environment {
        // Καλούμε τα credentials που αποθηκεύσαμε πριν με το ID τους
        GITHUB_CREDS = credentials('github-creds')
        REGISTRY_IMAGE = 'stratologia-api:latest'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Τράβηγμα κώδικα από το GitHub...'
                // Κατεβάζει τον κώδικα από το Main branch σου
                git branch: 'main', url: 'https://github.com/giannoskom/stratologia-devops.git', credentialsId: 'github-creds'
            }
        }

        stage('2. Syntax & Build Check') {
            steps {
                echo 'Έλεγχος συντακτικού της Python...'
                // Ο Jenkins τρέχει ένα γρήγορο compile check για να δει αν ξέχασες άνω-κάτω τελείες
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('3. Docker Package') {
            steps {
                echo '🐳 Δοκιμαστικό χτίσιμο του Docker Image...'
                // Ελέγχει αν το Dockerfile σου είναι σωστά γραμμένο και κάνει build το image
                sh 'docker build -t ${REGISTRY_IMAGE} .'
            }
        }
    }
}