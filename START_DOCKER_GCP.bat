@echo off
REM Verolux Enterprise - GCP Docker Deployment Script
REM Deploys to Google Cloud Platform using Docker

echo ╔════════════════════════════════════════════╗
echo ║  🚀 Verolux Enterprise - GCP Deployment   ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check prerequisites
echo [*] Checking prerequisites...
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found!
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)
echo [OK] Docker found

gcloud --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Google Cloud SDK not found!
    echo.
    echo Please install from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo [OK] Google Cloud SDK found

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose not found!
    pause
    exit /b 1
)
echo [OK] Docker Compose found

echo.
echo ════════════════════════════════════════════
echo GCP Configuration
echo ════════════════════════════════════════════
echo.

REM Get GCP Project ID
set /p GCP_PROJECT_ID="Enter your GCP Project ID: "

if "%GCP_PROJECT_ID%"=="" (
    echo [ERROR] Project ID cannot be empty!
    pause
    exit /b 1
)

REM Set default region and zone
set GCP_REGION=asia-southeast2
set GCP_ZONE=asia-southeast2-a

echo.
echo Configuration Summary:
echo   Project ID: %GCP_PROJECT_ID%
echo   Region:     %GCP_REGION%
echo   Zone:       %GCP_ZONE%
echo.

set /p CONFIRM="Continue with deployment? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo ════════════════════════════════════════════
echo Starting Deployment Process
echo ════════════════════════════════════════════
echo.

REM Step 1: Configure GCP
echo [1/7] Configuring GCP project...
gcloud config set project %GCP_PROJECT_ID%
gcloud config set compute/region %GCP_REGION%
gcloud config set compute/zone %GCP_ZONE%
echo [OK] GCP configured
echo.

REM Step 2: Enable APIs
echo [2/7] Enabling required GCP APIs...
echo [INFO] This may take 1-2 minutes...
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
echo [OK] APIs enabled
echo.

REM Step 3: Create environment file
echo [3/7] Setting up environment configuration...
if not exist ".env.gcp" (
    if exist "env.gcp.template" (
        copy env.gcp.template .env.gcp
        echo [INFO] Created .env.gcp from template
        echo [WARNING] Please edit .env.gcp with your configuration
        echo.
        set /p EDIT="Open .env.gcp in notepad to edit? (Y/N): "
        if /i "!EDIT!"=="Y" (
            notepad .env.gcp
            echo.
            echo Press any key after saving your changes...
            pause >nul
        )
    ) else (
        echo [ERROR] env.gcp.template not found!
        pause
        exit /b 1
    )
) else (
    echo [OK] .env.gcp already exists
)
echo.

REM Step 4: Authenticate Docker with GCR
echo [4/7] Authenticating Docker with Google Container Registry...
gcloud auth configure-docker gcr.io
if errorlevel 1 (
    echo [ERROR] Docker authentication failed!
    pause
    exit /b 1
)
echo [OK] Docker authenticated
echo.

REM Step 5: Build Docker images
echo [5/7] Building Docker images for GCP...
echo [INFO] This may take 10-15 minutes depending on your internet speed...
echo.

docker-compose -f docker-compose.gcp.yml build

if errorlevel 1 (
    echo [ERROR] Docker build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)
echo [OK] All images built successfully
echo.

REM Step 6: Push to GCR
echo [6/7] Pushing images to Google Container Registry...
echo [INFO] This may take 5-10 minutes...
echo.

docker-compose -f docker-compose.gcp.yml push

if errorlevel 1 (
    echo [ERROR] Image push failed!
    echo Check your internet connection and GCP permissions.
    pause
    exit /b 1
)
echo [OK] All images pushed to GCR
echo.

REM Step 7: Deploy infrastructure
echo [7/7] Deploying infrastructure to GCP...
echo [INFO] Creating compute instance, storage, and networking...
echo.

if exist "gcp-deployment\scripts\deploy-to-gcp.sh" (
    REM Use Git Bash or WSL if available
    where bash >nul 2>&1
    if not errorlevel 1 (
        bash gcp-deployment/scripts/deploy-to-gcp.sh
    ) else (
        echo [WARNING] Bash not found. Please run manually:
        echo   gcp-deployment\scripts\deploy-to-gcp.sh
        echo.
        echo Or use WSL/Git Bash to run the script.
    )
) else (
    echo [INFO] Manual deployment steps:
    echo.
    echo 1. Create GPU instance:
    echo    gcloud compute instances create verolux-gpu-instance --machine-type=g2-standard-8 --zone=%GCP_ZONE%
    echo.
    echo 2. SSH to instance and run:
    echo    gcloud compute ssh verolux-gpu-instance --zone=%GCP_ZONE%
    echo.
    echo 3. Pull and start containers on the instance
)

echo.
echo ════════════════════════════════════════════
echo Deployment Summary
echo ════════════════════════════════════════════
echo.
echo [OK] Docker images built and pushed to GCR
echo [OK] GCP infrastructure deployment initiated
echo.
echo Next Steps:
echo   1. Wait 2-3 minutes for services to start
echo   2. Get instance IP:
echo      gcloud compute instances list
echo.
echo   3. Access your dashboard:
echo      http://[INSTANCE-IP]
echo.
echo   4. Check service health:
echo      http://[INSTANCE-IP]:8000/health
echo.
echo ════════════════════════════════════════════
echo Useful Commands
echo ════════════════════════════════════════════
echo.
echo View instances:
echo   gcloud compute instances list
echo.
echo SSH to instance:
echo   gcloud compute ssh verolux-gpu-instance --zone=%GCP_ZONE%
echo.
echo View logs:
echo   gcloud logging read "resource.type=gce_instance" --limit=100
echo.
echo Check container status (after SSH):
echo   docker-compose -f docker-compose.gcp.yml ps
echo.
echo View container logs (after SSH):
echo   docker-compose -f docker-compose.gcp.yml logs -f
echo.
echo Stop all services (after SSH):
echo   docker-compose -f docker-compose.gcp.yml down
echo.
echo ════════════════════════════════════════════
echo.
echo Deployment complete! 🚀
echo.
pause












