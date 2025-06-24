# 🏆 BoliBazaar - Online Auction Platform

**BoliBazaar** is a modern online auction platform featuring real-time bidding, user management, and complete auction administration.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Bidding** - Live auction participation with instant updates
- **User Authentication** - Secure registration and login system
- **Email Verification** - Account verification with unique ID generation
- **Profile Management** - Complete user profile customization

### 🚀 Advanced Features
- **Cloudinary Image Storage** - Scalable cloud-based media management
- **Email Notifications** - Bid confirmations, auction updates, win/loss alerts
- **Admin Dashboard** - Complete auction and user management
- **Mobile Responsive** - Works perfectly on all devices
- **PostgreSQL Database** - Reliable data persistence

## 🛠️ Tech Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Image Storage**: Cloudinary
- **Deployment**: Render
- **Frontend**: Bootstrap 5, Custom CSS/JS
- **Email**: SMTP Gmail Integration

## 🚀 Live Demo

- **Website**: [Your Render URL]
- **Demo Login**: demo/demo123

## 📱 Quick Start

### Test Accounts
- **Demo User**: username: `demo`, password: `demo123`

## 🏗️ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/BoliBazaar.git
cd BoliBazaar

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 🌐 Deployment

### Render Deployment
1. Connect GitHub repository
2. **Build Command**: `./build.sh`
3. **Start Command**: `gunicorn bolibazaar.wsgi:application`
4. Add environment variables (see below)

### Environment Variables
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://...
CLOUDINARY_CLOUD_NAME=ssssssss
CLOUDINARY_API_KEY=99999999999999
CLOUDINARY_API_SECRET=8888888888888
```

## 🏆 Key Features

**BoliBazaar** is a complete auction platform with:

- ✅ **Real-time Bidding** - Live auction participation
- ✅ **User Management** - Complete registration and profile system
- ✅ **Production Ready** - Scalable, secure, and deployable
- ✅ **Admin Dashboard** - Complete auction management
- ✅ **Email System** - Automated notifications and verification

## 📞 Contact

- **Developer**: Sanatani Sher
- **Email**: sanatanisofindia@gmail.com
- **GitHub**: [@sanatanisher01](https://github.com/sanatanisher01)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🏆 Experience the future of online auctions! 🚀**
