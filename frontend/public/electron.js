const { app, BrowserWindow, protocol } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');

// Fix for running as root (required in some environments)
if (process.platform === 'linux') {
  app.commandLine.appendSwitch('no-sandbox');
  app.commandLine.appendSwitch('disable-gpu');
}

let mainWindow;
let backendProcess;

// Start the Python backend
function startBackend() {
  const backendPath = isDev
    ? path.join(__dirname, '..', 'backend', 'server.py')
    : path.join(process.resourcesPath, 'backend', 'server.py');

  console.log('Starting backend from:', backendPath);

  backendProcess = spawn('python3', [backendPath], {
    env: {
      ...process.env,
      ELECTRON_MODE: 'true',
      DB_PATH: path.join(app.getPath('userData'), 'ipo_tracker.db')
    }
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    title: 'IPO Tracker - Profit & Loss Manager',
    autoHideMenuBar: true,
  });

  // Load the React app
  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', () => {
  // Register file protocol
  protocol.registerFileProtocol('file', (request, callback) => {
    const pathname = decodeURI(request.url.replace('file:///', ''));
    callback(pathname);
  });

  // Start backend server
  startBackend();

  // Give backend time to start, then create window
  setTimeout(createWindow, 2000);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Clean up backend process on quit
app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});

app.on('will-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
