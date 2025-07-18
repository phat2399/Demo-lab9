pipeline {
    agent any
    environment {
        AWS_ACCOUNT_ID      = "927875589544"
        AWS_DEFAULT_REGION  = "ap-southeast-1"
        ECR_REPOSITORY_NAME = "demolab8" // Hoặc tên repo ECR của bạn
        EKS_CLUSTER_NAME    = "lab9-eks-cluster"
    }
    stages {
        stage('Checkout') {
            steps {
                // Lấy code từ GitHub
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                echo 'Building the Docker image...'
                sh "docker build -t ${ECR_REPOSITORY_NAME}:latest ."
            }
        }
        stage('Push to Amazon ECR') {
            steps {
                // Nạp AWS credentials một cách an toàn
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials-lab']]) {
                    script {
                        def ecrUri = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest"
                        sh "docker tag ${ECR_REPOSITORY_NAME}:latest ${ecrUri}"
                        sh "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
                        sh "docker push ${ecrUri}"
                    }
                }
            }
        }
        stage('Deploy to EKS') {
            steps {
                // Nạp credentials để ra lệnh cho EKS
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials-lab']]) {
                    script {
                        sh "aws eks --region ${AWS_DEFAULT_REGION} update-kubeconfig --name ${EKS_CLUSTER_NAME}"
                        // Áp dụng các file cấu hình Kubernetes
                        sh "kubectl apply -f deployment.yaml"
                        sh "kubectl apply -f service.yaml"
                    }
                }
            }
        }
    }
}