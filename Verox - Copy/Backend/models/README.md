# Custom Model Directory

## Using Your Custom weight.pt Model

1. **Place your custom `weight.pt` file in this directory**
2. **The system will automatically detect and load it**
3. **Model should be compatible with Ultralytics YOLO format**

## Model Requirements

- **Format**: PyTorch (.pt) file
- **Architecture**: YOLOv8/YOLOv5 compatible
- **Classes**: Should include "person" class
- **Input Size**: 640x640 (recommended)

## Supported Model Types

- ✅ Custom trained YOLOv8 models
- ✅ Custom trained YOLOv5 models  
- ✅ Fine-tuned models for person detection
- ✅ Pre-trained models with person class

## Fallback Behavior

If `weight.pt` is not found, the system will:
1. Try to download YOLOv8n.pt automatically
2. Use fallback detection if download fails
3. Show appropriate error messages

## Performance Optimization

The system is optimized for:
- **Real-time inference** (30+ FPS)
- **Person detection** focus
- **GPU acceleration** (CUDA)
- **Half-precision** inference for speed

## Troubleshooting

- **Model not loading**: Check file path and format
- **Low performance**: Ensure GPU is available
- **No detections**: Verify model includes person class
- **Memory issues**: Try CPU mode or smaller model

