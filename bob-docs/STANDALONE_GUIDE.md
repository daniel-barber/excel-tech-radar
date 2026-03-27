# Excel Tech Radar - Standalone Application Guide

This guide is for users of the standalone Excel Tech Radar application (no Python installation required).

## 📥 Installation

### macOS

1. **Download** the DMG file from [GitHub Releases](https://github.com/yourusername/excel-tech-radar/releases/latest)
   - Look for `RadarStudio-X.X.X-macOS.dmg`

2. **Open** the downloaded DMG file

3. **Drag** "Radar Studio" to your Applications folder

4. **First Launch** (Important!):
   - **Do not** double-click the app yet
   - **Right-click** (or Control+click) on "Radar Studio" in Applications
   - Select **"Open"** from the menu
   - A dialog will appear - click **"Open"** again
   - This is only needed the first time

5. **Subsequent Launches**: Double-click the app normally

**Why the extra step?** macOS Gatekeeper shows a security warning because the app is not signed with an Apple Developer certificate ($99/year). The app is completely safe - this is just Apple's way of protecting users from unverified developers.

**Alternative method (Terminal):**
```bash
xattr -d com.apple.quarantine "/Applications/Radar Studio.app"
```

**System Requirements**: macOS 10.13 (High Sierra) or later

### Windows

1. **Download** the ZIP file from [GitHub Releases](https://github.com/yourusername/excel-tech-radar/releases/latest)
   - Look for `RadarStudio-X.X.X-Windows.zip`

2. **Extract** the ZIP file to a folder
   - Recommended: `C:\Program Files\RadarStudio`
   - Or: `C:\Users\YourName\Documents\RadarStudio`

3. **Run** `RadarStudio.exe`

4. **First Launch** - If Windows Defender shows a warning:
   - Click **"More info"**
   - Click **"Run anyway"**
   - This is normal for unsigned applications
   - The app is safe - Windows just doesn't recognize the publisher

5. **Optional**: Create a desktop shortcut for easy access
   - Right-click `RadarStudio.exe`
   - Select "Create shortcut"
   - Drag shortcut to Desktop

**System Requirements**: Windows 10 or later

## 🚀 Getting Started

### First Time Setup

1. **Launch the Application**
   - macOS: Open from Applications folder
   - Windows: Run ExcelTechRadar.exe

2. **Select Data Directory**
   - Click the "Browse" button
   - Choose a folder where your Excel files are stored
   - This location is saved for future launches

3. **Launch the Radar Server**
   - Click "Launch Radar"
   - Wait for the status to show "Server running"
   - Your browser will open automatically to http://localhost:5050

4. **Start Using**
   - Create a new project or open an existing Excel file
   - Add entries and visualize your radar

### Daily Usage

Once configured, using the app is simple:

1. **Launch** the application
2. **Click** "Launch Radar" (directory is remembered)
3. **Work** in your browser at http://localhost:5050
4. **Stop** the server when done (click "Stop Server")
5. **Quit** the application

## 📁 Data Directory

### What is the Data Directory?

The data directory is where Excel Tech Radar stores:
- Your Excel files (one per project)
- Automatic backups
- Configuration files
- Logs

### Choosing a Location

**Recommended locations:**

**macOS:**
- `~/Documents/TechRadar` - Easy to find and backup
- `~/Desktop/TechRadar` - Quick access
- Any iCloud/Dropbox folder - Automatic cloud backup

**Windows:**
- `C:\Users\YourName\Documents\TechRadar` - Standard location
- `C:\Users\YourName\Desktop\TechRadar` - Quick access
- Any OneDrive/Dropbox folder - Automatic cloud backup

**Tips:**
- Choose a location you can easily find
- Use a cloud-synced folder for automatic backups
- Don't use system folders (Program Files, etc.)
- Keep it separate from other documents

### Changing the Directory

To change your data directory:
1. Click "Browse" in the launcher
2. Select a new folder
3. The new location is saved automatically
4. Your old data remains in the previous location (move manually if needed)

## 🌐 Using the Web Interface

### Accessing the Interface

Once the server is running:
- **Automatic**: Browser opens to http://localhost:5050
- **Manual**: Open any browser and go to http://localhost:5050

### Creating Your First Project

1. Click **"New Project"**
2. Enter a project name (e.g., "Q1 Initiatives")
3. Click **"Create"**
4. Start adding entries

### Adding Entries

**Option 1: Web Interface**
1. Click **"New Entry"**
2. Fill in the form:
   - Name (required)
   - Ring/Horizon (required)
   - Category (optional)
   - Deal Size (optional)
   - Propensity to Win (optional)
   - Description (optional)
3. Click **"Save"**

**Option 2: Excel Directly**
1. Click **"Edit Data"** to open Excel
2. Add rows with your data
3. Save the Excel file
4. Refresh the browser to see changes

### Viewing the Radar

- **Zoom**: Scroll wheel or pinch gesture
- **Pan**: Click and drag
- **Filter**: Use the filter panel on the right
- **Details**: Click any dot to see full information
- **Export**: Click "Export PNG" for presentations

## 🔧 Troubleshooting

### Application Won't Launch

**macOS:**
- **"App is damaged"**: Run `xattr -cr "/Applications/Excel Tech Radar.app"` in Terminal
- **Security warning**: Right-click app > Open (don't double-click)
- **Crashes immediately**: Check Console.app for error messages

**Windows:**
- **SmartScreen warning**: Click "More info" then "Run anyway"
- **Antivirus blocking**: Add exception for ExcelTechRadar.exe
- **Missing DLL**: Install Visual C++ Redistributable

### Server Won't Start

**Check Port Availability:**
- Another application might be using port 5050
- Close other applications and try again
- Or change the port in config.yml

**Check Directory Permissions:**
- Ensure you have write access to the data directory
- Try selecting a different directory

**Check Logs:**
- Look in the data directory for `logs/` folder
- Check `radar.log` for error messages

### Browser Doesn't Open

**Manual Access:**
1. Open any browser
2. Go to http://localhost:5050
3. Bookmark for easy access

**Check Firewall:**
- Ensure firewall allows localhost connections
- Add exception if needed

### Excel File Won't Load

**Check File Format:**
- Must be .xlsx format (not .xls)
- Must have required columns: name, ring
- Check for special characters in column names

**Check File Location:**
- File must be in the selected data directory
- File name should not have special characters

### Performance Issues

**Large Files:**
- Files with 1000+ entries may be slow
- Consider splitting into multiple projects
- Close other applications to free memory

**Slow Startup:**
- First launch extracts files (normal)
- Subsequent launches should be faster
- Check antivirus isn't scanning the app

## 💡 Tips & Best Practices

### Organization

- **One Project Per Team/Initiative**: Keep projects focused
- **Consistent Naming**: Use clear, descriptive project names
- **Regular Backups**: Backups are automatic, but export important projects
- **Cloud Sync**: Store data directory in Dropbox/OneDrive for safety

### Data Management

- **Start Simple**: Begin with just name and ring
- **Add Complexity Gradually**: Add categories, deal sizes as needed
- **Use Templates**: Create a template project to copy from
- **Document Conventions**: Keep a README in your data directory

### Collaboration

- **Shared Folder**: Use network drive or cloud folder for team access
- **Version Control**: Export projects before major changes
- **Communication**: Share PNG exports in presentations
- **Training**: Share this guide with team members

### Security

- **Local Only**: Server only accessible from your computer
- **No Internet Required**: Works completely offline
- **Data Privacy**: All data stays on your computer
- **Backups**: Keep backups of important projects

## 🆘 Getting Help

### Self-Help Resources

1. **Check Logs**: Look in `data/logs/radar.log`
2. **Review Documentation**: See README.md in the app folder
3. **Try Clean Start**: Select a new empty directory
4. **Restart Application**: Quit and relaunch

### Reporting Issues

If you encounter a bug:

1. **Gather Information**:
   - What were you doing when the error occurred?
   - What error message did you see?
   - Check the log file for details

2. **Report on GitHub**:
   - Go to [GitHub Issues](https://github.com/yourusername/excel-tech-radar/issues)
   - Click "New Issue"
   - Provide detailed description
   - Attach log file if possible

3. **Include**:
   - Operating system and version
   - Application version
   - Steps to reproduce
   - Expected vs actual behavior

## 📋 Keyboard Shortcuts

### In Browser

- **Ctrl/Cmd + F**: Search entries
- **Ctrl/Cmd + R**: Refresh radar
- **Ctrl/Cmd + P**: Export PNG
- **Esc**: Close detail panel

### In Launcher

- **Ctrl/Cmd + Q**: Quit application
- **Ctrl/Cmd + L**: Launch/Stop server

## 🔄 Updating

### Checking for Updates

1. Visit [GitHub Releases](https://github.com/yourusername/excel-tech-radar/releases)
2. Check if a newer version is available
3. Download the latest version

### Installing Updates

**macOS:**
1. Quit the current application
2. Download new DMG
3. Replace app in Applications folder
4. Launch new version

**Windows:**
1. Quit the current application
2. Download new ZIP
3. Extract to same location (overwrite)
4. Launch new version

**Your data is safe**: Updates don't affect your data directory

## 📊 Example Workflow

### Weekly Planning Session

1. **Monday Morning**:
   - Launch Excel Tech Radar
   - Open "Q1 Initiatives" project
   - Review current status

2. **Add New Items**:
   - Click "New Entry"
   - Add new initiatives from planning meeting
   - Set deal sizes and propensity

3. **Update Existing**:
   - Click entries to edit
   - Move items between rings
   - Update descriptions

4. **Export for Presentation**:
   - Click "Export PNG"
   - Save to presentation folder
   - Share with team

5. **Backup**:
   - Automatic backup created on save
   - Optional: Export project as ZIP

## 🎓 Learning Resources

- **Video Tutorial**: [Coming soon]
- **Sample Data**: Included in templates folder
- **Full Documentation**: See README.md
- **API Reference**: See API.md (for advanced users)

## ❓ FAQ

**Q: Do I need Python installed?**
A: No! The standalone app includes everything.

**Q: Can I use this offline?**
A: Yes, completely offline. No internet required.

**Q: Where is my data stored?**
A: In the directory you selected at startup.

**Q: Can multiple people use the same data directory?**
A: Yes, but not simultaneously. Use network/cloud folder.

**Q: How do I backup my data?**
A: Automatic backups are created. Also export projects as ZIP.

**Q: Can I customize the appearance?**
A: Yes, edit config.yml in your data directory.

**Q: Is my data secure?**
A: Yes, everything stays on your computer. No cloud upload.

**Q: Can I run multiple instances?**
A: No, only one instance per computer (port conflict).

---

**Need more help?** Open an issue on [GitHub](https://github.com/yourusername/excel-tech-radar/issues)