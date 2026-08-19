#!/bin/bash
# Windows Installer Build Script (for Mac/Linux)
# Cross-compile Windows installer from Mac or Linux

echo "============================================================"
echo "IPO Tracker - Windows Installer Build Script"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found"
    echo "Please run this script from the /frontend directory"
    exit 1
fi

# Step 1: Clean previous builds
echo "Step 1: Cleaning previous builds..."
rm -rf dist build
echo "Done!"
echo ""

# Step 2: Install dependencies (if needed)
echo "Step 2: Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    yarn install
else
    echo "Dependencies already installed"
fi
echo ""

# Step 3: Build React application
echo "Step 3: Building React application..."
echo "This may take 2-5 minutes..."
yarn build
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: React build failed"
    exit 1
fi
echo "Done!"
echo ""

# Step 4: Create Windows installer
echo "Step 4: Creating Windows installer..."
echo "This may take 5-15 minutes..."
echo ""
echo "Building:"
echo "  - IPO Tracker-Setup-1.0.0.exe (NSIS Installer)"
echo "  - IPO Tracker-Portable-1.0.0.exe (Portable)"
echo ""

# Install wine if on Mac/Linux (needed for NSIS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Note: Building Windows installer on Mac requires Wine"
    echo "Installing Wine via Homebrew (if not present)..."
    if ! command -v wine &> /dev/null; then
        brew install --cask wine-stable
    fi
fi

yarn dist
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Installer build failed"
    exit 1
fi
echo ""

# Step 5: Show results
echo "============================================================"
echo "BUILD COMPLETE!"
echo "============================================================"
echo ""
echo "Your installers are ready in the dist/ folder:"
echo ""
ls -lh dist/*.exe
echo ""
echo "============================================================"
echo "NEXT STEPS:"
echo "============================================================"
echo "1. Test IPO Tracker-Setup-1.0.0.exe on a clean Windows PC"
echo "2. Verify all features work correctly"
echo "3. Distribute to users!"
echo ""
echo "Need help? Check WINDOWS_INSTALLER_GUIDE.md"
echo "============================================================"
