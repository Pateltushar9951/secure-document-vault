# 🔐 Secure Document Vault

A **complete full-stack application** featuring a **FastAPI + MongoDB Atlas backend** and a **professional React + TypeScript frontend** for secure document management with end-to-end encryption and OTP-gated downloads.

---

## 📁 Project Structure

```
Secure Document Vault (Backend-Focused)/
│
├── backend/                          # FastAPI + MongoDB Backend
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── config.py                 # Settings (from .env)
│   │   ├── database.py               # MongoDB connection
│   │   ├── models/                   # MongoDB models
│   │   ├── routers/                  # API endpoints
│   │   ├── services/                 # Business logic
│   │   ├── schemas/                  # Pydantic schemas
│   │   └── utils/                    # Helpers
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Configuration (MongoDB URI, secrets)
│   ├── .env.example                  # Template for .env
│   ├── Postman-Collection.json       # API testing
│   ├── README.md                     # Backend documentation
│   ├── MIGRATION_GUIDE.md            # Setup guide
│   └── storage/                      # Encrypted files (git-ignored)
│
├── frontend/                         # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   ├── context/                  # Auth state management
│   │   ├── pages/                    # Page components
│   │   ├── App.tsx                   # Main router
│   │   └── main.tsx                  # Entry point
│   ├── package.json                  # Node dependencies
│   ├── vite.config.ts                # Vite build config
│   ├── tsconfig.json                 # TypeScript config
│   ├── README.md                     # Frontend documentation
│   └── index.html                    # HTML entry point
│
├── .venv/                            # Python virtual environment (shared)
├── vault.db                          # SQLite file (can be deleted)
└── README.md                         # This file
```

---

## ✨ Features

✅ **Full-Stack**: FastAPI backend + React frontend
✅ **MongoDB Atlas**: Cloud database with mongoengine ORM
✅ **Security**: bcrypt passwords + JWT tokens + AES-128 encryption
✅ **OTP Gates**: One-time passwords for secure downloads
✅ **Professional UI**: React 18 + TypeScript + Tailwind CSS
✅ **API Testing**: Postman collection included
✅ **Type Safety**: TypeScript + Pydantic validation

---

## 🚀 Quick Start

### 1️⃣ Setup Backend

```powershell
# Navigate to backend folder
cd backend

# Activate virtual environment (from workspace root)
..\.venv\Scripts\Activate.ps1

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### 2️⃣ Configure MongoDB

1. Go to https://cloud.mongodb.com
2. Create a free cluster
3. Get your connection string
4. Open `backend/.env` and add:

   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
   MONGODB_DB_NAME=Secure_vault
   ```

   (Replace username, password, cluster with your MongoDB Atlas details)

5. Generate encryption & JWT secrets:
   ```powershell
   # From backend folder
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Add these to `backend/.env` as `FERNET_KEY` and `JWT_SECRET_KEY`

### 3️⃣ Start Backend

```powershell
# From backend folder
cd backend
uvicorn app.main:app
```

Visit **http://localhost:8000/docs** for interactive API docs.

### 4️⃣ Setup Frontend (in new terminal)

```powershell
# From workspace root
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit **http://localhost:5173** for the React UI.

---

## 📚 Documentation

| File                                                               | Purpose                           |
| ------------------------------------------------------------------ | --------------------------------- |
| [backend/README.md](backend/README.md)                             | Full backend guide + architecture |
| [backend/MIGRATION_GUIDE.md](backend/MIGRATION_GUIDE.md)           | MongoDB migration details         |
| [frontend/README.md](frontend/README.md)                           | Frontend guide + setup            |
| [backend/Postman-Collection.json](backend/Postman-Collection.json) | API testing collection            |

---

## 🧪 Testing

### Option A: Use Postman

1. Open Postman
2. Import `backend/Postman-Collection.json`
3. Test all 9 endpoints (Register → Login → Upload → List → Download → Delete)

### Option B: Use React UI

1. Open http://localhost:5173
2. Register new account
3. Login
4. Upload, list, and download documents

### Option C: Use Swagger UI

1. Visit http://localhost:8000/docs
2. Try endpoints directly

---

## 🔑 Environment Setup

**Backend .env template** (in `backend/.env`):

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/Secure_vault
MONGODB_DB_NAME=Secure_vault

