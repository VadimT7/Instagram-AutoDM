# 🖥️ Desktop Application Guide

## Quick Start - 3 Steps to Desktop App

### Step 1: Build the Executable
```bash
# Double-click this file:
build_exe.bat
```
This will:
- Install PyInstaller if needed
- Clean previous builds
- Create the executable in the `dist` folder
- Takes 2-5 minutes

### Step 2: Setup Environment
1. Copy your `.env` file to the `dist` folder
2. (Optional) Copy `InstagramProfiles.csv` to `dist` folder if using CSV import

### Step 3: Create Desktop Shortcut
```bash
# Double-click this file:
create_shortcut.bat
```
This creates a shortcut on your desktop!

---

## 🎯 How to Use

### Launch Application
- **Desktop**: Double-click "Instagram DM Automation" shortcut
- **Or**: Navigate to `dist` folder and run `Instagram DM Automation.exe`

### First Time Setup
1. Launch the app
2. Go to ⚙️ Settings
3. Enter your Instagram credentials
4. Save settings

### Import Profiles
1. Go to 🔄 Flow Manager
2. Click "Import Single CSV" or "Import Multiple CSVs"
3. Select your CSV files with usernames
4. Profiles imported into database

### Start Automation
1. Go to 🏠 Dashboard
2. Select step in Flow Manager (default: Step 0)
3. Click "▶ Start Automation"
4. Confirm the prompt
5. Watch it run!

---

## 📁 File Structure

```
Instagram DMer/
├── dist/                          # Executable folder (created after build)
│   ├── Instagram DM Automation.exe
│   ├── .env                       # YOUR CREDENTIALS (copy here)
│   ├── InstagramProfiles.csv      # (optional)
│   └── automation_history.db      # Created automatically
│
├── build_exe.bat                  # Build the executable
├── create_shortcut.bat            # Create desktop shortcut
└── instagram_automation.spec      # Build configuration
```

---

## ⚙️ Advanced Options

### Custom Icon
1. Get a `.ico` file for your icon
2. Save it as `icon.ico` in the project folder
3. Edit `instagram_automation.spec`:
   ```python
   icon='icon.ico',  # Add this line
   ```
4. Rebuild: `build_exe.bat`

### Show Console Window (for debugging)
Edit `instagram_automation.spec`:
```python
console=True,  # Change False to True
```
Then rebuild.

### Reduce File Size
The executable is large (~150-200MB) because it includes:
- Python runtime
- Selenium & ChromeDriver
- All dependencies

To reduce size:
1. Use UPX compression (already enabled)
2. Exclude unused modules in spec file

---

## 🔧 Troubleshooting

### "Application won't start"
- **Check**: .env file in dist folder?
- **Check**: All credentials correct?
- **Fix**: Run with console=True to see errors

### "ChromeDriver not found"
- **Fix**: Chrome browser must be installed
- **Fix**: Restart computer after Chrome install

### "Module not found" error
- **Fix**: Rebuild with `build_exe.bat`
- **Fix**: Check all imports in spec file

### "Shortcut not working"
- **Fix**: Ensure executable exists in dist folder
- **Fix**: Re-run `create_shortcut.bat`

### "Database locked" error
- **Fix**: Close all instances of the app
- **Fix**: Delete `automation_history.db-journal` file

---

## 🚀 Distribution

### Share with Others
To give the app to someone else:
1. Zip the entire `dist` folder
2. Include a README with:
   - How to create `.env` file
   - Instagram credentials setup
   - Basic usage instructions

### What to Include
```
Instagram-DM-Automation.zip
├── Instagram DM Automation.exe
├── README.txt (your instructions)
└── .env.example (template)
```

⚠️ **Never share your .env file with credentials!**

---

## 📊 Performance

### Startup Time
- **First Launch**: 10-15 seconds (database init)
- **Subsequent**: 5-10 seconds

### Memory Usage
- **Idle**: ~100-150 MB
- **Running**: ~300-500 MB (Chrome browser)

### Disk Space
- **Executable**: ~150-200 MB
- **Database**: Grows with usage (~1MB per 1000 profiles)

---

## 🎨 Customization

### Change App Name
Edit `instagram_automation.spec`:
```python
name='Your Custom Name',
```

### Window Title
Edit `gui_modern.py`:
```python
self.root.title("Your Custom Title")
```

### Theme Colors
Edit color constants in `gui_modern.py`:
```python
COLORS = {
    'primary': '#1a73e8',    # Change these
    'accent': '#0066ff',
    # ... etc
}
```

---

## 🔄 Updates

### Update the App
1. Pull latest code changes
2. Run `build_exe.bat` again
3. New executable overwrites old one
4. Desktop shortcut still works

### Preserve Settings
- `.env` file: Keep in dist folder
- Database: `automation_history.db` - Keep in dist folder
- Settings persist between updates!

---

## ✅ Complete Setup Checklist

- [ ] Built executable (`build_exe.bat`)
- [ ] Copied `.env` file to `dist` folder
- [ ] Created desktop shortcut (`create_shortcut.bat`)
- [ ] Tested launch from desktop
- [ ] Configured Instagram credentials in Settings
- [ ] Imported profiles via Flow Manager
- [ ] Ran first test automation
- [ ] Checked Accounts tab for results

**Ready to automate! 🎉**

