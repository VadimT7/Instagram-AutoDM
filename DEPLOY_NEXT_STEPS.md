# AWS Deployment - Next Steps

## ✅ What's Been Done

All deployment files have been created and committed to git:
- ✅ `deploy/setup_ubuntu.sh` - Automated server setup
- ✅ `deploy/run_headless.sh` - Headless runner script
- ✅ `deploy/instagram-automation.service` - Systemd service for 24/7 operation
- ✅ `.gitignore` - Protects sensitive files
- ✅ `config.py` - Updated to headless mode by default
- ✅ `DEPLOYMENT.md` - Complete deployment guide
- ✅ Git repository initialized and files committed

---

## 📋 Your Next Steps

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a **PRIVATE** repository named `instagram-automation`
3. Do NOT initialize with README
4. Copy the repository URL

### Step 2: Push Code to GitHub

Run this command (replace with your repository URL):

```bash
git remote add origin https://github.com/YOUR_USERNAME/instagram-automation.git
git push -u origin main
```

If you need to use a Personal Access Token:
- Go to GitHub → Settings → Developer settings → Personal access tokens
- Generate new token with `repo` scope
- Use token as password when prompted

### Step 3: Deploy to AWS EC2

SSH into your EC2 instance:

```bash
ssh -i YOUR_KEY.pem ubuntu@YOUR_EC2_IP
```

Clone the repository:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/instagram-automation.git
cd instagram-automation
```

Run the automated setup:

```bash
bash deploy/setup_ubuntu.sh
```

### Step 4: Configure Credentials

Create `.env` file on the server:

```bash
nano .env
```

Add your credentials:
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

Save: `Ctrl + O`, `Enter`, `Ctrl + X`

### Step 5: Add Target Profiles

Edit the CSV file:

```bash
nano InstagramProfiles.csv
```

Add usernames (one per line):
```csv
username
target_user1
target_user2
```

### Step 6: Test Run

```bash
source venv/bin/activate
python main.py
```

Press `Ctrl + C` to stop when you verify it's working.

### Step 7: Set Up 24/7 Service

```bash
sudo cp deploy/instagram-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable instagram-automation
sudo systemctl start instagram-automation
```

### Step 8: Monitor

Check status:
```bash
sudo systemctl status instagram-automation
```

View logs:
```bash
sudo journalctl -u instagram-automation -f
```

---

## 📖 Full Documentation

See `DEPLOYMENT.md` for complete documentation including:
- Troubleshooting guide
- Performance estimates
- Monitoring commands
- Security best practices
- Cost estimates

---

## 🚀 Quick Commands Reference

```bash
# Check service status
sudo systemctl status instagram-automation

# View live logs
sudo journalctl -u instagram-automation -f

# Restart service
sudo systemctl restart instagram-automation

# Download results (from local machine)
scp -i YOUR_KEY.pem ubuntu@YOUR_EC2_IP:~/instagram-automation/*.csv ./
```

---

## ⚠️ Important Notes

1. **First login**: Instagram may require verification when logging in from EC2 for the first time
2. **Start slow**: Default settings send ~5-8 messages/hour (safe limits)
3. **Monitor closely**: Check logs for first 24 hours
4. **Cost**: EC2 t3.micro costs ~$10/month

---

## 🆘 Need Help?

If something goes wrong:
1. Check logs: `sudo journalctl -u instagram-automation -n 100`
2. Verify .env: `cat .env`
3. Test manually: `source venv/bin/activate && python main.py`
4. See troubleshooting section in `DEPLOYMENT.md`

