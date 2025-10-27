# 🚀 Verolux1st - Installation Guide

## 📋 **System Requirements**

### **Minimum Requirements**
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8+ (3.10+ recommended)
- **Node.js**: 16+ (18+ recommended)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 5GB free space
- **Internet**: Required for initial setup

### **Recommended Requirements**
- **OS**: Windows 11, macOS 12+, or Ubuntu 20.04+
- **Python**: 3.10+
- **Node.js**: 18+
- **RAM**: 16GB+
- **Storage**: 10GB+ free space
- **GPU**: NVIDIA GPU with CUDA support (optional)

---

## 🚀 **Quick Installation**

### **Windows**
1. **Download** the Verolux1st folder
2. **Double-click** `INSTALL_VEROLUX1ST.bat`
3. **Wait** for installation to complete
4. **Run** `START_VEROLUX1ST.bat` to start the system

### **Linux/macOS**
1. **Download** the Verolux1st folder
2. **Open terminal** in the folder
3. **Run**: `chmod +x INSTALL_VEROLUX1ST.sh && ./INSTALL_VEROLUX1ST.sh`
4. **Run**: `./START_VEROLUX1ST.sh` to start the system

---

## 🔧 **Manual Installation**

### **Step 1: Install Dependencies**

#### **Python Dependencies**
```bash
cd Backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

#### **Node.js Dependencies**
```bash
cd Frontend
npm install
```

### **Step 2: Download AI Models**
```bash
cd Backend
python download_models.py
```

### **Step 3: Initialize Database**
```bash
cd Backend
python -c "import sqlite3; conn = sqlite3.connect('verolux1st.db'); conn.close()"
```

### **Step 4: Start Services**

#### **Backend Services**
```bash
# Terminal 1 - Main Backend
cd Backend
venv\Scripts\activate  # Windows
python backend_server.py

# Terminal 2 - Analytics
cd Backend
venv\Scripts\activate  # Windows
python analytics_system.py

# Terminal 3 - Reporting
cd Backend
venv\Scripts\activate  # Windows
python reporting_system.py

# Terminal 4 - Semantic Search
cd Backend
venv\Scripts\activate  # Windows
python semantic_search.py
```

#### **Frontend Service**
```bash
# Terminal 5 - Frontend
cd Frontend
npm run dev
```

---

## 🌐 **Access the System**

Once all services are running, access the system at:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Analytics**: http://localhost:8002
- **Reporting**: http://localhost:8001
- **Semantic Search**: http://localhost:8003

---

## 📁 **Project Structure**

```
Verolux1st/
├── Backend/                 # Python backend services
│   ├── backend_server.py    # Main API server
│   ├── analytics_system.py  # Analytics service
│   ├── reporting_system.py  # Reporting service
│   ├── semantic_search.py   # Semantic search service
│   ├── requirements.txt     # Python dependencies
│   ├── models/             # AI models directory
│   └── uploads/            # File uploads directory
├── Frontend/               # React frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Build configuration
├── INSTALL_VEROLUX1ST.bat  # Windows installer
├── INSTALL_VEROLUX1ST.sh   # Linux/macOS installer
├── START_VEROLUX1ST.bat    # Windows startup script
├── START_VEROLUX1ST.sh     # Linux/macOS startup script
└── README.md              # Main documentation
```

---

## 🎯 **Features**

### **Core Features**
- 🎯 **Real-time Object Detection** with YOLO
- 📊 **Advanced Analytics Dashboard**
- 📋 **Comprehensive Reporting System**
- 🧠 **Semantic Search Engine**
- 🗺️ **GPS Heatmap Visualization**
- 🌐 **Multi-language Support** (English, Bahasa Indonesia, Mandarin)
- 📱 **Responsive Web Interface**

### **AI Capabilities**
- **Object Detection**: Person, vehicle, and object recognition
- **Semantic Search**: Natural language search with AI
- **Real-time Processing**: Live video stream analysis
- **Data Analytics**: Advanced insights and reporting

---

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ANALYTICS_PORT=8002
REPORTING_PORT=8001
SEMANTIC_PORT=8003

# AI Model Configuration
MODEL_PATH=./Backend/models/weight.pt
DEVICE=cuda  # or cpu

# Database Configuration
DATABASE_URL=sqlite:///./Backend/verolux1st.db
```

### **Port Configuration**
- **8000**: Main Backend API
- **8001**: Reporting System
- **8002**: Analytics System
- **8003**: Semantic Search
- **5173**: Frontend Development Server

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Python Issues**
```bash
# If Python not found
python3 --version  # Try python3 instead of python

# If pip not found
python -m pip install --upgrade pip
```

#### **Node.js Issues**
```bash
# If npm not found
node --version
npm --version

# Clear npm cache
npm cache clean --force
```

#### **Port Conflicts**
```bash
# Check if ports are in use
netstat -an | findstr :8000  # Windows
lsof -i :8000                # Linux/macOS
```

#### **Permission Issues (Linux/macOS)**
```bash
# Make scripts executable
chmod +x *.sh
chmod +x INSTALL_VEROLUX1ST.sh
chmod +x START_VEROLUX1ST.sh
```

### **Reset Installation**
```bash
# Remove virtual environment
rm -rf Backend/venv          # Linux/macOS
rmdir /s Backend\venv        # Windows

# Remove node_modules
rm -rf Frontend/node_modules # Linux/macOS
rmdir /s Frontend\node_modules # Windows

# Reinstall
./INSTALL_VEROLUX1ST.sh      # Linux/macOS
INSTALL_VEROLUX1ST.bat       # Windows
```

---

## 📚 **Documentation**

- **Main README**: `README.md`
- **API Documentation**: Available at http://localhost:8000/docs
- **Installation Guide**: This file
- **System Requirements**: See requirements section above

---

## 🆘 **Support**

If you encounter issues:

1. **Check** the troubleshooting section above
2. **Verify** all requirements are met
3. **Check** that all ports are available
4. **Review** the console output for error messages
5. **Restart** the installation process if needed

---

## 🎉 **Success!**

Once installation is complete, you'll have a fully functional Verolux1st system with:

- ✅ Real-time object detection
- ✅ Advanced analytics
- ✅ Comprehensive reporting
- ✅ Semantic search capabilities
- ✅ GPS heatmap visualization
- ✅ Multi-language support
- ✅ Responsive web interface

**Enjoy using Verolux1st!** 🚀

