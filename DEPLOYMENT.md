# AWS EC2 Deployment Guide

Complete guide for deploying Instagram DM Automation on AWS EC2 Ubuntu 24.04 instance.

---

## Prerequisites

- AWS EC2 t3.micro instance running Ubuntu 24.04
- SSH key pair (.pem file) for EC2 access
- Instagram account credentials
- GitHub/GitLab account (for code deployment)

---

## Part 1: Push Code to Git Repository

### 1.1 Create GitHub Repository

1. Go to https://github.com/new
2. Create a new **private** repository (name: `instagram-automation`)
3. Do NOT initialize with README (we already have files)
4. Copy the repository URL (e.g., `https://github.com/yourusername/instagram-automation.git`)

### 1.2 Push Code from Local Machine

Run these commands in your project directory:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment setup for AWS EC2"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/yourusername/instagram-automation.git

# Push to GitHub
git push -u origin main
```

**Note:** If you get authentication errors, you may need to:
- Use a Personal Access Token instead of password
- Or use SSH keys for GitHub authentication

---

## Part 2: EC2 Instance Setup

### 2.1 Connect to EC2 Instance

Replace `<YOUR_KEY.pem>` and `<YOUR_EC2_IP>` with your actual values:

```bash
ssh -i <YOUR_KEY.pem> ubuntu@<YOUR_EC2_IP>
```

**Example:**
```bash
ssh -i ~/Downloads/my-ec2-key.pem ubuntu@54.123.45.67
```

### 2.2 Clone Repository on EC2

Once connected to EC2, run:

```bash
cd ~
git clone https://github.com/yourusername/instagram-automation.git
cd instagram-automation
```

If repository is private, you'll need to authenticate:
- Enter GitHub username and Personal Access Token when prompted
- Or set up SSH keys on your EC2 instance

### 2.3 Run Automated Setup

This script installs all dependencies (Chrome, Python packages, etc.):

```bash
bash deploy/setup_ubuntu.sh
```

This will take 5-10 minutes. It installs:
- Python 3 and pip
- Google Chrome
- System dependencies
- Python packages
- Creates virtual environment

### 2.4 Configure Environment Variables

Create your `.env` file with Instagram credentials:

```bash
nano .env
```

Add the following (replace with your actual credentials):

```env
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

Save and exit:
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

### 2.5 Update Target Profiles

Edit the CSV file with your target Instagram usernames:

```bash
nano InstagramProfiles.csv
```

Add usernames (one per line):
```csv
username
driveitautogroup
retro_rides4u
luxurycarsmiami
```

---

## Part 3: Testing

### 3.1 Manual Test Run

Before setting up automatic operation, test manually:

```bash
source venv/bin/activate
python main.py
```

**What to expect:**
- Browser will run in headless mode (invisible)
- You'll see logs showing progress
- Press `Ctrl + C` to stop

**Common issues:**
- If login fails, check your .env credentials
- If Chrome crashes, ensure you have enough RAM (t3.micro has 1GB)

### 3.2 Check Logs

Look for any errors in the output. Successful run should show:
- Login successful
- Processing profiles
- Messages sent

---

## Part 4: 24/7 Automatic Operation

### 4.1 Install Systemd Service

Copy the service file to systemd:

```bash
sudo cp deploy/instagram-automation.service /etc/systemd/system/
```

**Important:** Edit the service file if your username is not "ubuntu" or path is different:

```bash
sudo nano /etc/systemd/system/instagram-automation.service
```

Update these lines if needed:
- `User=ubuntu` (change if different user)
- `WorkingDirectory=/home/ubuntu/instagram-automation` (change if different path)

### 4.2 Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable instagram-automation

# Start the service now
sudo systemctl start instagram-automation
```

### 4.3 Check Service Status

```bash
sudo systemctl status instagram-automation
```

You should see:
- `Active: active (running)` in green

---

## Part 5: Monitoring & Maintenance

### 5.1 View Live Logs

```bash
# Follow logs in real-time
sudo journalctl -u instagram-automation -f

# View last 100 lines
sudo journalctl -u instagram-automation -n 100

# View logs from today
sudo journalctl -u instagram-automation --since today
```

Press `Ctrl + C` to stop following logs.

### 5.2 Control Service

```bash
# Stop the service
sudo systemctl stop instagram-automation

# Restart the service
sudo systemctl restart instagram-automation

# Disable auto-start on boot
sudo systemctl disable instagram-automation
```

### 5.3 Update Code

When you make changes to your code locally:

```bash
# On your local machine, push changes
git add .
git commit -m "Update message template"
git push

