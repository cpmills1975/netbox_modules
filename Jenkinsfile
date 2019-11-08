pipeline {
    agent any
    stages {
        stage('Clone netbox') {
            steps {
                git url: 'https://github.com/FragmentedPacket/netbox-docker.git'
            }
        }
    }
}
