# IPO Tracker - Desktop Application (Windows .exe)

## 🎯 Overview
This is a **self-contained Windows desktop application** that runs entirely offline. No internet or external server required.

**Architecture:**
```
Windows .exe (Electron)
    ├── React Frontend
    ├── FastAPI Backend (bundled)
    └── SQLite Database (local file in AppData)
```

## 📦 What's Included

- **Electron Wrapper**: Converts web app to native Windows application
- **Local Database**: SQLite database stored in user's AppData folder
- **Bundled Backend**: Python FastAPI server runs automatically in background
- **Single Installer**: One `.exe` file installs everything
- **No Dependencies**: Installs all dependencies automatically

## 🚀 Building the Windows .exe

### Prerequisites
```bash
# Install Python dependencies for SQLite backend
cd backend
pip install aiosqlite databases sqlalchemy

# Install Node.js dependencies
cd ../frontend
yarn install
```

### Development Mode (Test Before Building)
```bash
cd frontend

# Run Electron app in development mode
yarn electron-dev
```

This will:
1. Start React dev server on port 3000
2. Start Python backend on port 8001
3. Open Electron window with the app

### Production Build (Create .exe)
```bash
cd frontend

# Build Windows x64 installer
yarn dist
```

This will create:
- `/frontend/dist/IPO Tracker Setup 1.0.0.exe` - Windows installer
- User can double-click to install
- Creates desktop shortcut and Start Menu entry

## 📁 Output Files

After running `yarn dist`, you'll find:

```
frontend/dist/
├── IPO Tracker Setup 1.0.0.exe     # 📦 Windows Installer
├── win-unpacked/                    # Unpacked app (for testing)
└── builder-debug.yml                # Build logs
```

## 🎨 Customization

### Application Icon
Place your icon files in `/frontend/assets/`:
- `icon.ico` - Windows icon (256x256)
- `icon.png` - Linux/Mac icon

### Application Name & Version
Edit `/frontend/package.json`:
```json
{
  "name": "ipo-tracker",
  "productName": "IPO Tracker",
  "version": "1.0.0",
  "description": "IPO Profit & Loss Manager",
  "author": "Your Name"
}
```

### Installer Options
Edit the `build` section in `/frontend/package.json`:
```json
{
  "build": {
    "appId": "com.ipotracker.app",
    "productName": "IPO Tracker",
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    }
  }
}
```

## 📊 Database Location

**Development:** `/app/backend/ipo_tracker.db`
**Production:** `C:\Users\{Username}\AppData\Roaming\IPO Tracker\ipo_tracker.db`

## 🔧 How It Works

1. **User double-clicks the .exe installer**
2. **Installation**: App is installed to Program Files
3. **First Launch**:
   - Electron creates a window
   - Python backend starts automatically (port 8001)
   - SQLite database is created in AppData
   - React app loads in the window
4. **Usage**: User interacts with the app like a normal Windows application
5. **Data Storage**: All data saved locally in SQLite database
6. **Closing**: Backend process automatically terminates when app closes

## 🛠️ Technical Details

### Backend Server
- **File**: `/backend/server_sqlite.py`
- **Port**: 127.0.0.1:8001 (localhost only)
- **Database**: SQLite with aiosqlite (async)
- **Auto-start**: Launched by Electron main process

### Frontend
- **File**: `/frontend/public/electron.js` (Electron main process)
- **React**: Built and bundled into `/frontend/build/`
- **API Calls**: Point to `http://localhost:8001/api`

### Electron Configuration
- **Main Process**: `/frontend/public/electron.js`
- **Window Size**: 1400x900 (min: 1000x700)
- **Menu**: Auto-hide (cleaner UI)
- **Dev Tools**: Enabled in development mode

## 🐛 Troubleshooting

### Issue: "Python not found"
**Solution**: Bundle Python with the app or require users to install Python 3.11+

### Issue: Database errors
**Solution**: Check write permissions in AppData folder

### Issue: Port 8001 already in use
**Solution**: Kill existing Python processes or change port in `electron.js`

### Issue: Build fails
**Solution**: 
```bash
# Clean and rebuild
cd frontend
rm -rf node_modules dist build
yarn install
yarn dist
```

## 📝 Notes

### Current Limitations
1. **Google OAuth**: Currently requires internet for first-time login. Consider adding offline mode or local auth.
2. **Python Bundling**: Python backend needs to be bundled using PyInstaller or similar for production.
3. **Icon**: Need to create proper .ico file for Windows.

### Future Improvements
1. Bundle Python backend into single executable (using PyInstaller)
2. Add auto-update functionality (electron-updater)
3. Create Mac (.dmg) and Linux (.AppImage) versions
4. Add offline authentication option
5. Implement data import/export for backup

## 📚 Resources

- [Electron Documentation](https://www.electronjs.org/docs/latest/)
- [Electron Builder](https://www.electron.build/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [SQLite with Python](https://docs.python.org/3/library/sqlite3.html)

---

## ⚠️ Important: Before Distribution

1. **Bundle Python**: Package Python with PyInstaller
2. **Code Signing**: Sign the .exe with a code signing certificate
3. **Testing**: Test on clean Windows machines
4. **License**: Add proper license and terms
5. **Documentation**: Create user manual

---

Built with ❤️ using React, Electron, FastAPI, and SQLite