# On EC2 instance, pull changes
cd ~/instagram-automation
git pull
sudo systemctl restart instagram-automation
```

### 5.4 Download Results

From your **local machine**, download the CSV reports:

```bash
# Download all CSV files
scp -i <YOUR_KEY.pem> ubuntu@<YOUR_EC2_IP>:~/instagram-automation/*.csv ./

# Download specific report
scp -i <YOUR_KEY.pem> ubuntu@<YOUR_EC2_IP>:~/instagram-automation/successful_sends_*.csv ./
```

**Example:**
```bash
scp -i ~/Downloads/my-ec2-key.pem ubuntu@54.123.45.67:~/instagram-automation/*.csv ./downloads/
```

---

## Part 6: Troubleshooting

### Service Won't Start

```bash
# Check detailed error logs
sudo journalctl -u instagram-automation -n 50 --no-pager

# Check if virtual environment exists
ls ~/instagram-automation/venv

# Reinstall if needed
cd ~/instagram-automation
bash deploy/setup_ubuntu.sh
```

### Chrome Crashes (Out of Memory)

T3.micro has limited RAM. Solutions:

1. **Add swap space:**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

2. **Reduce concurrent operations:**
Edit `config.py` to lower limits:
```python
MESSAGES_PER_SESSION = 5  # Reduce from 10
```

### Login Keeps Failing

1. Check credentials:
```bash
cat .env
```

2. Instagram may be suspicious of new login location:
   - Try logging in manually from a browser first
   - Instagram may send verification code to your email/phone
   - You may need to verify it's you

3. Consider using cookies from manual login (advanced)

### High CPU Usage

This is normal during operation. Chrome uses significant CPU for browser automation.

---

## Part 7: Security Best Practices

### 7.1 Secure Your .env File

```bash
# Set restrictive permissions
chmod 600 .env

# Verify only you can read it
ls -la .env
```

### 7.2 Enable EC2 Firewall

In AWS Console:
1. Go to EC2 → Security Groups
2. Only allow SSH (port 22) from your IP
3. No need to open other ports

### 7.3 Regular Updates

```bash
# Update system packages monthly
sudo apt-get update && sudo apt-get upgrade -y
```

---

## Part 8: Performance Estimates

### With T3.micro Instance (1 GB RAM, 2 vCPU)

**Conservative Settings (recommended):**
- Messages per hour: ~5-8
- Messages per day: ~50-80
- Cost: ~$8/month for EC2
- Additional: Bandwidth (minimal)

**Aggressive Settings (higher risk):**
- Messages per hour: ~15-20
- Messages per day: ~150-200
- Higher chance of Instagram detection

### Recommended Configuration

Edit `config.py` on server:
```python
MIN_DELAY_BETWEEN_MESSAGES = 300  # 5 minutes
MAX_DELAY_BETWEEN_MESSAGES = 600  # 10 minutes
MESSAGES_PER_SESSION = 5
SESSION_BREAK_MIN = 1800  # 30 minutes
SESSION_BREAK_MAX = 3600  # 1 hour
DAILY_MESSAGE_LIMIT = 50
```

---

## Quick Reference Commands

```bash
# SSH to server
ssh -i <KEY> ubuntu@<IP>

# Check service
sudo systemctl status instagram-automation

# View logs
sudo journalctl -u instagram-automation -f

# Restart service
sudo systemctl restart instagram-automation

# Pull code updates
cd ~/instagram-automation && git pull && sudo systemctl restart instagram-automation

# Download results
scp -i <KEY> ubuntu@<IP>:~/instagram-automation/*.csv ./
```

---

## Support

If you encounter issues:
1. Check logs: `sudo journalctl -u instagram-automation -n 100`
2. Test manual run: `source venv/bin/activate && python main.py`
3. Verify .env credentials: `cat .env`
4. Check Chrome installation: `google-chrome --version`

---

## Cost Estimation

**Monthly AWS costs:**
- EC2 t3.micro: ~$8
- EBS Storage (8 GB): ~$1
- Data transfer: ~$1
- **Total: ~$10/month**

**Additional costs (optional):**
- Residential proxy: $5-20/month (recommended for higher volume)
- Elastic IP: $3.60/month if stopped frequently

---

## Next Steps After Deployment

1. Monitor for first 24 hours to ensure stability
2. Check Instagram account for any warnings
3. Adjust delays in `config.py` based on results
4. Set up CloudWatch alarms (optional)
5. Consider adding proxy for higher limits

