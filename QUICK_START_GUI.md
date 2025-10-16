# Quick Start Guide - GUI Version

## Launch the GUI

**Windows:**
- Double-click `run_gui.bat`
- Or run: `python gui.py`

**Mac/Linux:**
- Run: `./run_gui.sh`
- Or run: `python3 gui.py`

## Using the Interface

### 1. Input Tab

Choose your input method:

**Option A: Load from CSV File**
- Select "Load from CSV File"
- Browse to your CSV file (default: InstagramProfiles.csv)
- CSV format: One column named "username" with usernames (one per line)

**Option B: Enter Usernames Directly**
- Select "Enter Usernames Directly"
- Paste or type usernames in the text box (one per line)
- Example:
  ```
  cristiano
  leomessi
  selenagomez
  ```

### 2. Settings Tab

**Instagram Credentials:**
- Enter your Instagram username
- Enter your Instagram password
- These will be stored in the .env file

**Message Settings:**
- Customize the message to send
- Default: "Hello World"

**Timing Information:**
- View current delay settings
- Messages per session
- Daily limits
- Edit `config.py` to change these values

### 3. Advanced Tab

**Browser Settings:**
- ☑ Run browser in headless mode (background)
- ☑ Save session cookies (faster subsequent logins)

**Safety Features:**
- ☑ Check for account blocks/restrictions
- ☑ Enable random human-like actions

**Actions:**
- **View Report**: Open the message report CSV
- **Reset Progress**: Clear processed profiles history
- **Open Log File**: View detailed logs

### 4. Start Automation

1. Click the **"▶ Start Automation"** button
2. Confirm the disclaimer
3. Watch real-time progress in the log window
4. Monitor statistics: Processed | Success | Failed
5. Click **"■ Stop"** to stop at any time

## Features

✅ **Real-time Log Output** - See what's happening as it happens
✅ **Progress Bar** - Visual indication of automation progress
✅ **Statistics Counter** - Track success and failure rates
✅ **Multiple Input Methods** - CSV file or direct paste
✅ **Easy Configuration** - All settings in one interface
✅ **One-Click Actions** - View reports, reset progress, open logs

## Tips

- Start with a small batch (2-3 profiles) to test
- Make sure Chrome browser is installed
- The browser window will open automatically
- Keep the GUI window open while automation runs
- Check the log output for any errors or warnings

## Troubleshooting

**GUI won't start:**
- Make sure Python is installed
- Run: `pip install -r requirements.txt`

**Browser won't open:**
- Check that Chrome browser is installed
- Try updating Chrome to the latest version

**Login fails:**
- Verify your Instagram credentials
- Instagram may require additional verification
- Try logging in manually first

**No profiles loading:**
- Check CSV file format (must have "username" column)
- Verify file path is correct
- Make sure usernames don't have @ symbols

## Safety Reminders

⚠️ **Use Responsibly:**
- This tool is for educational purposes
- Don't spam or harass users
- Respect Instagram's Terms of Service
- Use reasonable delays and limits
- Monitor your account for restrictions

## Need Help?

- Check the main `README.md` for detailed documentation
- Review `instagram_automation.log` for error details
- Make sure all dependencies are installed: `pip install -r requirements.txt`

