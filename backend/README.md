# 🔐 Secure Document Vault

A **production-quality** Python / FastAPI backend + React frontend that acts as a secure personal locker for digital documents. Every file is **AES-encrypted at rest** with MongoDB Atlas storage and can only be downloaded after successful **OTP verification**.

---

## ✨ Features

| Feature             | Implementation                                |
| ------------------- | --------------------------------------------- |
| **Database**        | MongoDB Atlas (cloud-based, scalable)         |
| **User Auth**       | bcrypt passwords + JWT Bearer tokens          |
| **File Validation** | Magic-byte MIME sniffing + size limit         |
| **Encryption**      | AES-128-CBC via Fernet (symmetric)            |
| **OTP Security**    | 6-digit, 5-min TTL, single-use, bcrypt-hashed |
| **Email Delivery**  | SMTP with HTML template (console fallback)    |
| **Rate Limiting**   | slowapi middleware for DDoS protection        |
| **API Docs**        | Interactive Swagger UI at `/docs`             |
| **Professional UI** | React 18 + TypeScript + Tailwind CSS          |
| **API Testing**     | Postman collection included                   |

---

## 🗂️ Project Structure

```
Secure Document Vault (Backend-Focused)/
├── backend/                      # FastAPI + MongoDB backend
│   ├── app/
│   │   ├── main.py               # App factory, middleware, lifespan
│   │   ├── config.py             # Settings from .env
│   │   ├── database.py           # MongoDB connection (mongoengine)
│   │   ├── models/
│   │   │   ├── user.py           # User document model
│   │   │   └── document.py       # Document + OTP models
│   │   ├── schemas/
│   │   │   ├── user.py           # Pydantic schemas
│   │   │   └── document.py
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── auth.py           # /api/v1/auth/*
│   │   │   └── documents.py      # /api/v1/documents/*
│   │   ├── services/
│   │   │   ├── auth_service.py   # JWT + bcrypt
│   │   │   ├── encryption_service.py # AES encrypt/decrypt
│   │   │   ├── otp_service.py    # OTP logic
│   │   │   └── email_service.py  # SMTP sender
│   │   └── utils/
│   │       └── file_validator.py # MIME validation
│   ├── README.md
│   ├── MIGRATION_GUIDE.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── Postman-Collection.json
│   └── storage/                  # Encrypted files (git-ignored)
│
├── frontend/                     # React UI
│   ├── src/
│   │   ├── components/           # Reusable components
│   │   ├── context/              # React Context (Auth)
│   │   ├── pages/                # Login, Register, Dashboard
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
└── README.md                     # Workspace overview
```

---

## ⚡ Quick Start (Backend + Frontend)

### Step 1: Setup Backend

```powershell
# Navigate to project directory
cd backend

# Activate the existing workspace virtual environment
..\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Configure MongoDB Atlas

1. **Create MongoDB Cluster**:
   - Go to https://cloud.mongodb.com
   - Sign up or login
   - Create a free cluster (M0 tier)
   - Get your connection string

2. **Setup .env**:

   ```bash
   cp .env.example .env
   ```

3. **Edit .env** with your secrets:

   ```
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/secure_vault?retryWrites=true&w=majority
   MONGODB_DB_NAME=secure_vault

   # Generate these:
   FERNET_KEY=<run: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
   JWT_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
   ```

### Step 3: Start Backend Server

```powershell
# Without reload (recommended for Python 3.14)
uvicorn app.main:app

# Or with reload (may have issues with Python 3.14)
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for interactive API docs.

### Step 4: Setup Frontend (in another terminal)

```powershell
cd ..\frontend
npm install
npm run dev
```

Visit **http://localhost:5173** for the React UI.

---

## 📋 API Reference

### Health Check

```
GET /health
```

### Authentication — `/api/v1/auth`

| Method | Endpoint               | Auth | Description                            |
| ------ | ---------------------- | ---- | -------------------------------------- |
| `POST` | `/register`            | ❌   | Create account and send email OTP      |
| `POST` | `/verify-email`        | ❌   | Verify a new account                   |
| `POST` | `/resend-verification` | ❌   | Resend verification OTP                |
| `POST` | `/login`               | ❌   | Get JWT token after email verification |
| `GET`  | `/me`                  | ✅   | My profile                             |

**Example Register**:

```json
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Example Login Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

**Registration Flow**:

1. Submit `/register` with email and password.
2. Check the inbox for the verification OTP.
3. Submit the code to `/verify-email`.
4. Login is blocked until `email_verified=true` is stored in MongoDB.

### Documents — `/api/v1/documents`

| Method   | Endpoint                     | Auth | Description           |
| -------- | ---------------------------- | ---- | --------------------- |
| `POST`   | `/upload`                    | ✅   | Upload & encrypt file |
| `GET`    | `/`                          | ✅   | List my documents     |
| `DELETE` | `/{doc_id}`                  | ✅   | Delete document       |
| `POST`   | `/download/request/{doc_id}` | ✅   | Generate OTP          |
| `POST`   | `/download/verify/{doc_id}`  | ✅   | Submit OTP → download |

Download OTPs are always sent to the authenticated user's email address from the current JWT session.

---

## 🔐 Security Flow

```
User Registration
  ↓
  └─→ Password: bcrypt-hashed → stored in MongoDB

