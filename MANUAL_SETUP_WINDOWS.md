# IPO Tracker - Manual Windows Setup Guide

## Quick Setup Instructions

Follow these steps to manually create the project on your Windows PC.

## Prerequisites

Before starting, install:
1. **Node.js 20+**: https://nodejs.org/ (Download LTS version)
2. **Python 3.11+**: https://python.org/ (Check "Add to PATH" during install)
3. **Git**: https://git-scm.com/ (Optional, for downloading files)

## Step-by-Step Setup

### Part 1: Create Folder Structure

Open Command Prompt (cmd) and run these commands ONE BY ONE:

```cmd
cd C:\Users\Administrator\Desktop
mkdir ipo-tracker
cd ipo-tracker
mkdir backend
mkdir frontend
cd frontend
mkdir public
mkdir src
mkdir src\pages
mkdir src\components
mkdir src\components\ui
mkdir src\utils
mkdir assets
cd ..
```

### Part 2: Download All Files

Since you're reading this, you have access to the Emergent container. 

**Option A: Use Emergent's File Browser**
- Look for a file explorer or file manager in Emergent
- Download these folders/files to your Desktop

**Option B: Copy Files Individually**
I'll provide you the essential files below. Create each file using Notepad:

---

## Essential Files to Create

### 1. backend\requirements.txt

```cmd
cd C:\Users\Administrator\Desktop\ipo-tracker\backend
notepad requirements.txt
```

Paste this content and save:
```
fastapi==0.115.6
uvicorn[standard]==0.34.0
motor==3.7.0
python-dotenv==1.0.1
pydantic==2.10.6
httpx==0.28.1
aiosqlite==0.22.1
databases==0.9.0
sqlalchemy==2.0.52
```

---

### 2. backend\.env

```cmd
notepad .env
```

Paste this:
```
DB_NAME=ipo_tracker
CORS_ORIGINS=http://localhost:3000,https://demat-dashboard-1.preview.emergentagent.com
```

---

### 3. frontend\package.json

```cmd
cd ..\frontend
notepad package.json
```

**This file is TOO LARGE to paste here. You need to get it from Emergent.**

---

## Easier Alternative: Use GitHub

Instead of manually creating 50+ files, I recommend using Emergent's GitHub feature:

1. In Emergent chat, look for **"Push to GitHub"** button
2. Click it
3. Copy the GitHub URL it gives you
4. On your Windows PC:

```cmd
cd C:\Users\Administrator\Desktop
git clone YOUR_GITHUB_URL
cd ipo-tracker
```

---

## Can You Find GitHub Option?

**Please check your Emergent interface for:**
- "Push to GitHub" button
- "Save to GitHub" button
- "Connect GitHub" option
- "Export" or "Download" button

**If you find ANY of these, please tell me which one you see, and I'll guide you through the easiest path!**

---

## Alternative: I'll Create a Compressed Bundle

If you can't find GitHub options, I can:
1. Create a single downloadable file with all the code
2. You download it
3. Extract and use

Would you prefer this approach?
