# 📦 Windows Installer Creation Guide

## Overview

This guide explains how to create a professional Windows installer (.exe) for the IPO Tracker desktop application.

## 🎯 Final Output

When you complete this process, you'll have:

```
IPO Tracker-Setup-1.0.0.exe          ← NSIS Installer (recommended)
IPO Tracker-Portable-1.0.0.exe       ← Portable version (no install needed)
```

## 📋 Prerequisites

### System Requirements
- **Operating System:** Windows 10+ (64-bit)
- **Node.js:** Version 20.x or higher
- **Python:** Version 3.11 or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** At least 2GB free

### Software Installation
```bash
# 1. Install Node.js from https://nodejs.org/
# 2. Install Python from https://python.org/
# 3. Install Git from https://git-scm.com/
```

## 🚀 Step-by-Step Build Process

### Step 1: Clone Repository to Windows PC
```bash
git clone <your-repository-url>
cd ipo-tracker
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
pip install aiosqlite databases sqlalchemy
cd ..
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
yarn install
```

### Step 4: Create Application Icon (Optional but Recommended)
```bash
# Place your icon files in frontend/assets/
# Required file: icon.ico (256x256 pixels)
```

**Create Icon Online:**
- Use https://convertio.co/png-ico/ 
- Upload a 256×256 PNG image
- Download as icon.ico
- Place in `/frontend/assets/icon.ico`

**Icon Design Tips:**
- Use simple, recognizable design
- Ensure visibility at small sizes (16×16, 32×32)
- Use high contrast colors
- Test on light and dark backgrounds

### Step 5: Build React Application
```bash
cd frontend
yarn build
```

This creates an optimized production build in `frontend/build/`

**Expected Output:**
```
Creating an optimized production build...
Compiled successfully!

File sizes after gzip:
  125.5 kB  build/static/js/main.[hash].js
  25.2 kB   build/static/css/main.[hash].css

The build folder is ready to be deployed.
```

### Step 6: Create Windows Installer
```bash
# Still in frontend directory
yarn dist
```

**What Happens:**
1. Electron Builder packages your app
2. Bundles Node.js runtime
3. Creates NSIS installer
4. Creates portable .exe (optional)
5. Outputs to `frontend/dist/`

**Build Time:** 5-15 minutes (depending on your machine)

**Expected Output:**
```
  • electron-builder  version=24.13.3
  • loaded configuration  file=package.json ("build" field)
  • writing effective config  file=dist/builder-effective-config.yaml
  • packaging       platform=win32 arch=x64 electron=28.0.0 appOutDir=dist\win-unpacked
  • building        target=nsis file=dist\IPO Tracker-Setup-1.0.0.exe
  • building        target=portable file=dist\IPO Tracker-Portable-1.0.0.exe
  • building block map  blockMapFile=dist\IPO Tracker-Setup-1.0.0.exe.blockmap
```

## 📦 Output Files

After successful build, you'll find in `frontend/dist/`:

```
frontend/dist/
├── IPO Tracker-Setup-1.0.0.exe          ← Main installer (65-150 MB)
├── IPO Tracker-Portable-1.0.0.exe       ← Portable version (65-150 MB)
├── IPO Tracker-Setup-1.0.0.exe.blockmap ← Update file
├── win-unpacked/                         ← Unpacked app (for testing)
│   ├── IPO Tracker.exe
│   ├── resources/
│   └── ...
├── builder-effective-config.yaml        ← Build configuration
└── builder-debug.yml                    ← Build logs
```

## 🎨 Installer Features

### NSIS Installer (`IPO Tracker-Setup-1.0.0.exe`)

**Installation Flow:**
1. **Welcome Screen**
   ```
   Welcome to IPO Tracker Setup
   [Next] [Cancel]
   ```

2. **License Agreement** (if you add one)
   ```
   Please read the following license agreement
   [I Agree] [Cancel]
   ```

3. **Installation Directory**
   ```
   Choose Install Location
   Default: C:\Users\{Username}\AppData\Local\Programs\IPO Tracker
   [Browse] [Next] [Cancel]
   ```

4. **Installation Progress**
   ```
   Installing IPO Tracker...
   [Progress bar]
   Extracting files...
   Creating shortcuts...
   ```

5. **Finish Screen**
   ```
   Completing IPO Tracker Setup
   ☑ Launch IPO Tracker
   ☑ View README
   [Finish]
   ```

**What Gets Installed:**
- ✅ Application files in Program Files
- ✅ Desktop shortcut (optional during install)
- ✅ Start Menu entry
- ✅ Database folder in AppData
- ✅ Uninstaller in Control Panel

### Portable Version (`IPO Tracker-Portable-1.0.0.exe`)

**No Installation Required:**
- Just double-click to run
- Creates database in same folder
- Perfect for USB drives
- No registry entries
- No admin rights needed

## 🧪 Testing the Installer

### Test on Clean Windows Machine

**Important:** Always test installers on a clean Windows machine that:
- Doesn't have Python installed
- Doesn't have Node.js installed  
- Represents your typical end-user

### Testing Checklist

1. **Installation Process**
   - [ ] Installer downloads and opens
   - [ ] Welcome screen displays correctly
   - [ ] Can choose installation directory
   - [ ] Installation completes without errors
   - [ ] Desktop shortcut created
   - [ ] Start Menu entry created

2. **First Launch**
   - [ ] Application opens without errors
   - [ ] Login screen displays
   - [ ] Can login with Google OAuth
   - [ ] Database file created in AppData

