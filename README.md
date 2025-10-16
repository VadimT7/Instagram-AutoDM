# Instagram DM Automation System

An advanced, undetectable Instagram automation system for sending direct messages with human-like behavior patterns.

## ⚠️ IMPORTANT DISCLAIMER

**This tool is for educational purposes only.** Using automation on Instagram may violate their Terms of Service and could result in account restrictions or bans. Always:
- Ensure you have permission to contact users
- Comply with all applicable laws and platform policies
- Use at your own risk

## 🚀 Features

- **Modern Graphical User Interface**: Easy-to-use GUI with real-time progress monitoring
- **Flexible Input Options**:
  - Load usernames from CSV file
  - Paste usernames directly in the interface
- **Undetectable Browser Automation**: Uses undetected-chromedriver to bypass detection
- **Human-like Behavior**: Simulates real user interactions with:
  - Random delays and timing variations
  - Natural mouse movements with bezier curves
  - Realistic typing speed with occasional typos
  - Random scrolling and mouse movements
  - Session breaks and daily limits
- **Smart Processing**:
  - CSV file processing for bulk profiles
  - Progress tracking and resume capability
  - Automatic retry on failures
  - Session persistence with cookies
- **Safety Features**:
  - Daily message limits
  - Session-based messaging with breaks
  - Block/restriction detection
  - Comprehensive logging

## 📋 Requirements

- Python 3.8 or higher
- Google Chrome browser (latest version)
- ChromeDriver (automatically handled by undetected-chromedriver)
- Windows/Mac/Linux OS

## 🛠️ Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your credentials:**
   - Copy `env.example` to `.env`:
     ```bash
     copy env.example .env  # Windows
     cp env.example .env     # Mac/Linux
     ```
   - Edit `.env` file and add your Instagram credentials:
     ```
     INSTAGRAM_USERNAME=your_username
     INSTAGRAM_PASSWORD=your_password
     ```

4. **Prepare your CSV file:**
   - Edit `InstagramProfiles.csv`
   - Add Instagram usernames in the "username" column
   - Example format:
     ```csv
     username
     cristiano
     leomessi
     selenagomez
     ```
   - Note: The system will automatically construct full URLs from usernames
   - You can also use the old format with full URLs in a "link" column (backward compatible)

## 🎯 Usage

### Option 1: Graphical User Interface (GUI) - Recommended

1. **Run the GUI:**
   ```bash
   python gui.py
   ```
   Or double-click:
   - Windows: `run_gui.bat`
   - Mac/Linux: `run_gui.sh`

2. **Use the interface:**
   - **Input Tab**: Choose to load from CSV file OR paste usernames directly
   - **Settings Tab**: Enter Instagram credentials and customize message
   - **Advanced Tab**: Configure browser and safety settings
   - Click **"Start Automation"** to begin
   - Monitor progress in real-time with live log output

### Option 2: Command Line Interface (CLI)

1. **Run the automation:**
   ```bash
   python main.py
   ```

2. **Follow the prompts:**
   - The system will ask for confirmation before starting
   - If credentials are not in .env, it will prompt for them
   - Monitor the colored console output for progress

3. **Monitor progress:**
   - Check `instagram_automation.log` for detailed logs
   - View `message_report.csv` for sent message reports
   - Check `processed_profiles.json` to see processing history

## ⚙️ Configuration

Edit `config.py` to customize:

- **Message Settings:**
  - `DEFAULT_MESSAGE`: The message to send (default: "Hello World")
  - Message variations for more natural messaging

- **Timing Settings:**
  - `MIN_DELAY_BETWEEN_MESSAGES`: Minimum delay (default: 30 seconds)
  - `MAX_DELAY_BETWEEN_MESSAGES`: Maximum delay (default: 120 seconds)
  - `MESSAGES_PER_SESSION`: Messages before taking a break (default: 10)
  - `SESSION_BREAK_MIN/MAX`: Break duration between sessions

