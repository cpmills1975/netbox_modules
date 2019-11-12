pipeline {
    agent any
    stages {
        stage('Clone netbox') {
            steps {
                dir('netbox-docker') {
                    git url: 'https://github.com/FragmentedPacket/netbox-docker.git'
                    sh 'git checkout startup-dcim-interfaces-2.5'
                    sh 'docker-compose pull'
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Clone Ansible') {
            agent {
                docker { image 'python:3.6' }
            }
            steps {
                sh 'python -c "print('Hello World!')"'
            }
        }
    }
}
