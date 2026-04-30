🔐 Secure Document Vault

A full-stack secure document management system built with FastAPI (backend) and React + TypeScript (frontend).
Ensures encrypted storage, JWT authentication, and OTP-based secure downloads.

🚀 Features
🔐 JWT Authentication + bcrypt password hashing
📁 Secure file upload & management
🔒 AES encryption (Fernet)
🔑 OTP-based protected downloads
☁️ MongoDB Atlas database
⚡ Modern UI with React + Tailwind
🛠️ Tech Stack

Backend: FastAPI, MongoDB, JWT, bcrypt
Frontend: React, TypeScript, Tailwind CSS

📁 Project Structure
backend/ # API + Database + Security
frontend/ # UI (React App)
⚡ Getting Started

1. Backend
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app
2. Frontend
   cd frontend
   npm install
   npm run dev
   🔑 Environment Variables

Create backend/.env:

MONGODB_URI=your_mongodb_uri
JWT_SECRET_KEY=your_secret
FERNET_KEY=your_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_gmail_address@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_gmail_address@gmail.com

Important: if you use Gmail, generate a Google App Password and use that value for `SMTP_PASSWORD`. Regular Gmail passwords will not work for SMTP.
📡 API Overview
Auth: Register, Login, Profile
Documents: Upload, List, Delete
Download: OTP Request + Verify
🔐 Security Highlights
Encrypted file storage
OTP-based access control
Secure authentication with JWT
📌 Status

✅ Backend complete
✅ Frontend complete
🚀 Ready for deployment

👨‍💻 Author

Tushar Patel
