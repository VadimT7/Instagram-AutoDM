# 🚀 Build Desktop Application - Quick Instructions

## Option 1: One-Click Build (Recommended)

### Just double-click: `QUICK_BUILD.bat`

This will automatically:
1. ✅ Build the executable
2. ✅ Copy necessary files (.env, CSV)
3. ✅ Create desktop shortcut
4. ✅ Launch the application

**That's it!** Your app will be ready in 2-5 minutes.

---

## Option 2: Step-by-Step Build

### Step 1: Build Executable
```bash
# Double-click:
build_exe.bat
```
Wait 2-5 minutes for build to complete.

### Step 2: Setup Files
```bash
# Manually copy these files to the dist folder:
- .env (your Instagram credentials)
- InstagramProfiles.csv (optional, if using CSV import)
```

### Step 3: Create Shortcut
```bash
# Double-click:
create_shortcut.bat
```

### Step 4: Launch
- Double-click the desktop shortcut: "Instagram DM Automation"
- Or run from: `dist\Instagram DM Automation.exe`

---

## ⚠️ Important Notes

### Before Building
- Make sure your `.env` file exists with Instagram credentials
- Chrome browser must be installed on your system

### After Building
1. **The executable is in**: `dist\Instagram DM Automation.exe`
2. **Desktop shortcut created**: `Instagram DM Automation.lnk`
3. **File size**: ~150-200 MB (includes Python + dependencies)

### First Launch
1. Open Settings (⚙️) tab
2. Verify Instagram credentials
3. Save settings
4. Start using the app!

---

## 🔧 Troubleshooting

### Build fails?
- Install Visual C++ Redistributable
- Update Python to latest version
- Run as Administrator

### Executable won't start?
- Check if .env file is in dist folder
- Ensure Chrome browser is installed
- Try building with `console=True` for debug info

### ChromeDriver issues?
- Update Chrome to latest version
- Restart computer
- Rebuild the executable

---

## 📦 File Overview

**Build Scripts:**
- `QUICK_BUILD.bat` - One-click build + setup
- `build_exe.bat` - Build executable only
- `create_shortcut.bat` - Create desktop shortcut

**Configuration:**
- `instagram_automation.spec` - PyInstaller configuration
- `.env` - Your credentials (copy to dist/)

**Generated:**
- `dist/` - Executable and runtime files
- `build/` - Temporary build files (auto-cleaned)

---

## ✨ Next Steps

After building:
1. ✅ Launch from desktop shortcut
2. ✅ Configure Settings
3. ✅ Import profiles in Flow Manager
4. ✅ Start automation!

See `DESKTOP_APP_GUIDE.md` for detailed usage instructions.

