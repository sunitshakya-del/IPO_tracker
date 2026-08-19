# Windows Installer Flow Diagram

## Installation Process

```
User Downloads
    │
    ▼
IPO Tracker-Setup-1.0.0.exe
    │
    ▼
Double-Click to Run
    │
    ▼
┌────────────────────────────────┐
│  Windows Installer (NSIS)      │
│  ┌──────────────────────────┐  │
│  │  Welcome Screen          │  │
│  │  [Next] [Cancel]         │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│  Choose Install Location       │
│  ┌──────────────────────────┐  │
│  │ C:\Users\{User}\AppData\ │  │
│  │    Local\Programs\       │  │
│  │    IPO Tracker\          │  │
│  │ [Browse] [Next]          │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│  Installation Progress         │
│  ┌──────────────────────────┐  │
│  │ ▓▓▓▓▓▓▓▓░░░░░░░░ 45%    │  │
│  │ Extracting files...      │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
    │
    ▼
Installation Complete!
    │
    ├─────────────────────────┐
    │                         │
    ▼                         ▼
Desktop Shortcut        Start Menu Entry
    │                         │
    └──────────┬──────────────┘
               ▼
┌────────────────────────────────┐
│  Setup Complete                │
│  ┌──────────────────────────┐  │
│  │ ☑ Launch IPO Tracker    │  │
│  │ [ ] View README         │  │
│  │ [Finish]                │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
    │
    ▼
Application Launches
    │
    ▼
┌────────────────────────────────┐
│  IPO Tracker Window           │
│  ┌──────────────────────────┐  │
│  │  🔑 Sign in with Google │  │
│  │                          │  │
│  │  [Sign In] Button        │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
    │
    ▼
User Starts Tracking IPOs!
```

## File Structure After Installation

```
Installation Directory:
C:\Users\{User}\AppData\Local\Programs\IPO Tracker\
├── IPO Tracker.exe           ← Main application
├── resources\
│   ├── app.asar              ← Packaged React app
│   └── backend\              ← Python backend
│       ├── server_sqlite.py
│       └── requirements.txt
├── locales\
├── uninstall.exe             ← Uninstaller
└── README.txt

Database Location:
C:\Users\{User}\AppData\Roaming\IPO Tracker\
└── ipo_tracker.db            ← SQLite database (user data)

Desktop:
C:\Users\{User}\Desktop\
└── IPO Tracker.lnk           ← Desktop shortcut

Start Menu:
C:\Users\{User}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\
└── IPO Tracker.lnk           ← Start menu shortcut
```

## Registry Entries (Created by Installer)

```
HKEY_CURRENT_USER\Software\IPOTracker\
├── InstallDir = "C:\Users\{User}\AppData\Local\Programs\IPO Tracker"
└── Version = "1.0.0"

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\IPOTracker\
├── DisplayName = "IPO Tracker"
├── DisplayVersion = "1.0.0"
├── Publisher = "IPO Tracker"
├── InstallLocation = "C:\...\IPO Tracker"
├── UninstallString = "C:\...\IPO Tracker\uninstall.exe"
└── DisplayIcon = "C:\...\IPO Tracker\IPO Tracker.exe"
```

## Application Startup Flow

```
User Double-Clicks Shortcut
    │
    ▼
IPO Tracker.exe Launches
    │
    ├─────────────────────┐
    │                     │
    ▼                     ▼
Electron Window    Python Backend
    │                     │
    │              ┌──────┴──────┐
    │              │ server_sqlite.py
    │              │ Port: 8001
    │              │ Database: SQLite
    │              └──────┬──────┘
    │                     │
    │◄────────API─────────┤
    │                     │
    ▼                     ▼
React App Loads    Database Ready
    │                     │
    └──────────┬──────────┘
               │
               ▼
   User Sees Login Screen
               │
               ▼
     Application Ready!
```

## Uninstallation Flow