- **Limits:**
  - `DAILY_MESSAGE_LIMIT`: Maximum messages per day (default: 50)

- **Browser Settings:**
  - `HEADLESS_MODE`: Run browser in background (default: False)

## 📁 File Structure

```
Instagram DMer/
├── gui.py                     # Graphical user interface (NEW!)
├── main.py                    # Command-line automation script
├── instagram_automation.py    # Instagram interaction logic
├── browser_manager.py         # Browser setup with anti-detection
├── human_behavior.py          # Human-like behavior simulation
├── csv_processor.py           # CSV file handling
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── run_gui.bat                # GUI launcher for Windows
├── run_gui.sh                 # GUI launcher for Mac/Linux
├── run.bat                    # CLI launcher for Windows
├── run.sh                     # CLI launcher for Mac/Linux
├── InstagramProfiles.csv      # Input CSV file with usernames
├── .env                       # Your credentials (create from env.example)
├── processed_profiles.json    # Tracking processed profiles (auto-generated)
├── instagram_cookies.json     # Session cookies (auto-generated)
├── instagram_automation.log   # Detailed logs (auto-generated)
└── message_report.csv         # Report of sent messages (auto-generated)
```

## 🔒 Anti-Detection Features

The system implements multiple layers of anti-detection:

1. **Browser Fingerprinting Protection:**
   - Uses undetected-chromedriver
   - Randomized user agents
   - Modified browser properties
   - Disabled automation flags

2. **Human-like Interactions:**
   - Bezier curve mouse movements
   - Variable typing speeds with typos
   - Random delays with normal distribution
   - Random scrolling and mouse movements
   - Session-based activity patterns

3. **Smart Timing:**
   - Randomized delays between actions
   - Session breaks to mimic human behavior
   - Daily limits to avoid triggering rate limits
   - Longer occasional pauses

## 🐛 Troubleshooting

### Common Issues:

1. **"Chrome driver not found"**
   - The system uses undetected-chromedriver which handles this automatically
   - Ensure Chrome browser is installed and updated

2. **"Login failed"**
   - Check your credentials in the .env file
   - Instagram may require additional verification
   - Try logging in manually first to clear any security checks

3. **"Message button not found"**
   - The profile may be private
   - The user may have disabled messages
   - Instagram's UI may have changed

4. **"Daily limit reached"**
   - Wait until the next day for the counter to reset
   - Or modify `DAILY_MESSAGE_LIMIT` in config.py

### Reset Processing History:

To start fresh and reprocess all profiles:
1. Delete `processed_profiles.json`
2. Run the script again

## 🔄 Resuming After Interruption

The system automatically tracks processed profiles. If interrupted:
- Simply run `python main.py` again
- It will skip already processed profiles
- Continue from where it left off

## 📊 Reports

After running, check:
- `message_report.csv` - Detailed report of all messages sent
- `instagram_automation.log` - Full execution logs
- Console output - Real-time progress with color coding

## 🚨 Best Practices

1. **Start Small**: Test with a few profiles first
2. **Use Reasonable Delays**: Don't set delays too low
3. **Monitor Your Account**: Watch for any restrictions
4. **Respect Privacy**: Only message users appropriately
5. **Regular Breaks**: Let the system take session breaks
6. **Update Regularly**: Keep Chrome and dependencies updated

## 📝 Notes

- The system saves login cookies for faster subsequent runs
- Processed profiles are tracked to avoid duplicate messages
- All actions are logged for debugging purposes
- The browser window is visible by default (change HEADLESS_MODE for background operation)

## 🤝 Support

This is an educational project. For issues:
1. Check the troubleshooting section
2. Review the logs in `instagram_automation.log`
3. Ensure all dependencies are correctly installed
4. Verify your CSV file format is correct

## 📄 License

This project is provided as-is for educational purposes only. Use responsibly and at your own risk.
