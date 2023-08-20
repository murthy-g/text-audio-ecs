# check if service exists
aws ecs describe-services --cluster text-audio-ecs-cluster --services text-audio-ecs-service

# update service
aws ecs update-service --cluster text-audio-ecs-cluster --service text-audio-ecs-service --task-definition text-audio-ecs


# delete and recreate service
aws ecs delete-service --cluster text-audio-ecs-cluster --service text-audio-ecs-service --force
aws ecs create-service --cluster text-audio-ecs-cluster --service-name text-audio-ecs-service --task-definition text-audio-ecs --desired-count 1 --launch-type EC2 --scheduling-strategy REPLICA
