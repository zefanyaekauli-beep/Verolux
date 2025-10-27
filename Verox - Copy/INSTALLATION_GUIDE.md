# Verolux1st - Complete Installation Guide

## 🚀 **Quick Start (Recommended)**

### **Option 1: One-Click Installation**
```bash
# Download and run the complete setup script
curl -o install_verolux.bat https://raw.githubusercontent.com/your-repo/verolux-enterprise/main/install_verolux.bat
install_verolux.bat
```

### **Option 2: Manual Installation**
Follow the step-by-step guide below.

---

## 📋 **System Requirements**

### **Minimum Requirements:**
- **OS**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional, for AI features)
- **Internet**: Required for initial setup and AI model downloads

### **Software Requirements:**
- **Python**: 3.8+ (3.10+ recommended)
- **Node.js**: 16+ (18+ recommended)
- **Git**: Latest version
- **Chrome/Firefox**: For web interface

---

## 🔧 **Installation Steps**

### **Step 1: Clone Repository**
```bash
git clone https://github.com/your-repo/verolux-enterprise.git
cd verolux-enterprise
```

### **Step 2: Install Python Dependencies**
```bash
# Install Python packages
pip install -r Backend/requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r Backend/requirements.txt
```

### **Step 3: Install Node.js Dependencies**
```bash
cd Frontend
npm install
cd ..
```

### **Step 4: Download AI Models**
```bash
# Download YOLO model (if not present)
python Backend/download_models.py
```

### **Step 5: Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

---

## 🚀 **Running the System**

### **Option 1: Complete System (All Features)**
```bash
# Windows
START_COMPLETE_SYSTEM.bat

# Linux/macOS
./start_complete_system.sh
```

### **Option 2: Individual Components**

#### **Backend Only:**
```bash
# Main detection backend
cd Backend
python backend_server.py

# Analytics backend (separate terminal)
cd Backend
python analytics_system.py

# Reporting backend (separate terminal)
cd Backend
python reporting_system.py

# Semantic search backend (separate terminal)
cd Backend
python semantic_search.py
```

#### **Frontend Only:**
```bash
cd Frontend
npm run dev
```

---

## 🌐 **Access URLs**

After starting the system, access these URLs:

- **Main Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Analytics API**: http://localhost:8002
- **Reporting API**: http://localhost:8001
- **Semantic Search API**: http://localhost:8003

---

## ⚙️ **Configuration**

### **Environment Variables (.env)**
```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ANALYTICS_PORT=8002
REPORTING_PORT=8001
SEMANTIC_PORT=8003

# AI Model Configuration
MODEL_PATH=Backend/models/weight.pt
CONFIDENCE_THRESHOLD=0.5
DEVICE=cuda  # or cpu

# Database Configuration
DATABASE_URL=sqlite:///verolux_enterprise.db

# Google Maps API (for GPS features)
GOOGLE_MAPS_API_KEY=your_api_key_here

# Language Configuration
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,id,zh
```

### **Camera Configuration**
```yaml
# cameras.yaml
cameras:
  - id: webcam_0
    name: "Main Webcam"
    source: 0
    enabled: true
  - id: webcam_1
    name: "Secondary Webcam"
    source: 1
    enabled: false
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **1. Port Already in Use**
```bash
# Find and kill process using port
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### **2. Python Dependencies Issues**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall requirements
pip install -r Backend/requirements.txt --force-reinstall
```

#### **3. Node.js Dependencies Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### **4. CUDA/GPU Issues**
```bash
# Check CUDA installation
nvidia-smi

# Install CPU-only PyTorch if CUDA not available
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### **5. Model Loading Issues**
```bash
# Download models manually
python Backend/download_models.py --force-download

# Check model file
ls -la Backend/models/
```

---

## 📊 **Performance Optimization**

### **For Better Performance:**

#### **1. GPU Acceleration**
```bash
# Install CUDA toolkit
# Download from: https://developer.nvidia.com/cuda-downloads

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### **2. Memory Optimization**
```bash
# Set environment variables
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0
```

#### **3. Database Optimization**
```bash
# Use PostgreSQL for production
pip install psycopg2-binary
# Update DATABASE_URL in .env
```

---

## 🔐 **Security Configuration**

### **Production Setup:**

#### **1. HTTPS Configuration**
```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update backend configuration
BACKEND_SSL_CERT=cert.pem
BACKEND_SSL_KEY=key.pem
```

#### **2. Authentication**
```bash
# Enable authentication
AUTH_ENABLED=true
JWT_SECRET_KEY=your_secret_key_here
```

#### **3. API Rate Limiting**
```bash
# Configure rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

---

## 📱 **Mobile Access**

### **Mobile Configuration:**
1. Ensure your device is on the same network
2. Find your computer's IP address
3. Access: `http://YOUR_IP:5173`

### **Network Configuration:**
```bash
# Allow external connections
BACKEND_HOST=0.0.0.0
FRONTEND_HOST=0.0.0.0
```

---

## 🆘 **Support**

### **Getting Help:**
1. **Documentation**: Check this guide and README files
2. **Issues**: Report bugs on GitHub Issues
3. **Discord**: Join our community Discord
4. **Email**: support@verolux.com

### **Logs and Debugging:**
```bash
# View backend logs
tail -f Backend/logs/backend.log

# View frontend logs
npm run dev -- --debug

# Check system status
python Backend/health_check.py
```

---

## 🎯 **Quick Commands Reference**

```bash
# Start everything
./START_COMPLETE_SYSTEM.bat

# Start individual services
python Backend/backend_server.py
python Backend/analytics_system.py
python Backend/reporting_system.py
python Backend/semantic_search.py
cd Frontend && npm run dev

# Stop all services
./STOP_ALL_SERVICES.bat

# Update system
git pull
pip install -r Backend/requirements.txt
cd Frontend && npm install

# Reset database
python Backend/reset_database.py

# Health check
python Backend/health_check.py
```

---

## ✅ **Verification**

After installation, verify everything works:

1. **Backend Health**: http://localhost:8000/health
2. **Frontend**: http://localhost:5173
3. **Camera Feed**: Check Cameras page
4. **Analytics**: Check Analytics page
5. **Reports**: Check Reports page
6. **Semantic Search**: Check Semantic Search page
7. **Heatmap**: Check Heatmap page
8. **Language**: Test language switcher in topbar

---

**🎉 Congratulations! Your Verolux1st system is now ready!**

