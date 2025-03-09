from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import certifi
import logging
from logging_config import configure_logging
from pydantic import BaseModel, Field
from typing import List, Optional
import model_config

# Configure logging based on environment
environment = os.getenv('ENVIRONMENT', 'production')
configure_logging(environment)
logger = logging.getLogger(__name__)

# Set SSL certificate path
os.environ['SSL_CERT_FILE'] = certifi.where()

# Define the request model
class LogAnalysisRequest(BaseModel):
    log_data: str = Field(..., description="The log data to analyze")
    model_id: Optional[str] = Field(None, description="The specific model ID to use")

# Create FastAPI app
app = FastAPI(
    title="Network Log Analyzer API",
    description="API for analyzing network security logs using AI",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Clean HTML tags from log data
def clean_log_data(log_data):
    """Remove HTML tags from log data"""
    if log_data:
        return re.sub(r'<[^>]+>', '', log_data)
    return log_data

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("log_analyzer.html", {"request": request})

@app.post("/analyze")
async def analyze_log(log_data: str = Form(...), model_id: Optional[str] = Form(None)):
    """Analyze log data using the specified model"""
    try:
        if not log_data or len(log_data) < 10:
            raise HTTPException(status_code=400, detail="Log data is too short or empty")
            
        # Log the request for debugging
        logger.info(f"Analyzing log with model: {model_id or 'default'}")
        
        # Analyze with Gemini
        result = model_config.analyze_with_gemini(log_data, model_id)
            
        return result
    except Exception as e:
        logger.error(f"Error analyzing log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing log: {str(e)}")

@app.get("/models", summary="Get available models")
async def get_models():
    """Get the list of available models."""
    return model_config.GEMINI_MODELS

@app.get("/health", summary="Health check endpoint")
async def health_check():
    """Check if the API is healthy"""
    return {"status": "ok", "version": "1.0.0"}

# Create HTML template file
def create_template_file():
    """Create the HTML template file if it doesn't exist"""
    os.makedirs("templates", exist_ok=True)
    template_path = os.path.join("templates", "log_analyzer.html")
    
    if not os.path.exists(template_path):
        with open(template_path, "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Log Analyzer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        }
        .header {
            margin-bottom: 30px;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 20px;
        }
        .log-textarea {
            min-height: 200px;
            font-family: monospace;
            margin-bottom: 20px;
        }
        .analysis-result {
            margin-top: 30px;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            background-color: #f8f9fa;
            min-height: 200px;
            white-space: pre-wrap;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .model-info {
            margin-top: 10px;
            font-size: 0.8rem;
            color: #6c757d;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Network Log Analyzer</h1>
            <p class="lead">Analyze network logs using AI to identify security threats and anomalies</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="modelSelect" class="form-label">Model</label>
                    <select class="form-select" id="modelSelect">
                        <!-- Models will be populated by JavaScript -->
                    </select>
                </div>
            </div>
        </div>
        
        <div class="mb-3">
            <label for="logData" class="form-label">Network Log Data</label>
            <textarea class="form-control log-textarea" id="logData" rows="8" placeholder="Paste your network log data here..."></textarea>
        </div>
        
        <div class="mb-3">
            <button class="btn btn-primary" id="analyzeButton">Analyze Log Data</button>
            <button class="btn btn-secondary" id="exampleButton">Load Example</button>
            <button class="btn btn-outline-danger" id="clearButton">Clear</button>
        </div>
        
        <div class="loading" id="loadingIndicator">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Analyzing log data, please wait...</p>
        </div>
        
        <div id="resultSection" style="display: none;">
            <h3>Analysis Result</h3>
            <div class="analysis-result" id="analysisResult"></div>
            <div class="model-info" id="modelInfo"></div>
        </div>
    </div>

    <script>
        // Example log data
        const exampleLogData = `Mar 15 06:42:12 server sshd[5774]: Failed password for invalid user admin from 192.168.1.100 port 43250 ssh2
Mar 15 06:42:14 server sshd[5774]: Failed password for invalid user admin from 192.168.1.100 port 43250 ssh2
Mar 15 06:42:17 server sshd[5774]: Failed password for invalid user admin from 192.168.1.100 port 43250 ssh2
Mar 15 06:42:19 server sshd[5774]: Failed password for invalid user root from 192.168.1.100 port 43250 ssh2
Mar 15 06:42:21 server sshd[5774]: Failed password for invalid user root from 192.168.1.100 port 43250 ssh2
Mar 15 06:42:24 server sshd[5774]: Failed password for invalid user root from 192.168.1.100 port 43250 ssh2
Mar 15 06:42:26 server sshd[5774]: Failed password for invalid user admin from 192.168.1.100 port 43250 ssh2`;

        // DOM elements
        const modelSelect = document.getElementById('modelSelect');
        const logDataTextarea = document.getElementById('logData');
        const analyzeButton = document.getElementById('analyzeButton');
        const exampleButton = document.getElementById('exampleButton');
        const clearButton = document.getElementById('clearButton');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const resultSection = document.getElementById('resultSection');
        const analysisResult = document.getElementById('analysisResult');
        const modelInfo = document.getElementById('modelInfo');

        // Available models
        let availableModels = [];

        // Fetch available models on page load
        async function fetchModels() {
            try {
                const response = await fetch('/models');
                const data = await response.json();
                
                availableModels = data;
                
                // Populate model select
                populateModelSelect();
            } catch (error) {
                console.error('Error fetching models:', error);
            }
        }

        // Populate model select dropdown
        function populateModelSelect() {
            modelSelect.innerHTML = '';
            
            availableModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.text = `${model.name} - ${model.description}`;
                modelSelect.appendChild(option);
            });
        }

        // Handle analyze button click
        analyzeButton.addEventListener('click', async () => {
            const logData = logDataTextarea.value.trim();
            
            if (!logData) {
                alert('Please enter log data to analyze');
                return;
            }
            
            // Show loading indicator
            loadingIndicator.style.display = 'block';
            resultSection.style.display = 'none';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `log_data=${encodeURIComponent(logData)}&model_id=${modelSelect.value}`
                });
                
                const result = await response.json();
                
                // Display result
                analysisResult.textContent = result.analysis;
                modelInfo.textContent = `Analyzed with: ${result.model_used} (Gemini)`;
                
                // Show result section
                resultSection.style.display = 'block';
            } catch (error) {
                console.error('Error analyzing log:', error);
                analysisResult.textContent = `Error: ${error.message || 'Failed to analyze log data'}`;
                resultSection.style.display = 'block';
            } finally {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
            }
        });

        // Handle example button click
        exampleButton.addEventListener('click', () => {
            logDataTextarea.value = exampleLogData;
        });

        // Handle clear button click
        clearButton.addEventListener('click', () => {
            logDataTextarea.value = '';
            resultSection.style.display = 'none';
        });

        // Initialize page
        fetchModels();
    </script>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
        logger.info(f"Created template file at {template_path}")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    from threading import Timer
    
    # Create template file
    create_template_file()
    
    def open_browser():
        webbrowser.open("http://localhost:8001")
    
    # Open browser after a 1.5 second delay to ensure server is running
    Timer(1.5, open_browser).start()
    
    # Configure uvicorn logging
    uvicorn_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(uvicorn_config)
    server.run()
