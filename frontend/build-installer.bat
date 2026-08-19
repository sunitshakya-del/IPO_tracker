@echo off
REM Windows Installer Build Script
REM Run this on Windows PC to create the installer

echo ============================================================
echo IPO Tracker - Windows Installer Build Script
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: package.json not found
    echo Please run this script from the /frontend directory
    pause
    exit /b 1
)

REM Step 1: Clean previous builds
echo Step 1: Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo Done!
echo.

REM Step 2: Install dependencies (if needed)
echo Step 2: Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call yarn install
) else (
    echo Dependencies already installed
)
echo.

REM Step 3: Build React application
echo Step 3: Building React application...
echo This may take 2-5 minutes...
call yarn build
if errorlevel 1 (
    echo.
    echo Error: React build failed
    pause
    exit /b 1
)
echo Done!
echo.

REM Step 4: Create Windows installer
echo Step 4: Creating Windows installer...
echo This may take 5-15 minutes...
echo.
echo Building:
echo  - IPO Tracker-Setup-1.0.0.exe (NSIS Installer)
echo  - IPO Tracker-Portable-1.0.0.exe (Portable)
echo.
call yarn dist
if errorlevel 1 (
    echo.
    echo Error: Installer build failed
    pause
    exit /b 1
)
echo.

REM Step 5: Show results
echo ============================================================
echo BUILD COMPLETE!
echo ============================================================
echo.
echo Your installers are ready in the dist/ folder:
echo.
dir /b dist\*.exe
echo.
echo Installation files:
dir dist\*.exe
echo.
echo ============================================================
echo NEXT STEPS:
echo ============================================================
echo 1. Test IPO Tracker-Setup-1.0.0.exe on a clean Windows PC
echo 2. Verify all features work correctly
echo 3. Distribute to users!
echo.
echo Need help? Check WINDOWS_INSTALLER_GUIDE.md
echo ============================================================
echo.
pause
