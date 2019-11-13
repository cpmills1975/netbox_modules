pipeline {
    agent none
    stages {
        stage('Clone netbox') {
            agent any
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
                docker {
                    image 'python:3'
                    args '-u 0:0'
                }
            }
            steps {
                sh 'pip install -U pip'
                sh 'pip install pytest==4.6.5 pytest-mock pytest-xdist jinja2 PyYAML black==19.3b0'
                sh 'pip install pynetbox==4.0.6 cryptography codecov'
                sh 'pip install jmespath'
                dir('ansible') {
                    git branch: 'stable-2.9', url: 'https://github.com/ansible/ansible.git'
                    sh '. hacking/env-setup'
                    sh 'ansible --version'
                }
            }
        }
    }
}
