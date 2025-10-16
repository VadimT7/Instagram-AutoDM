# Quick Start Guide - Flow Manager

## 🚀 Simple 3-Step Process

### Step 1: Import Your Profiles
1. Open app: `python gui_modern.py`
2. Go to **"🔄 Flow Manager"** tab
3. Click **"📁 Import CSV"** (or **"📁📁 Import Multiple"** for bulk)
4. Select your CSV file(s) with Instagram usernames
5. ✅ Profiles are now in database at **Step 0**

### Step 2: Select Target Step
In Flow Manager, use the dropdown to select:
- **Step 0**: Send initial outreach to new profiles
- **Step 1**: Send first follow-up (to profiles from Step 0, after 3 days)
- **Step 2**: Send final follow-up (to profiles from Step 1, after 5 days)
- **Step 3**: Send re-engagement (to profiles from Step 2, after 30+ days)

### Step 3: Start Automation
1. Go back to **"🏠 Dashboard"** tab
2. Click **"▶ Start Automation"**
3. Confirm the details shown
4. ✅ Automation runs using selected step!

---

## 📊 How Steps Work

```
Your CSV Import
      ↓
[Step 0: Not Contacted] ← 125 profiles waiting
      ↓
Click "Start" (with Step 0 selected)
      ↓
Sends "Initial Outreach" message
      ↓
[Step 1: Initial Outreach] ← Profiles move here after first message
      ↓
Wait 3 days (automatic)
      ↓
Click "Start" (with Step 1 selected)
      ↓
Sends "First Follow-up" message
      ↓
[Step 2: First Follow-up]
      ↓
...and so on
```

---

## 💡 Key Points

✅ **Import once, use forever** - No need for CSV files after import  
✅ **Never sends duplicates** - System tracks who got what  
✅ **Automatic waiting periods** - Respects cooldowns between steps  
✅ **One entry point** - Always use Dashboard "Start Automation"  
✅ **Step selection in Flow Manager** - Choose which step to target  

---

## 🎯 Example Workflow

**Monday**: Import 500 car rental companies → Select Step 0 → Start Automation  
**Result**: 500 profiles get Step 1 "Initial Outreach" message, move to Step 1

**Thursday** (3 days later): Select Step 1 → Start Automation  
**Result**: Eligible profiles from Step 1 get Step 2 "First Follow-up" message

**Next Tuesday** (5 more days): Select Step 2 → Start Automation  
**Result**: Eligible profiles from Step 2 get Step 3 "Final Follow-up" message

---

## ❓ Common Questions

**Q: I imported profiles, where are they?**  
A: Check **History** tab - they're at Step 0 (Not Contacted)

**Q: Why does Start Automation say "0 eligible"?**  
A: Go to Flow Manager and select the step that has profiles (check Statistics)

**Q: Can I edit the message templates?**  
A: Yes! In Flow Manager → Select step → Edit message → Save Template

**Q: What if I have multiple CSV files?**  
A: Use "Import Multiple" - all profiles go into one database

---

**That's it! Import → Select Step → Start Automation** 🎉