User Login
  ↓
  └─→ Verify password → issue JWT (30-min expiry)

Document Upload
  ↓
  ├─→ File validated (magic-byte MIME sniff, size check)
  ├─→ AES-encrypted with Fernet key
  ├─→ Stored as UUID.enc in storage/
  └─→ Metadata saved to MongoDB

Document Download
  ↓
  ├─→ Request OTP → generated, bcrypt-hashed, stored in MongoDB
  ├─→ OTP sent via email (or logged in DEBUG mode)
  ├─→ User submits OTP
  ├─→ Verify OTP hash + expiry + single-use flag
  ├─→ Read encrypted file → AES-decrypt in-memory
  └─→ Stream decrypted bytes to client
```

---

## 🧪 Testing with Postman

1. **Import Collection**:
   - Open Postman
   - Click "Import"
   - Select `Postman-Collection.json`

2. **Set Variables**:
   - Environment tab → "token" and "doc_id" variables
   - Or copy token from login response and paste into headers

3. **Test Flow**:
   - Register → Login → Upload → List → Download → Delete

---

## 🎨 Frontend Features

- **Professional UI** built with React + Tailwind CSS
- **Real-time Authentication** with JWT tokens
- **Document Management** - upload, list, download, delete
- **OTP Verification** - secure download with one-time password
- **Responsive Design** - works on desktop and mobile
- **Error Handling** - user-friendly error messages

See `../frontend/README.md` for detailed frontend documentation.

---

## 🔑 Environment Variables

| Variable                          | Default                                | Description                                |
| --------------------------------- | -------------------------------------- | ------------------------------------------ |
| `DEBUG`                           | `True`                                 | Enable debug logging                       |
| `MONGODB_URI`                     | —                                      | MongoDB Atlas connection string (required) |
| `MONGODB_DB_NAME`                 | `secure_vault`                         | Database name                              |
| `FERNET_KEY`                      | —                                      | AES encryption key (required)              |
| `JWT_SECRET_KEY`                  | —                                      | JWT signing secret (required)              |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                   | Token lifetime                             |
| `STORAGE_DIR`                     | `storage`                              | Encrypted file directory                   |
| `MAX_FILE_SIZE_MB`                | `10`                                   | Upload size limit                          |
| `ALLOWED_MIME_TYPES`              | `application/pdf,image/png,image/jpeg` | Allowed types                              |
| `OTP_EXPIRE_MINUTES`              | `5`                                    | OTP validity window                        |
| `OTP_LENGTH`                      | `6`                                    | OTP digit count                            |
| `SMTP_HOST`                       | ``                                     | SMTP server (blank = disabled)             |
| `SMTP_PORT`                       | `587`                                  | SMTP port                                  |
| `SMTP_USERNAME`                   | ``                                     | SMTP username                              |
| `SMTP_PASSWORD`                   | ``                                     | SMTP password                              |
| `EMAIL_FROM`                      | ``                                     | Sender email                               |

---

## ⚠️ Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong, random secrets for `JWT_SECRET_KEY` and `FERNET_KEY`
- [ ] Configure MongoDB Atlas IP whitelist for your server
- [ ] Setup SMTP for real email delivery
- [ ] Store `storage/` on encrypted, backed-up volume
- [ ] Deploy behind reverse proxy (nginx) with TLS
- [ ] Restrict CORS `allow_origins` to your frontend domain
- [ ] Implement request logging and monitoring
- [ ] Setup automated backups for MongoDB and storage files

---

## 🐛 Troubleshooting

### MongoDB Connection Fails

```
Error: Failed to connect to MongoDB
→ Check MONGODB_URI in .env
→ Verify MongoDB cluster is running
→ Check IP whitelist in MongoDB Atlas
```

### Token Expired

- Tokens expire after 30 minutes by default
- User must re-login to get a new token

### CORS Errors on Frontend

- Ensure backend has CORS enabled: `allow_origins=["*"]` in DEBUG mode
- For production, set to your frontend domain

### Port Already in Use

```powershell
# Change backend port
uvicorn app.main:app --port 8001

# Change frontend port (in vite.config.ts)
# port: 5174
```

---

## 📚 Technologies

**Backend**:

- FastAPI - Web framework
- MongoDB Atlas - Cloud database
- mongoengine - MongoDB ORM
- Fernet - Symmetric encryption
- JWT (python-jose) - Token-based auth
- bcrypt - Password hashing
- slowapi - Rate limiting

**Frontend**:

- React 18 - UI library
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client
- React Router - Navigation

---

## 📄 License

This project is for educational purposes. Use at your own risk in production.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Report bugs
2. Suggest features
3. Submit pull requests

---

**Built with ❤️ for secure document management**
