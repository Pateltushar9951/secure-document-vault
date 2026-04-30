# Secure Document Vault - Frontend

A professional React + TypeScript UI for the Secure Document Vault application.

## Features

- **Modern UI** - Built with React 18, Tailwind CSS, and Lucide icons
- **Authentication** - Secure login/register with JWT tokens
- **Document Management** - Upload, download, and delete encrypted documents
- **OTP Security** - One-Time Password verification for downloads
- **Responsive Design** - Works seamlessly on desktop and mobile

## Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running on http://localhost:8000

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Backend URL

The frontend is configured to connect to `http://localhost:8000`. If your backend runs on a different URL, update `API_URL` in:

- `src/context/AuthContext.tsx` - Change `http://localhost:8000/api/v1`

### 3. Start Development Server

```bash
npm run dev
```

The app will open at `http://localhost:5173` by default.

## Building for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Navbar.tsx
│   │   └── ProtectedRoute.tsx
│   ├── context/             # React Context for state management
│   │   └── AuthContext.tsx
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   └── DashboardPage.tsx
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js

```

## API Integration

The frontend connects to the backend API with these endpoints:

- **Auth**
  - `POST /api/v1/auth/register` - Create account
  - `POST /api/v1/auth/login` - Login
  - `GET /api/v1/auth/me` - Get current user

- **Documents**
  - `GET /api/v1/documents/` - List documents
  - `POST /api/v1/documents/upload` - Upload document
  - `DELETE /api/v1/documents/{id}` - Delete document
  - `POST /api/v1/documents/download/request/{id}` - Request download OTP
  - `POST /api/v1/documents/download/verify/{id}` - Verify OTP and download

## Security Notes

- Tokens are stored in localStorage (consider using secure cookies in production)
- All requests include Bearer token authentication
- OTP verification is required before file downloads
- Files are encrypted with AES-128 on the server

## Technologies Used

- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation
- **Lucide Icons** - Icon library

## Troubleshooting

### CORS Issues

If you get CORS errors, ensure the backend has CORS enabled:

```python
# In backend/app/main.py
allow_origins=["*"] if settings.DEBUG else []
```

### Connection Refused

Make sure the backend is running on http://localhost:8000:

```bash
cd ..\backend
. ..\.venv\Scripts\Activate.ps1
uvicorn app.main:app
```

### Token Issues

If you're logged out unexpectedly, check if the token in localStorage has expired. The default expiry is 30 minutes.

## Development Tips

- Use React DevTools browser extension for debugging
- Check Network tab in browser DevTools for API calls
- Use `console.log()` in components to debug state

## Support

For issues with the API, refer to the main README.md in the parent directory.
