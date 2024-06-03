const { app, BrowserWindow, globalShortcut, desktopCapturer } = require('electron');
const path = require('path');
const regedit = require('regedit');
// const robot = require('robotjs');
// const jimp = require('jimp');


// regedit.setExternalVBSLocation('resources/regedit/vbs'); // Required for Electron packaging

// function takeScreenshot() {
//   // Get a list of active windows
//   const windows = robot.getWindowList();

//   // Find the BlueStacks window
//   const blueStacksWindow = windows.find(window => window.name.includes('BlueStacks'));

//   if (blueStacksWindow) {
//     // Get the BlueStacks window dimensions
//     const { left, top, width, height } = blueStacksWindow.rect;

//     // Capture the screen region corresponding to the BlueStacks window
//     desktopCapturer.getSources({ types: ['screen'], thumbnailSize: { width, height } }).then(async sources => {
//       const source = sources.find(source => source.id === 'window:current:0');

//       if (source) {
//         const screenshot = await new Promise(resolve => {
//           source.thumbnail.toPNG((err, thumbnail) => {
//             if (!err) {
//               resolve(thumbnail);
//             }
//           });
//         });

//         // Save the screenshot to a temporary folder
//         const tempDir = app.getPath('temp');
//         const screenshotPath = path.join(tempDir, 'bluestacks_screenshot.png');

//         // Save the screenshot using jimp
//         const image = await jimp.read(screenshot);
//         image.crop(left, top, width, height);
//         image.write(screenshotPath);
//       }
//     });
//   }
// }


function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 1000,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    
  });
  // globalShortcut.register('Shift+P', takeScreenshot);
  mainWindow.loadURL('http://localhost:3000');
  mainWindow.webContents.openDevTools();
}
app.on('ready', () => {
  createWindow()
});
app.on('window-all-closed', () => {
  globalShortcut.unregister('Shift+P');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
