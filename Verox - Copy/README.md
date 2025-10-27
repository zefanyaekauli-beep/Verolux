# 🚀 Verolux1st - AI-Powered Surveillance System

> **Advanced AI-powered surveillance and analytics platform with real-time object detection, semantic search, and comprehensive reporting capabilities.**

## ✨ **Features**

- 🎯 **Real-time Object Detection** with YOLO
- 📊 **Advanced Analytics Dashboard**
- 📋 **Comprehensive Reporting System**
- 🧠 **Semantic Search Engine**
- 🗺️ **GPS Heatmap Visualization**
- 🌐 **Multi-language Support** (English, Bahasa Indonesia, Mandarin)
- 📱 **Responsive Web Interface**

## 🚀 **Quick Start**

### **Windows**
```bash
# 1. Download and extract Verolux1st
# 2. Double-click INSTALL_VEROLUX1ST.bat
# 3. Run START_VEROLUX1ST.bat
# 4. Access at http://localhost:5173
```

### **Linux/macOS**
```bash
# 1. Download and extract Verolux1st
# 2. chmod +x INSTALL_VEROLUX1ST.sh
# 3. ./INSTALL_VEROLUX1ST.sh
# 4. ./START_VEROLUX1ST.sh
# 5. Access at http://localhost:5173
```

## 🛠️ **Tech Stack**

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, OpenCV, Ultralytics YOLO, SQLite |
| **Frontend** | React 18, Vite, Framer Motion, Zustand |
| **AI/ML** | YOLO, Sentence Transformers, Scikit-learn |
| **Database** | SQLite with vector search capabilities |
| **Maps** | Google Maps API with heatmap visualization |

## 📁 **Project Structure**

```
Verolux1st/
├── Backend/                    # Python backend services
│   ├── backend_server.py       # Main API server
│   ├── analytics_system.py     # Analytics service
│   ├── reporting_system.py     # Reporting service
│   ├── semantic_search.py      # Semantic search service
│   └── requirements.txt        # Python dependencies
├── Frontend/                   # React frontend
│   ├── src/                    # Source code
│   ├── public/                 # Static assets
│   └── package.json            # Node.js dependencies
├── INSTALL_VEROLUX1ST.bat      # Windows installer
├── INSTALL_VEROLUX1ST.sh       # Linux/macOS installer
├── START_VEROLUX1ST.bat        # Windows startup script
├── START_VEROLUX1ST.sh         # Linux/macOS startup script
└── README_INSTALLATION.md      # Detailed installation guide
```

## 🌐 **Access Points**

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **Analytics** | http://localhost:8002 | Analytics service |
| **Reporting** | http://localhost:8001 | Reporting service |
| **Semantic Search** | http://localhost:8003 | Search API |

## 📋 **System Requirements**

- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8+ (3.10+ recommended)
- **Node.js**: 16+ (18+ recommended)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 5GB free space

## 📚 **Documentation**

- **[Installation Guide](README_INSTALLATION.md)** - Detailed setup instructions
- **[API Documentation](http://localhost:8000/docs)** - Available after installation
- **[System Requirements](README_INSTALLATION.md#system-requirements)** - Hardware/software requirements

## 🚨 **Troubleshooting**

### **Common Issues**
- **Python not found**: Install Python 3.8+ from [python.org](https://python.org)
- **Node.js not found**: Install Node.js 16+ from [nodejs.org](https://nodejs.org)
- **Port conflicts**: Check if ports 8000-8003 and 5173 are available
- **Permission errors**: Run as administrator (Windows) or use `sudo` (Linux/macOS)

### **Reset Installation**
```bash
# Remove dependencies and reinstall
rm -rf Backend/venv Frontend/node_modules  # Linux/macOS
rmdir /s Backend\venv Frontend\node_modules  # Windows

# Reinstall
./INSTALL_VEROLUX1ST.sh  # Linux/macOS
INSTALL_VEROLUX1ST.bat   # Windows
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 **Success!**

Once installed, you'll have a fully functional AI-powered surveillance system with real-time object detection, advanced analytics, semantic search, and comprehensive reporting capabilities.

**Welcome to Verolux1st!** 🚀