```
Control Panel → Programs → Uninstall
    │
    ▼
Select "IPO Tracker"
    │
    ▼
Click [Uninstall]
    │
    ▼
┌────────────────────────────────┐
│  Confirm Uninstall             │
│  ┌──────────────────────────┐  │
│  │ Remove IPO Tracker?      │  │
│  │ [Yes] [No]               │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
    │
    ▼
Uninstaller Runs
    │
    ├───────────────────────────┐
    │                           │
    ▼                           ▼
Remove Program Files    Remove Shortcuts
    │                           │
    ▼                           ▼
Remove Registry Entries    Clean Up
    │                           │
    └────────────┬──────────────┘
                 │
                 ▼
        Optional: Keep Data?
                 │
         ┌───────┴───────┐
         │               │
         ▼               ▼
    Keep Database    Delete Database
         │               │
         └───────┬───────┘
                 │
                 ▼
    Uninstallation Complete!
```

## Build Process Flow

```
Developer Machine (Windows/Mac/Linux)
    │
    ▼
cd /frontend
    │
    ▼
yarn install
    │
    ▼
yarn build
    │
    ├─── React Production Build
    │    └─── /frontend/build/
    │         ├── index.html
    │         ├── static/
    │         └── assets/
    │
    ▼
yarn dist
    │
    ├─── Electron Builder Process
    │    │
    │    ├─── Package React App
    │    ├─── Bundle Backend Files
    │    ├─── Add Electron Runtime
    │    ├─── Create NSIS Installer
    │    └─── Create Portable .exe
    │
    ▼
Output in /dist/
    │
    ├── IPO Tracker-Setup-1.0.0.exe        (75-150 MB)
    ├── IPO Tracker-Portable-1.0.0.exe     (75-150 MB)
    └── win-unpacked/                      (Uncompressed)
    │
    ▼
Upload to Distribution Server
    │
    ├─── GitHub Releases
    ├─── Own Website
    ├─── Microsoft Store
    └─── Cloud Storage
    │
    ▼
Users Download & Install!
```

## Portable Version Flow

```
User Downloads
    │
    ▼
IPO Tracker-Portable-1.0.0.exe
    │
    ▼
Copy to Any Location
    │  (Desktop, USB Drive, Network Share)
    │
    ▼
Double-Click to Run
    │
    ▼
Application Starts
    │
    ├─── No Installation
    ├─── No Registry Changes
    ├─── No Admin Rights Needed
    │
    ▼
Database Created in Same Folder
    │
    └── IPO Tracker-Portable-1.0.0.exe
        └── ipo_tracker.db
    │
    ▼
Portable & Ready to Use!
```

## Size Breakdown

```
IPO Tracker-Setup-1.0.0.exe (Total: ~120 MB compressed)
    │
    ├── Electron Runtime          ~80 MB  (67%)
    │   └── Chromium Engine       ~40 MB  (33%)
    │   └── Node.js Runtime       ~10 MB  (8%)
    │
    ├── Application Code          ~15 MB  (13%)
    │   ├── React Build           ~8 MB   (7%)
    │   ├── Backend Python        ~5 MB   (4%)
    │   └── Dependencies          ~2 MB   (2%)
    │
    ├── NSIS Installer Overhead   ~5 MB   (4%)
    │
    └── Resources & Assets        ~20 MB  (16%)
        ├── Icons                 ~1 MB   (1%)
        ├── Node Modules          ~18 MB  (15%)
        └── Misc                  ~1 MB   (1%)
```

## Version Updates Flow

```
Developer Releases v1.0.1
    │
    ▼
User Opens App (v1.0.0)
    │
    ▼
Auto-Updater Checks Server
    │
    ├─── No Update Available
    │    └── Continue Using App
    │
    └─── Update Available!
         │
         ▼
    ┌──────────────────────────┐
    │ Update Available         │
    │ v1.0.0 → v1.0.1         │
    │                          │
    │ [Update] [Skip] [Later] │
    └──────────────────────────┘
         │
         ▼
    Download Update in Background
         │
         ▼
    Install on Next Launch
         │
         ▼
    User Restarts App
         │
         ▼
    Running v1.0.1!
```

---

**Summary:**
- Simple user experience: Download → Install → Use
- Professional installer with progress and options
- Automatic shortcuts creation
- Clean uninstallation
- Optional portable version for flexibility