# Encryption & Auth (generate with Python commands above)
FERNET_KEY=<your-fernet-key>
JWT_SECRET_KEY=<your-jwt-secret>

# App Settings
DEBUG=True
STORAGE_DIR=storage
MAX_FILE_SIZE_MB=10
ALLOWED_MIME_TYPES=application/pdf,image/png,image/jpeg
OTP_EXPIRE_MINUTES=5
OTP_LENGTH=6

# Email (optional - leave blank to disable)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=
```

---

## 🔐 Security Features

| Feature               | Implementation                                     |
| --------------------- | -------------------------------------------------- |
| **User Auth**         | bcrypt (rounds=12) + JWT (30-min expiry)           |
| **File Encryption**   | AES-128 via Fernet                                 |
| **Download Security** | OTP (6-digit, 5-min TTL, single-use)               |
| **MIME Validation**   | Magic-byte detection + size limits                 |
| **Database**          | MongoDB Atlas with TLS                             |
| **CORS**              | Enabled in DEBUG mode, restrictable for production |

---

## 🛠️ Tech Stack

**Backend**:

- FastAPI 0.111
- MongoDB Atlas + mongoengine
- Uvicorn (ASGI server)
- Pydantic (validation)
- PyJWT + bcrypt
- Fernet (encryption)

**Frontend**:

- React 18.2
- TypeScript 5
- Vite 5.0
- Tailwind CSS 3.3
- Axios (HTTP client)
- React Router 6

---

## 📖 Workflow

```
User Registration/Login
         ↓
   JWT Token (localStorage)
         ↓
    Document Upload
    ↓            ↓
  Encrypt    Store Metadata
    ↓            ↓
  Storage ← MongoDB
         ↓
   Request Download
    ↓
  Generate OTP
    ↓
  Send Email (or show in DEBUG)
    ↓
   User Submits OTP
    ↓
  Decrypt & Stream
```

---

## 🐛 Troubleshooting

**Backend won't start?**

- Check MongoDB URI in `backend/.env`
- Verify `.venv` is activated
- Check that `cryptography`, `mongoengine`, `fastapi` are installed: `pip list`

**Frontend won't connect to backend?**

- Backend must be running on http://localhost:8000
- Check CORS: `DEBUG=True` in backend `.env`
- Browser console shows exact error

**MongoDB connection fails?**

- Verify connection string format in MongoDB Atlas
- Add your IP to Atlas **Network Access**
- Check username and password spelling

**Port 8000 already in use?**

```powershell
# Use different port
uvicorn app.main:app --port 8001
```

---

## ⚡ Commands Cheat Sheet

```powershell
# Backend
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app

# Frontend
cd frontend
npm install
npm run dev
npm run build

# Testing
# Import backend/Postman-Collection.json into Postman
```

---

## 📊 API Endpoints

**Health**: `GET /health`

**Auth**:

- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login (returns JWT)
- `GET /api/v1/auth/me` - Get profile

**Documents**:

- `POST /api/v1/documents/upload` - Upload file
- `GET /api/v1/documents/` - List files
- `DELETE /api/v1/documents/{doc_id}` - Delete file
- `POST /api/v1/documents/download/request/{doc_id}` - Request OTP
- `POST /api/v1/documents/download/verify/{doc_id}` - Download with OTP

---

## 🎯 Interview Topics

This project demonstrates:

- **Full-stack development** (backend + frontend)
- **Secure authentication** (JWT + bcrypt)
- **Encryption** (AES-128 Fernet)
- **Database design** (MongoDB with mongoengine)
- **API design** (RESTful endpoints)
- **Modern frontend** (React hooks, Context API)
- **Cloud integration** (MongoDB Atlas)
- **Error handling** (Pydantic validation, try/except)

---

## 📝 License

Educational project. Use freely for learning.

---

## ✅ Status

- ✅ Backend: MongoDB Atlas configured
- ✅ Frontend: React UI ready
- ✅ API: 9 endpoints fully functional
- ✅ Testing: Postman collection included
- ⏳ Deployment: Ready for cloud hosting

**Next Steps**:

1. Populate MongoDB with user accounts
2. Test file encryption/decryption
3. Configure email for OTP delivery (optional)
4. Deploy to production (Azure, Heroku, etc.)

---

Built with ❤️ for secure document management
#   s e c u r e - d o c u m e n t - v a u l t  
 