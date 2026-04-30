# 🔐 Secure Document Vault

A full-stack secure document management system built with **FastAPI (backend)** and **React + TypeScript (frontend)**.
It ensures encrypted storage, JWT-based authentication, and OTP-protected document downloads.

---

## 🚀 Features

* 🔐 JWT authentication with bcrypt password hashing
* 📁 Secure file upload and management
* 🔒 AES encryption using Fernet
* 🔑 OTP-based protected downloads
* ☁️ MongoDB Atlas integration
* ⚡ Modern UI with React and Tailwind CSS

---

## 🛠️ Tech Stack

### Backend

* FastAPI
* MongoDB
* JWT Authentication
* bcrypt

### Frontend

* React
* TypeScript
* Tailwind CSS

---

## 📁 Project Structure

```bash
secure-document-vault/
│
├── backend/        # API, database, security logic
├── frontend/       # React frontend application
└── README.md
```

---

## ⚙️ Getting Started

### 🔹 Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

### 🔹 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Environment Variables

Create a `.env` file inside `/backend`:

```env
MONGODB_URI=your_mongodb_uri
JWT_SECRET_KEY=your_secret
FERNET_KEY=your_key
```

---

## 📡 API Overview

### 🔐 Auth

* Register
* Login
* Profile

### 📁 Documents

* Upload
* List
* Delete

### 🔑 Download

* OTP Request
* OTP Verification

---

## 🔐 Security Highlights

* Encrypted file storage (Fernet AES)
* OTP-based access control
* Secure JWT authentication

---

## 📌 Status

* ✅ Backend complete
* ✅ Frontend complete
* 🚀 Ready for deployment

---

## 👨‍💻 Author

**Tushar Patel**
Backend Developer
