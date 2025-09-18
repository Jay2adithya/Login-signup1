pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        CSV_FILE = 'uploads/csv.csv'
    }

    stages {
        stage('Install Python') {
            steps {
                echo '🔧 Installing Python and pip...'
                sh '''
                    apt-get update
                    apt-get install -y python3 python3-pip python3-venv
                '''
            }
        }

        stage('Set Up Python Environment') {
            steps {
                echo '🐍 Creating virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install pandas numpy scipy
                '''
            }
        }

        stage('Run CSV Script') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    python3 validate_csv.py $CSV_FILE
                '''
            }
        }
    }

    post {
        success {
            echo '✅ CSV script ran successfully.'
        }
        failure {
            echo '❌ Build failed.'
        }
    }
}
