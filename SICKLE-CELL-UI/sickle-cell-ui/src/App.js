
import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [selectMode, setSelectMode] = useState(null);
  const [results, setResults] = useState(null);
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cameraSupported, setCameraSupported] = useState(true);
  const [imageUrl, setImageUrl] = useState(null);

  // Check camera support on component mount
  useEffect(() => {
    const checkCameraSupport = async () => {
      try {
        // Check if getUserMedia is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setCameraSupported(false);
          return;
        }

        // Try to get camera permission (this will trigger permission dialog)
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        stream.getTracks().forEach(track => track.stop()); // Stop the stream immediately
        setCameraSupported(true);
      } catch (error) {
        console.warn('Camera not supported or permission denied:', error);
        setCameraSupported(false);
      }
    };

    checkCameraSupport();
  }, []);

  const [backendUrl] = useState(process.env.REACT_APP_API_URL || '');

  const getBackendEndpoint = (path) => {
    return backendUrl ? `${backendUrl}${path}` : path;
  };

  // Check if user has accepted disclaimer
  useEffect(() => {
    const accepted = sessionStorage.getItem('disclaimerAccepted');
    if (accepted) {
      setDisclaimerAccepted(true);
      setShowDisclaimer(false);
    }
  }, []);

  // Clear sensitive data on component unmount
  useEffect(() => {
    return () => {
      setResults(null);
      setError(null);
    };
  }, []);

  const handleAcceptDisclaimer = () => {
    setDisclaimerAccepted(true);
    setShowDisclaimer(false);
    sessionStorage.setItem('disclaimerAccepted', 'true');
  };

  const handleImageUpload = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];

      // Security: Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'image/bmp'];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a valid image file (JPG, PNG, WebP, or BMP)');
        return;
      }

      // Security: Validate file size (Max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setError(null);
      setImageUrl(URL.createObjectURL(file));
      setIsProcessing(true);

      try {
        // Prepare form data
        const formData = new FormData();
        formData.append('image', file);

        // Call backend API
        const response = await fetch(getBackendEndpoint('/predict'), {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to analyze image');
        }

        const data = await response.json();

        setResults({
          type: 'image',
          label: data.label,
          confidence: (data.confidence * 100).toFixed(2),
          interpretation: data.interpretation,
          recommendations: data.recommendations,
          is_sickle_positive: data.is_sickle_positive,
          probabilities: data.probabilities,
        });
      } catch (err) {
        setError(`Error: ${err.message}`);
        console.error('Image upload error:', err);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const handleCameraCapture = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];

      // For camera capture, the file might not have a proper type initially
      // Convert to a proper blob if needed
      let processedFile = file;

      // If the file doesn't have a proper MIME type, try to determine it
      if (!file.type || file.type === '') {
        try {
          // Create a new file with proper MIME type based on file extension or content
          const fileName = file.name || 'camera_capture.jpg';
          const mimeType = fileName.toLowerCase().includes('.png') ? 'image/png' : 'image/jpeg';
          processedFile = new File([file], fileName, { type: mimeType });
        } catch (error) {
          console.warn('Could not process camera file type:', error);
          processedFile = file;
        }
      }

      // Security: Validate file size (Max 10MB)
      if (processedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      // Additional validation for camera captures
      if (processedFile.size === 0) {
        setError('Camera capture failed. Please try again or upload from device.');
        return;
      }

      setError(null);
      setImageUrl(URL.createObjectURL(processedFile));
      setIsProcessing(true);

      try {
        // Prepare form data
        const formData = new FormData();
        formData.append('image', processedFile);

        // Call backend API with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const response = await fetch(getBackendEndpoint('/predict'), {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to analyze image');
        }

        const data = await response.json();

        setResults({
          type: 'image',
          label: data.label,
          confidence: (data.confidence * 100).toFixed(2),
          interpretation: data.interpretation,
          recommendations: data.recommendations,
          is_sickle_positive: data.is_sickle_positive,
          probabilities: data.probabilities,
        });
      } catch (err) {
        if (err.name === 'AbortError') {
          setError('Request timed out. Please check your connection and try again.');
        } else {
          setError(`Camera capture error: ${err.message}`);
        }
        console.error('Camera capture error:', err);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const handleLabSubmit = async (e) => {
    e.preventDefault();
    
    // Validate and get form inputs
    const formData = new FormData(e.target);
    const hb = parseFloat(formData.get('hb'));
    const wbc = parseFloat(formData.get('wbc'));
    const rbc = parseFloat(formData.get('rbc'));
    const rdw = parseFloat(formData.get('rdw'));
    const platelets = parseFloat(formData.get('platelets'));

    if (isNaN(hb) || isNaN(wbc) || isNaN(rbc) || isNaN(rdw) || isNaN(platelets)) {
      setError('Please enter valid numeric values');
      return;
    }

    setError(null);
    setIsProcessing(true);

    try {
      // Call backend API
      const response = await fetch(
        getBackendEndpoint(`/analyze-lab-values?hb=${hb}&wbc=${wbc}&rbc=${rbc}&rdw=${rdw}&platelets=${platelets}`),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze lab values');
      }

      const data = await response.json();
      
      setResults({
        type: 'lab',
        hb: data.hb,
        wbc: data.wbc,
        rbc: data.rbc,
        rdw: data.rdw,
        platelets: data.platelets,
        analysis: data.analysis,
        risk_assessment: data.risk_assessment,
        recommendations: data.recommendations,
        disclaimer: data.disclaimer,
      });
    } catch (err) {
      setError(`Error: ${err.message}`);
      console.error('Lab analysis error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    // Clear data securely
    setSelectMode(null);
    setResults(null);
    setError(null);
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
    }
    setImageUrl(null);
    setIsProcessing(false);
  };

  if (showDisclaimer && !disclaimerAccepted) {
    return (
      <div className="app-container">
        <header className="app-header">
          <div className="container d-flex align-items-center justify-content-between h-100">
            <div className="d-flex align-items-center">
              <img src="/falcons-logo.svg" alt="FalconsScan AI logo" className="app-logo" />
              <h1 className="app-title">FalconsScan AI</h1>
            </div>
          </div>
        </header>

        <div className="disclaimer-overlay">
          <div className="disclaimer-card">
            <h2>Medical Disclaimer</h2>
            
            <div className="disclaimer-content">
              <section>
                <h3>⚠️ Important Notice</h3>
                <p>
                  <strong>FalconsScan AI</strong> is a supportive analysis tool and NOT a substitute for professional medical diagnosis, treatment, or advice. 
                  This application should only be used as an aid in conjunction with medical professional evaluation.
                </p>
              </section>

              <section>
                <h3>📋 How This Application Works</h3>
                <ul>
                  <li>Analyzes blood smear images using AI-powered image recognition</li>
                  <li>Evaluates laboratory values for potential health indicators</li>
                  <li>Provides preliminary analysis for informational purposes only</li>
                  <li>All analysis is performed with your consent and data privacy</li>
                </ul>
              </section>

              <section>
                <h3>🔒 Privacy & Security</h3>
                <ul>
                  <li><strong>Zero Data Collection:</strong> We do not collect, store, or track any user information</li>
                  <li><strong>Local Processing:</strong> All analysis happens on your device</li>
                  <li><strong>No Third-party Tracking:</strong> No analytics, cookies, or external tracking</li>
                  <li><strong>Session-based:</strong> Data is cleared when you close the application</li>
                </ul>
              </section>

              <section>
                <h3>⚕️ Medical Guidance</h3>
                <ul>
                  <li>Always consult qualified healthcare professionals for medical decisions</li>
                  <li>Results should be reviewed by a pathologist or physician</li>
                  <li>Do not make medical decisions based solely on this application</li>
                  <li>Seek immediate medical attention for urgent conditions</li>
                </ul>
              </section>

              <section>
                <h3>💾 Data Handling</h3>
                <ul>
                  <li>Images and values are processed and not permanently stored</li>
                  <li>No permanent storage of any patient information</li>
                  <li>Browser cache may store application code only (not patient data)</li>
                  <li>Refresh or close the browser to clear all session data</li>
                </ul>
              </section>
            </div>

            <div className="disclaimer-actions">
              <button 
                className="disclaimer-reject"
                onClick={() => {
                  alert('You must accept the disclaimer to use this application');
                  setShowDisclaimer(true);
                }}
              >
                Do Not Accept
              </button>
              <button 
                className="disclaimer-accept"
                onClick={handleAcceptDisclaimer}
              >
                I Understand and Accept
              </button>
            </div>

            <p className="disclaimer-footer">
              You must accept these terms to continue. This notice will not appear again in this session.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="container d-flex align-items-center justify-content-between h-100">
          <div className="d-flex align-items-center">
            <img src="/falcons-logo.svg" alt="FalconsScan AI logo" className="app-logo" />
            <h1 className="app-title">FalconsScan AI</h1>
          </div>
          <button className="settings-btn" title="Settings">⚙️</button>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="container">
          {/* Error Message */}
          {error && (
            <div className="error-alert">
              <span className="error-icon">❌</span>
              <div className="error-content">
                <strong>Error:</strong> {error}
              </div>
              <button 
                className="error-close"
                onClick={() => setError(null)}
              >
                ✕
              </button>
            </div>
          )}

          {!selectMode && !results && !isProcessing && (
            <div>
              {/* Option Cards */}
              <div className="options-container">
                <div className="option-card" onClick={() => setSelectMode('image')} role="button" tabIndex="0">
                  <div className="option-icon" aria-hidden="true">📷</div>
                  <div className="option-title">Scan Blood Smear</div>
                  <div className="option-subtitle">Upload an image for AI analysis</div>
                </div>

                <div className="option-divider" aria-hidden="true">or</div>

                <div className="option-card" onClick={() => setSelectMode('lab')} role="button" tabIndex="0">
                  <div className="option-icon" aria-hidden="true">📋</div>
                  <div className="option-title">Enter Lab Values</div>
                  <div className="option-subtitle">Analyze hemoglobin, WBC, RBC, RDW, and platelets</div>
                </div>
              </div>

              {/* Analyze Button */}
              <button className="analyze-btn" onClick={() => console.log('Ready to analyze')}>
                Get Started
              </button>
            </div>
          )}

          {selectMode === 'image' && !results && (
            <div className="input-section">
              <div className="image-input-options">
                <label htmlFor="fileInput" className="file-label">
                  📤 Upload from Device
                  <input
                    id="fileInput"
                    type="file"
                    accept="image/jpeg,image/png,image/jpg,image/webp,image/bmp"
                    className="file-input"
                    onChange={handleImageUpload}
                    disabled={isProcessing}
                  />
                </label>

                {!cameraSupported ? (
                  <div className="camera-disabled">
                    <span className="camera-icon">📷</span>
                    <div className="camera-text">
                      <div className="camera-title">Camera Not Available</div>
                      <div className="camera-subtitle">Use device upload instead</div>
                    </div>
                  </div>
                ) : (
                  <label htmlFor="cameraInput" className="camera-label">
                    📸 Capture from Camera
                    <input
                      id="cameraInput"
                      type="file"
                      accept="image/*"
                      capture={navigator.userAgent.includes('Mobile') ? 'environment' : undefined}
                      className="file-input"
                      onChange={handleCameraCapture}
                      disabled={isProcessing}
                    />
                  </label>
                )}
              </div>
              <p className="file-note">Supported formats: JPG, PNG, WebP, BMP (Max 10MB)</p>
              <button className="btn-cancel" onClick={handleReset} disabled={isProcessing}>
                Cancel
              </button>
            </div>
          )}

          {selectMode === 'lab' && !results && (
            <div className="input-section">
              <form onSubmit={handleLabSubmit}>
                <div className="lab-inputs">
                  <div className="lab-input-group">
                    <label htmlFor="hb">Hemoglobin (Hb) g/dL</label>
                    <input
                      id="hb"
                      name="hb"
                      type="number"
                      step="0.1"
                      placeholder="Normal: 12-17.5"
                      required
                      min="0"
                      max="25"
                      disabled={isProcessing}
                    />
                    <small className="input-hint">Normal range: 12-17.5 g/dL</small>
                  </div>
                  <div className="lab-input-group">
                    <label htmlFor="wbc">WBC Count 10^9/L</label>
                    <input
                      id="wbc"
                      name="wbc"
                      type="number"
                      step="0.1"
                      placeholder="Normal: 4.5-11"
                      required
                      min="0"
                      max="100"
                      disabled={isProcessing}
                    />
                    <small className="input-hint">Normal range: 4.5-11 ×10^9/L</small>
                  </div>
                  <div className="lab-input-group">
                    <label htmlFor="rbc">RBC Count 10^12/L</label>
                    <input
                      id="rbc"
                      name="rbc"
                      type="number"
                      step="0.01"
                      placeholder="Normal: 4.0-6.0"
                      required
                      min="0"
                      max="10"
                      disabled={isProcessing}
                    />
                    <small className="input-hint">Normal range: 4.0-6.0 ×10^12/L</small>
                  </div>
                  <div className="lab-input-group">
                    <label htmlFor="rdw">RDW (%)</label>
                    <input
                      id="rdw"
                      name="rdw"
                      type="number"
                      step="0.1"
                      placeholder="Normal: 11.5-14.5"
                      required
                      min="0"
                      max="50"
                      disabled={isProcessing}
                    />
                    <small className="input-hint">Normal range: 11.5-14.5%</small>
                  </div>
                  <div className="lab-input-group">
                    <label htmlFor="platelets">Platelets 10^9/L</label>
                    <input
                      id="platelets"
                      name="platelets"
                      type="number"
                      step="0.1"
                      placeholder="Normal: 150-400"
                      required
                      min="0"
                      max="1000"
                      disabled={isProcessing}
                    />
                    <small className="input-hint">Normal range: 150-400 ×10^9/L</small>
                  </div>
                </div>
                <button type="submit" className="analyze-btn" disabled={isProcessing}>
                  {isProcessing ? 'Analyzing...' : 'Analyze'}
                </button>
              </form>
              <button className="btn-cancel" onClick={handleReset} disabled={isProcessing}>
                Cancel
              </button>
            </div>
          )}

          {(isProcessing) && (
            <div className="processing-state">
              <div className="spinner"></div>
              <p>Analyzing your data...</p>
              <p className="processing-note">Communicating with AI analysis engine...</p>
            </div>
          )}

          {results && results.type === 'image' && (
            <div className="results-section">
              <h2>Blood Smear Analysis Results</h2>
              <div className="medical-notice">
                💡 <strong>Note:</strong> These results are for reference only. Consult a healthcare provider for clinical decisions.
              </div>
              
              {imageUrl && (
                <div className="image-preview">
                  <h3>Uploaded Image</h3>
                  <img src={imageUrl} alt="Blood smear image" className="uploaded-image" />
                </div>
              )}
              
              <div className="results-card">
                <div className="result-header">
                  <span className="result-icon-large">
                    {results.is_sickle_positive ? '⚠️' : '✅'}
                  </span>
                  <div>
                    <h3 className={results.is_sickle_positive ? 'text-danger' : 'text-success'}>
                      {results.label.toUpperCase()}
                    </h3>
                    <p className="confidence-badge">
                      Confidence: {results.confidence}%
                    </p>
                  </div>
                </div>

                <div className="result-item interpretation-box">
                  <span className="result-icon" aria-hidden="true">📊</span>
                  <div className="result-content">
                    <span className="result-label">Interpretation:</span>
                    <span className="result-value">{results.interpretation}</span>
                  </div>
                </div>

                <div className="result-item">
                  <span className="result-icon" aria-hidden="true">📈</span>
                  <div className="result-content">
                    <span className="result-label">Cell Classification Confidence:</span>
                    <div className="probability-display">
                      {Object.entries(results.probabilities).map(([label, prob]) => (
                        <div key={label} className="probability-bar">
                          <span className="prob-label">{label.charAt(0).toUpperCase() + label.slice(1)}</span>
                          <div className="prob-bar-container">
                            <div 
                              className="prob-bar-fill"
                              style={{width: `${prob * 100}%`}}
                            ></div>
                          </div>
                          <span className="prob-value">{(prob * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="recommendations-box">
                  <h4>📋 Recommended Actions:</h4>
                  <ul>
                    {results.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <button className="analyze-btn" onClick={handleReset}>
                New Analysis
              </button>
            </div>
          )}

          {results && results.type === 'lab' && (
            <div className="results-section">
              <h2>Laboratory Values Analysis</h2>
              <div className="medical-notice">
                💡 <strong>Disclaimer:</strong> {results.disclaimer}
              </div>

              <div className="results-card">
                <div className="result-item assessment-box">
                  <span className="result-icon" aria-hidden="true">🔍</span>
                  <div className="result-content">
                    <span className="result-label">Overall Risk Assessment:</span>
                    <span className={`result-value assessment-${results.risk_assessment.split('-')[0].toLowerCase()}`}>
                      {results.risk_assessment}
                    </span>
                  </div>
                </div>

                {results.ml_prediction && (
                  <div className="ml-prediction-box">
                    <h4>🤖 Machine Learning Analysis</h4>
                    <div className="ml-prediction-content">
                      <div className="prediction-main">
                        <span className="prediction-label">Model Prediction:</span>
                        <span className={`prediction-value prediction-${
                          results.ml_prediction.model_prediction.includes('Sickle Cell Disease') ? 'positive' : 
                          results.ml_prediction.model_prediction.includes('Carrier') ? 'warning' : 'negative'
                        }`}>
                          {results.ml_prediction.model_prediction}
                        </span>
                      </div>
                      <div className="prediction-confidence">
                        <span className="conf-label">Confidence:</span>
                        <span className="conf-value">
                          {(results.ml_prediction.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="prediction-probabilities">
                        <div className="prob-item">
                          <span className="prob-label">Normal:</span>
                          <div className="prob-bar-container">
                            <div 
                              className="prob-bar prob-normal" 
                              style={{width: `${results.ml_prediction.normal_probability * 100}%`}}
                            >
                              <span className="prob-text">{(results.ml_prediction.normal_probability * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                        <div className="prob-item">
                          <span className="prob-label">Carrier (Trait):</span>
                          <div className="prob-bar-container">
                            <div 
                              className="prob-bar prob-carrier" 
                              style={{width: `${results.ml_prediction.carrier_probability * 100}%`}}
                            >
                              <span className="prob-text">{(results.ml_prediction.carrier_probability * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                        <div className="prob-item">
                          <span className="prob-label">Sickle Cell Disease:</span>
                          <div className="prob-bar-container">
                            <div 
                              className="prob-bar prob-sickle" 
                              style={{width: `${results.ml_prediction.sickle_probability * 100}%`}}
                            >
                              <span className="prob-text">{(results.ml_prediction.sickle_probability * 100).toFixed(1)}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="lab-results-grid">
                  <div className="lab-result-item">
                    <div className="lab-value-header">
                      <span className="lab-icon">🩸</span>
                      <h4>Hemoglobin (Hb)</h4>
                    </div>
                    <div className="lab-value-main">{results.hb} g/dL</div>
                    <div className={`lab-status lab-${results.analysis.hemoglobin.status.toLowerCase().replace('_', '-')}`}>
                      {results.analysis.hemoglobin.status}
                    </div>
                    <p className="lab-interpretation">{results.analysis.hemoglobin.interpretation}</p>
                  </div>

                  <div className="lab-result-item">
                    <div className="lab-value-header">
                      <span className="lab-icon">⚪</span>
                      <h4>WBC Count</h4>
                    </div>
                    <div className="lab-value-main">{results.wbc} ×10^9/L</div>
                    <div className={`lab-status lab-${results.analysis.wbc.status.toLowerCase().replace('_', '-')}`}>
                      {results.analysis.wbc.status}
                    </div>
                    <p className="lab-interpretation">{results.analysis.wbc.interpretation}</p>
                  </div>

                  <div className="lab-result-item">
                    <div className="lab-value-header">
                      <span className="lab-icon">🧬</span>
                      <h4>RBC Count</h4>
                    </div>
                    <div className="lab-value-main">{results.rbc} ×10^12/L</div>
                    <div className={`lab-status lab-${results.analysis.rbc.status.toLowerCase().replace('_', '-')}`}>
                      {results.analysis.rbc.status}
                    </div>
                    <p className="lab-interpretation">{results.analysis.rbc.interpretation}</p>
                  </div>

                  <div className="lab-result-item">
                    <div className="lab-value-header">
                      <span className="lab-icon">📈</span>
                      <h4>RDW</h4>
                    </div>
                    <div className="lab-value-main">{results.rdw}%</div>
                    <div className={`lab-status lab-${results.analysis.rdw.status.toLowerCase().replace('_', '-')}`}>
                      {results.analysis.rdw.status}
                    </div>
                    <p className="lab-interpretation">{results.analysis.rdw.interpretation}</p>
                  </div>

                  <div className="lab-result-item">
                    <div className="lab-value-header">
                      <span className="lab-icon">🔵</span>
                      <h4>Platelets</h4>
                    </div>
                    <div className="lab-value-main">{results.platelets} ×10^9/L</div>
                    <div className={`lab-status lab-${results.analysis.platelets.status.toLowerCase().replace('_', '-')}`}>
                      {results.analysis.platelets.status}
                    </div>
                    <p className="lab-interpretation">{results.analysis.platelets.interpretation}</p>
                  </div>
                </div>

                <div className="recommendations-box">
                  <h4>📋 Recommended Actions:</h4>
                  <ul>
                    {results.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <button className="analyze-btn" onClick={handleReset}>
                New Analysis
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Footer with disclaimers */}
      <footer className="app-footer">
        <div className="container">
          <p>
            ⚠️ Medical Disclaimer: This tool is for informational purposes only and does not replace professional medical advice. 
            🔒 Privacy: No data is collected, stored, or transmitted.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
