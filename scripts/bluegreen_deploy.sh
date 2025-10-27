#!/bin/bash
# Blue/Green Deployment Script
# Enables zero-downtime deployments with instant rollback

set -e

NAMESPACE="verolux"
SERVICE="verolux-backend"

echo "============================================"
echo "Verolux Blue/Green Deployment"
echo "============================================"

# Get current active deployment
CURRENT_ACTIVE=$(kubectl get svc $SERVICE -n $NAMESPACE -o jsonpath='{.spec.selector.version}')

if [ "$CURRENT_ACTIVE" == "blue" ]; then
    INACTIVE="green"
elif [ "$CURRENT_ACTIVE" == "green" ]; then
    INACTIVE="blue"
else
    echo "No active deployment found, defaulting to blue→green"
    CURRENT_ACTIVE="blue"
    INACTIVE="green"
fi

echo "Current active: $CURRENT_ACTIVE"
echo "Deploying to: $INACTIVE"
echo ""

# Step 1: Deploy new version to inactive color
echo "Step 1: Deploying new version to $INACTIVE..."
kubectl set image deployment/$SERVICE-$INACTIVE \
    backend=gcr.io/PROJECT_ID/verolux-backend:$NEW_TAG \
    -n $NAMESPACE

# Step 2: Scale up inactive deployment
echo "Step 2: Scaling up $INACTIVE deployment..."
kubectl scale deployment/$SERVICE-$INACTIVE --replicas=3 -n $NAMESPACE

# Step 3: Wait for rollout to complete
echo "Step 3: Waiting for $INACTIVE deployment to be ready..."
kubectl rollout status deployment/$SERVICE-$INACTIVE -n $NAMESPACE

# Step 4: Run smoke tests
echo "Step 4: Running smoke tests on $INACTIVE..."
INACTIVE_POD=$(kubectl get pod -n $NAMESPACE -l version=$INACTIVE -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n $NAMESPACE $INACTIVE_POD -- curl -f http://localhost:8000/health

if [ $? -ne 0 ]; then
    echo "❌ Smoke tests failed! Aborting deployment."
    kubectl scale deployment/$SERVICE-$INACTIVE --replicas=0 -n $NAMESPACE
    exit 1
fi

echo "✅ Smoke tests passed"

# Step 5: Switch traffic to new deployment
echo "Step 5: Switching traffic to $INACTIVE..."
kubectl patch svc $SERVICE -n $NAMESPACE -p '{"spec":{"selector":{"version":"'$INACTIVE'"}}}'

# Step 6: Monitor for 2 minutes
echo "Step 6: Monitoring new deployment for 2 minutes..."
sleep 120

# Check error rate
ERROR_RATE=$(kubectl logs -n $NAMESPACE -l version=$INACTIVE --tail=100 | grep ERROR | wc -l)

if [ $ERROR_RATE -gt 10 ]; then
    echo "⚠️  High error rate detected ($ERROR_RATE errors)"
    echo "Rolling back..."
    kubectl patch svc $SERVICE -n $NAMESPACE -p '{"spec":{"selector":{"version":"'$CURRENT_ACTIVE'"}}}'
    echo "❌ Deployment rolled back due to errors"
    exit 1
fi

# Step 7: Scale down old deployment
echo "Step 7: Scaling down $CURRENT_ACTIVE deployment..."
kubectl scale deployment/$SERVICE-$CURRENT_ACTIVE --replicas=0 -n $NAMESPACE

echo ""
echo "============================================"
echo "✅ Blue/Green Deployment Complete!"
echo "============================================"
echo "Active deployment: $INACTIVE"
echo "Previous deployment: $CURRENT_ACTIVE (scaled to 0)"
echo ""
echo "To rollback:"
echo "  ./bluegreen_rollback.sh"













