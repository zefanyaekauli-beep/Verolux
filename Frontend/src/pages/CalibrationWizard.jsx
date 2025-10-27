import React, { useState, useRef, useEffect } from 'react';
import { Stage, Layer, Image as KonvaImage, Circle, Line } from 'react-konva';

/**
 * Camera Calibration Wizard
 * Guided homography calibration with visual interface
 */
export default function CalibrationWizard({ cameraId, videoUrl, onComplete }) {
  const [step, setStep] = useState(1); // 1: intro, 2: place points, 3: measurements, 4: confirm
  const [videoImage, setVideoImage] = useState(null);
  const [imagePoints, setImagePoints] = useState([]);
  const [worldPoints, setWorldPoints] = useState([]);
  const [currentMeasurement, setCurrentMeasurement] = useState({ x: 0, y: 0 });
  
  const canvasRef = useRef(null);
  const videoRef = useRef(null);

  // Required calibration points
  const requiredPoints = 4;
  const pointLabels = ["Top-Left Gate Post", "Top-Right Gate Post", "Bottom-Right Marker", "Bottom-Left Marker"];

  useEffect(() => {
    // Load video frame for calibration
    const video = document.createElement('video');
    video.src = videoUrl;
    video.crossOrigin = "anonymous";
    
    video.onloadeddata = () => {
      video.currentTime = 0;
    };
    
    video.onseeked = () => {
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      const img = new window.Image();
      img.src = canvas.toDataURL();
      img.onload = () => {
        setVideoImage(img);
      };
    };
    
    videoRef.current = video;
  }, [videoUrl]);

  const handleStageClick = (e) => {
    if (step !== 2) return;
    if (imagePoints.length >= requiredPoints) return;
    
    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();
    
    setImagePoints([...imagePoints, { x: pos.x, y: pos.y }]);
  };

  const handleWorldMeasurementChange = (index, axis, value) => {
    const newPoints = [...worldPoints];
    newPoints[index] = newPoints[index] || { x: 0, y: 0 };
    newPoints[index][axis] = parseFloat(value) || 0;
    setWorldPoints(newPoints);
  };

  const submitCalibration = async () => {
    const calibrationData = {
      camera_id: cameraId,
      image_points: imagePoints.map(p => [p.x, p.y]),
      world_points: worldPoints.map(p => [p.x, p.y])
    };

    try {
      const response = await fetch(`http://127.0.0.1:8002/calibration/${cameraId}/set`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(calibrationData)
      });

      if (response.ok) {
        alert('✅ Calibration successful!');
        if (onComplete) onComplete(calibrationData);
      } else {
        alert('❌ Calibration failed');
      }
    } catch (error) {
      console.error('Calibration error:', error);
      alert('❌ Calibration error');
    }
  };

  return (
    <div className="calibration-wizard">
      <h2>🎯 Camera Calibration Wizard</h2>
      <p className="camera-id">Camera: {cameraId}</p>

      {/* Progress */}
      <div className="progress-bar">
        <div className={`step ${step >= 1 ? 'active' : ''}`}>1. Introduction</div>
        <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Place Points</div>
        <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Measurements</div>
        <div className={`step ${step >= 4 ? 'active' : ''}`}>4. Confirm</div>
      </div>

      {/* Step 1: Introduction */}
      {step === 1 && (
        <div className="wizard-step">
          <h3>📖 Calibration Guide</h3>
          <p>This wizard will help you calibrate the camera for accurate zone detection.</p>
          
          <div className="instructions">
            <h4>What you'll need:</h4>
            <ul>
              <li>✅ A clear view of the gate area</li>
              <li>✅ Known measurements (in meters)</li>
              <li>✅ 4 reference points visible in the frame</li>
            </ul>
            
            <h4>Steps:</h4>
            <ol>
              <li>Click 4 points on the video frame (corners of gate area)</li>
              <li>Enter real-world measurements for each point</li>
              <li>Review and confirm calibration</li>
            </ol>
          </div>

          <button onClick={() => setStep(2)} className="btn-primary">
            Start Calibration →
          </button>
        </div>
      )}

      {/* Step 2: Place Points */}
      {step === 2 && (
        <div className="wizard-step">
          <h3>📍 Place Calibration Points</h3>
          <p>Click {requiredPoints} points on the image. Current: {imagePoints.length}/{requiredPoints}</p>

          {imagePoints.length < requiredPoints && (
            <div className="point-instruction">
              <strong>Next point:</strong> {pointLabels[imagePoints.length]}
            </div>
          )}

          <div className="canvas-container">
            <Stage
              width={800}
              height={600}
              onClick={handleStageClick}
              ref={canvasRef}
            >
              <Layer>
                {videoImage && <KonvaImage image={videoImage} />}
                
                {/* Draw points */}
                {imagePoints.map((point, i) => (
                  <Circle
                    key={i}
                    x={point.x}
                    y={point.y}
                    radius={10}
                    fill="red"
                    stroke="white"
                    strokeWidth={2}
                  />
                ))}
                
                {/* Draw lines between points */}
                {imagePoints.length > 1 && (
                  <Line
                    points={imagePoints.flatMap(p => [p.x, p.y])}
                    stroke="yellow"
                    strokeWidth={2}
                    closed={imagePoints.length === requiredPoints}
                  />
                )}
              </Layer>
            </Stage>
          </div>

          <div className="wizard-actions">
            <button onClick={() => setImagePoints(imagePoints.slice(0, -1))} 
                    disabled={imagePoints.length === 0}>
              ← Undo Last Point
            </button>
            
            <button onClick={() => setImagePoints([])} 
                    disabled={imagePoints.length === 0}>
              🔄 Reset Points
            </button>
            
            <button onClick={() => setStep(3)}
                    disabled={imagePoints.length !== requiredPoints}
                    className="btn-primary">
              Next: Enter Measurements →
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Measurements */}
      {step === 3 && (
        <div className="wizard-step">
          <h3>📏 Enter Real-World Measurements</h3>
          <p>Enter the actual measurements (in meters) for each calibration point</p>

          <div className="measurements-grid">
            {imagePoints.map((point, i) => (
              <div key={i} className="measurement-input">
                <h4>{pointLabels[i]}</h4>
                <p className="pixel-coords">Pixel: ({point.x.toFixed(0)}, {point.y.toFixed(0)})</p>
                
                <div className="input-group">
                  <label>
                    X (meters):
                    <input
                      type="number"
                      step="0.1"
                      value={worldPoints[i]?.x || 0}
                      onChange={(e) => handleWorldMeasurementChange(i, 'x', e.target.value)}
                      placeholder="0.0"
                    />
                  </label>
                  
                  <label>
                    Y (meters):
                    <input
                      type="number"
                      step="0.1"
                      value={worldPoints[i]?.y || 0}
                      onChange={(e) => handleWorldMeasurementChange(i, 'y', e.target.value)}
                      placeholder="0.0"
                    />
                  </label>
                </div>
              </div>
            ))}
          </div>

          <div className="wizard-actions">
            <button onClick={() => setStep(2)}>
              ← Back to Points
            </button>
            
            <button onClick={() => setStep(4)}
                    disabled={worldPoints.length !== requiredPoints}
                    className="btn-primary">
              Next: Review →
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Confirm */}
      {step === 4 && (
        <div className="wizard-step">
          <h3>✅ Review Calibration</h3>
          
          <div className="calibration-summary">
            <h4>Calibration Points:</h4>
            <table>
              <thead>
                <tr>
                  <th>Point</th>
                  <th>Image (pixels)</th>
                  <th>World (meters)</th>
                </tr>
              </thead>
              <tbody>
                {imagePoints.map((imgPt, i) => (
                  <tr key={i}>
                    <td>{pointLabels[i]}</td>
                    <td>({imgPt.x.toFixed(0)}, {imgPt.y.toFixed(0)})</td>
                    <td>({worldPoints[i]?.x.toFixed(2) || 0}, {worldPoints[i]?.y.toFixed(2) || 0})</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="wizard-actions">
            <button onClick={() => setStep(3)}>
              ← Back to Measurements
            </button>
            
            <button onClick={submitCalibration} className="btn-success">
              ✅ Apply Calibration
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        .calibration-wizard {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .camera-id {
          color: #666;
          margin-bottom: 20px;
        }

        .progress-bar {
          display: flex;
          gap: 10px;
          margin-bottom: 30px;
        }

        .step {
          flex: 1;
          padding: 10px;
          background: #f0f0f0;
          border-radius: 5px;
          text-align: center;
        }

        .step.active {
          background: #4CAF50;
          color: white;
        }

        .wizard-step {
          background: white;
          padding: 30px;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .canvas-container {
          border: 2px solid #ddd;
          border-radius: 5px;
          overflow: hidden;
          margin: 20px 0;
        }

        .point-instruction {
          background: #fff3cd;
          padding: 15px;
          border-radius: 5px;
          margin: 15px 0;
          font-size: 16px;
        }

        .measurements-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;
          margin: 20px 0;
        }

        .measurement-input {
          border: 1px solid #ddd;
          padding: 15px;
          border-radius: 5px;
        }

        .pixel-coords {
          color: #666;
          font-size: 14px;
        }

        .input-group {
          display: flex;
          gap: 10px;
          margin-top: 10px;
        }

        .input-group label {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .input-group input {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .wizard-actions {
          display: flex;
          justify-content: space-between;
          margin-top: 30px;
          gap: 10px;
        }

        button {
          padding: 12px 24px;
          border: none;
          border-radius: 5px;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.2s;
        }

        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-primary {
          background: #2196F3;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #1976D2;
        }

        .btn-success {
          background: #4CAF50;
          color: white;
        }

        .btn-success:hover {
          background: #45a049;
        }

        .calibration-summary table {
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
        }

        .calibration-summary th,
        .calibration-summary td {
          padding: 10px;
          border: 1px solid #ddd;
          text-align: left;
        }

        .calibration-summary th {
          background: #f5f5f5;
          font-weight: bold;
        }

        .instructions {
          background: #f9f9f9;
          padding: 20px;
          border-radius: 5px;
          margin: 20px 0;
        }

        .instructions h4 {
          margin-top: 0;
        }

        .instructions ul, .instructions ol {
          margin: 10px 0;
        }

        .instructions li {
          margin: 5px 0;
        }
      `}</style>
    </div>
  );
}












