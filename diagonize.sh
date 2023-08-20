#!/bin/bash

CLUSTER_NAME="text-audio-ecs-cluster"

# 1. Check ECS Cluster Instances
INSTANCES_COUNT=$(aws ecs list-container-instances --cluster $CLUSTER_NAME --query 'containerInstanceArns' --output text | wc -w)
if [ "$INSTANCES_COUNT" -eq "0" ]; then
    echo "No instances found in your cluster."
else
    echo "$INSTANCES_COUNT instance(s) found in your cluster."
fi

# 2. Check ECS Instance Type and Resources
echo "Listing instance types and available resources:"
aws ecs describe-container-instances --cluster $CLUSTER_NAME --container-instances $(aws ecs list-container-instances --cluster $CLUSTER_NAME --query 'containerInstanceArns' --output text) --query 'containerInstances[*].{ID:containerInstanceArn,Type:ec2InstanceId,RemainingCPU:remainingResources[?name==`CPU`].integerValue | [0],RemainingMemory:remainingResources[?name==`MEMORY`].integerValue | [0]}' --output table

# 3. Check ECS Agent status
echo "Listing ECS agent status:"
aws ecs describe-container-instances --cluster $CLUSTER_NAME --container-instances $(aws ecs list-container-instances --cluster $CLUSTER_NAME --query 'containerInstanceArns' --output text) --query 'containerInstances[*].{ID:containerInstanceArn,AgentConnected:agentConnected,Status:status}' --output table

# 4. Check active tasks in the cluster to see if the port 5000 is already in use
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --query 'taskArns[0]' --output text)
if [ "$TASK_ARN" != "None" ]; then
    BIND_PORTS=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --query 'tasks[0].containers[0].networkBindings[].hostPort' --output text)
    if echo $BIND_PORTS | grep -q "5000"; then
        echo "Port 5000 is already in use by another task."
    else
        echo "Port 5000 is not in use."
    fi
else
    echo "No active tasks found in the cluster."
fi

# Add more checks as needed

# Note: This script assumes you have AWS CLI installed and properly configured with the necessary permissions.
