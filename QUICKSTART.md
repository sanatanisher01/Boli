# 🚀 BoliBazaar Quick Start Guide

## 1. Setup (One-time only)

### Option A: Automatic Setup (Windows)
```bash
setup.bat
```

### Option B: Manual Setup
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python setup.py
```

## 2. Start the Server

### Option A: Quick Start (Windows)
```bash
run.bat
```

### Option B: Manual Start
```bash
python manage.py runserver
```

## 3. Open in Browser
Visit: http://127.0.0.1:8000

## 4. Login Credentials

### Admin Account (Full Access)
- **Username**: admin
- **Password**: admin123
- **Features**: Add/edit products, view reports, manage auctions

### Demo User Account
- **Username**: demo
- **Password**: demo123
- **Features**: Browse auctions, place bids, voice commands

## 5. Test Voice Features

1. Go to any product detail page
2. Click the microphone button 🎤
3. Try these commands:
   - "What is the current bid?"
   - "Place a bid of 6000 rupees"

## 6. Admin Features

1. Login as admin
2. Click "Admin" in navigation
3. Add new products
4. Generate reports (PDF/CSV)
5. View all bids and manage auctions

## 🎯 Key Features to Test

- ✅ User registration and login
- ✅ Browse auction products
- ✅ Real-time countdown timers
- ✅ Manual bidding
- ✅ Voice bidding commands
- ✅ Bid history and leaderboards
- ✅ Admin product management
- ✅ Report generation
- ✅ Dark/light theme toggle
- ✅ Responsive mobile design

## 🔧 Troubleshooting

**Voice not working?**
- Use Chrome or Edge browser
- Allow microphone permissions
- Ensure you're on localhost or HTTPS

**Server won't start?**
- Check if port 8000 is free
- Run: `python manage.py check`
- Reinstall dependencies if needed

**Database issues?**
- Delete `db.sqlite3` file
- Run setup again

---

**Happy Bidding! 🎉**