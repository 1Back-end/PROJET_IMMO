pipeline {
    agent any
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Clone repository') {
            steps {
                script {
                    sh 'printenv'
                    echo 'Pulling...' + env.BRANCH_NAME
                    checkout scm
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    slackSend(message: "${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)\nBuild commencé", channel: "lawtechnology-crm")
                    if (env.BRANCH_NAME == 'master') {
                        app = docker.build("registry.gitlab.com/lawtechnology/ems/api:latest")
                    } else {
                        app = docker.build("registry.gitlab.com/lawtechnology/ems/api:" + env.BRANCH_NAME)
                    }
                }
            }
        }
        stage('Test') {
            steps {
                echo 'Empty...'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    docker.withRegistry('https://registry.gitlab.com/lawtechnology/ems/api', 'gitlab_username_password') {
                        if (env.BRANCH_NAME == 'master') {
                            app.push("latest")
                        } else {
                            app.push(env.BRANCH_NAME)
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            slackSend(color: "good", message: "${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)\nBuild effectué avec succès", channel: "lawtechnology-crm")
        }
        failure {
            slackSend(failOnError: true, message: "${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)\nÉchec de build", channel: "lawtechnology-crm")
        }
    }
}
