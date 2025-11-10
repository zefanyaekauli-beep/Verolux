#!/bin/bash
# Setup DVC (Data Version Control) for ML data versioning

echo "Setting up DVC for Verolux..."

# Install DVC
pip install dvc dvc-s3 dvc-gs

# Initialize DVC (if not already)
if [ ! -d ".dvc" ]; then
    dvc init
    echo "✅ DVC initialized"
fi

# Add remote storage
dvc remote add -d storage s3://verolux-ml-data/dvc-storage

# Track training data
dvc add Backend/training_data
dvc add Backend/validation_data
dvc add Backend/test_data

# Track models
dvc add Backend/models/*.pt
dvc add Backend/models/*.onnx

# Create DVC pipeline
cat > dvc.yaml << 'EOF'
stages:
  prepare_data:
    cmd: python scripts/prepare_training_data.py
    deps:
      - scripts/prepare_training_data.py
      - Backend/raw_data
    outs:
      - Backend/training_data
      - Backend/validation_data
  
  train_model:
    cmd: python scripts/train_model.py
    deps:
      - Backend/training_data
      - Backend/validation_data
    params:
      - train.epochs
      - train.batch_size
    outs:
      - Backend/models/weight.pt
    metrics:
      - Backend/metrics/train_metrics.json

  validate_model:
    cmd: python Backend/model_validation.py
    deps:
      - Backend/models/weight.pt
      - Backend/test_data
    metrics:
      - Backend/metrics/validation_metrics.json
EOF

# Commit DVC files to git
git add .dvc/config dvc.yaml Backend/*.dvc

echo "✅ DVC setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure cloud storage: dvc remote modify storage url s3://your-bucket"
echo "2. Push data: dvc push"
echo "3. Run pipeline: dvc repro"



















