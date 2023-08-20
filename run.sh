# brew uninstall awscli
# brew install awscli

# 1. Push Docker Image to ECR

aws ecr create-repository --repository-name text-audio-ecs

# aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 897527378750.dkr.ecr.us-east-1.amazonaws.com

docker build -t text-audio-ecs .

docker tag text-audio-ecs:latest 897527378750.dkr.ecr.us-east-1.amazonaws.com/text-audio-ecs:latest

docker push 897527378750.dkr.ecr.us-east-1.amazonaws.com/text-audio-ecs:latest

# # 2. Set Up ECS Cluster

# # Create a new ECS cluster:
aws ecs create-cluster --cluster-name text-audio-ecs-cluster


# # 3. Create ECS Task Definition:
# # see attached ecs-task-definition.json

# # 4. Register the task definition with ECS:

aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# # 5. Create an EC2 Launch Template:

aws iam create-role --role-name ecsInstanceRole --assume-role-policy-document file://ecs-trust-policy.json

aws iam attach-role-policy --role-name ecsInstanceRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role

aws iam create-instance-profile --instance-profile-name ecsInstanceRole
aws iam add-role-to-instance-profile --role-name ecsInstanceRole --instance-profile-name ecsInstanceRole

aws ssm get-parameter --name /aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id --region us-east-1 --query "Parameter.Value" --output text


aws ec2 create-launch-template \
    --launch-template-name text-audio-ecs-launch-template-$(date +%s) \
    --version-description version1 \
    --launch-template-data '{
        "InstanceType": "t2.micro",
        "UserData": "'$(echo '#!/bin/bash\necho ECS_CLUSTER=text-audio-ecs-cluster >> /etc/ecs/ecs.config' | base64)'",
        "ImageId": "ami-0e13330257b20a8e4",
        "IamInstanceProfile": {
            "Name": "ecsInstanceRole"
        }
    }'


# # 6. Create an EC2 Auto Scaling group:

#change the template name

aws ec2 describe-launch-templates --query 'LaunchTemplates[?LaunchTemplateName==`text-audio-ecs-launch-template-1692561618`]'

aws autoscaling create-auto-scaling-group \
    --region us-east-1 \
    --auto-scaling-group-name text-audio-ecs-asg \
    --launch-template LaunchTemplateName=text-audio-ecs-launch-template-1692561618,Version=1 \
    --min-size 1 \
    --max-size 3 \
    --desired-capacity 1 \
    --availability-zones us-east-1a us-east-1b




# # 7. Launch the service:

aws ecs create-service --cluster text-audio-ecs-cluster --service-name text-audio-ecs-service --task-definition text-audio-ecs --desired-count 1 --launch-type EC2 --scheduling-strategy REPLICA
