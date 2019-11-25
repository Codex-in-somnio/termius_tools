const { app, BrowserWindow } = require('electron')

function createWindow() {
    let win = new BrowserWindow({
        width: 1000,
        height: 800,
        webPreferences: {
            nodeIntegration: true
        }
    })
    win.removeMenu()
    win.webContents.openDevTools({ mode: 'bottom' })
    win.loadFile('src/index.html')
}

app.on('ready', createWindow)