3. **Core Functionality**
   - [ ] Can create Demat account
   - [ ] Can add IPO
   - [ ] P&L calculations correct
   - [ ] Dashboard displays stats
   - [ ] Can edit/delete records

4. **Application Lifecycle**
   - [ ] Application closes cleanly
   - [ ] Can reopen application
   - [ ] Data persists between sessions
   - [ ] Multiple launches work

5. **Uninstallation**
   - [ ] Can uninstall from Control Panel
   - [ ] Shortcuts removed
   - [ ] Registry entries cleaned (optional: keep data)

## ⚠️ Common Build Issues

### Issue 1: "electron-builder not found"
```bash
# Solution
cd frontend
yarn add -D electron-builder
```

### Issue 2: "Cannot find module 'electron'"
```bash
# Solution
yarn add -D electron
```

### Issue 3: "Icon file not found"
```
# Solution: Create placeholder or add actual icon
mkdir -p assets
# Add icon.ico to assets folder
```

### Issue 4: "Build fails - out of memory"
```bash
# Solution: Increase Node.js memory
set NODE_OPTIONS=--max-old-space-size=4096
yarn dist
```

### Issue 5: Python backend not bundled
**Current Limitation:** Backend requires Python installed on user's machine.

**Future Solution:** Bundle with PyInstaller
```bash
pip install pyinstaller
cd backend
pyinstaller --onefile --name ipo-tracker-backend server_sqlite.py
```

## 🔒 Code Signing (Optional but Recommended)

### Why Code Sign?
- Prevents "Unknown Publisher" warnings
- Builds user trust
- Improves Microsoft Defender SmartScreen score
- Professional appearance

### How to Code Sign

1. **Purchase Code Signing Certificate**
   - DigiCert
   - Sectigo
   - GlobalSign
   - Cost: ~$100-400/year

2. **Install Certificate on Windows**
   - Import .pfx file
   - Install in Windows Certificate Store

3. **Sign the Installer**
```bash
# Using SignTool (Windows SDK)
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com "IPO Tracker-Setup-1.0.0.exe"
```

4. **Configure electron-builder**
```json
"win": {
  "certificateFile": "certificate.pfx",
  "certificatePassword": "your-password",
  "signingHashAlgorithms": ["sha256"],
  "timeStampServer": "http://timestamp.digicert.com"
}
```

## 📊 Installer Size Optimization

### Current Size: ~100-150 MB

**What's Included:**
- Electron runtime: ~80 MB
- Chromium engine: ~40 MB
- Node.js runtime: ~10 MB
- Your app code: ~5-10 MB
- Python backend: ~5 MB
- Dependencies: ~10-20 MB

### Optimization Tips

1. **Remove Dev Dependencies**
```json
// package.json - ensure devDependencies are not bundled
"files": [
  "build/**/*",
  "!build/**/*.map"  // Remove source maps
]
```

2. **Compress with NSIS**
```json
"nsis": {
  "compression": "maximum"
}
```

3. **Use Portable Version**
- No installer overhead
- Slightly smaller size

## 🚀 Distribution Options

### Option 1: Direct Download
- Host .exe on your website
- Users download and install
- Simple but no auto-updates

### Option 2: GitHub Releases
- Upload to GitHub Releases
- Users download from GitHub
- Version history maintained

### Option 3: Microsoft Store
- Submit to Windows Store
- Professional distribution
- Requires developer account ($19)

### Option 4: Auto-Update Server
- Implement electron-updater
- Host updates on your server
- Automatic update notifications

## 📝 Release Checklist

Before releasing to users:

- [ ] Test installer on multiple Windows versions (10, 11)
- [ ] Test on clean machines without Python/Node
- [ ] Verify all features work correctly
- [ ] Test uninstaller
- [ ] Create user documentation
- [ ] Create video tutorial (optional)
- [ ] Test portable version
- [ ] Code sign the installer (recommended)
- [ ] Create release notes
- [ ] Test auto-update (if implemented)

## 📖 Creating README.txt for Installer

Create `/frontend/build/README.txt`:

```text
IPO Tracker - Profit & Loss Manager
Version 1.0.0

SYSTEM REQUIREMENTS
- Windows 10 or higher (64-bit)
- 4 GB RAM minimum
- 500 MB free disk space
- Internet connection (for Google login)

INSTALLATION
1. Run IPO Tracker-Setup-1.0.0.exe
2. Follow the installation wizard
3. Launch from desktop shortcut

FIRST TIME SETUP
1. Click "Sign in with Google"
2. Authorize with your Google account
3. Start tracking your IPOs!

DATA STORAGE
Your data is stored locally at:
C:\Users\{YourName}\AppData\Roaming\IPO Tracker\ipo_tracker.db

SUPPORT
Email: support@ipotracker.com
Website: https://ipotracker.com

LICENSE
[Your license information]

Copyright © 2026 IPO Tracker
```

## 🎉 Success!

After completing these steps, you'll have:

✅ Professional Windows installer  
✅ Desktop shortcut  
✅ Start Menu entry  
✅ Portable version (bonus!)  
✅ Uninstaller in Control Panel  
✅ Production-ready application  

## 📚 Additional Resources

- [Electron Builder Docs](https://www.electron.build/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
- [Code Signing Guide](https://www.electron.build/code-signing)
- [Windows Installer Best Practices](https://docs.microsoft.com/en-us/windows/win32/msi/installer-best-practices)

---

**Next Steps:**
1. Build the installer: `yarn dist`
2. Test on clean Windows machine
3. Distribute to users!

Good luck with your Windows installer! 🚀
