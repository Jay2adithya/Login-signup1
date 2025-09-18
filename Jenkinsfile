pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        CSV_FILE = 'data.csv' // Update this if your CSV filename/path is different
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url:'https://github.com/Jay2adithya/Login-signup1.git' // Change if needed
            }
        }

        stage('Set Up Python Environment') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install pandas numpy scipy
                '''
            }
        }

        stage('Run CSV Metrics Script') {
            steps {
                echo '📊 Running script to calculate CSV metrics...'
                sh '''
                    . $VENV_DIR/bin/activate
                    python3 validate_csv.py "$CSV_FILE"
                '''
            }
        }
    }

    post {
        success {
            echo ' Build succeeded!'
        }
        failure {
            echo ' Build failed. Check Console Output for errors.'
        }
    }
}
