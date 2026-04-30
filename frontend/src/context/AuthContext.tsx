import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { API_BASE_URL } from "../config.ts";

interface User {
  id: string;
  email: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
}

interface RegistrationResponse {
  message: string;
  email: string;
  verification_required: boolean;
  expires_in_minutes: number;
  verification_code?: string | null;
}

interface VerificationResponse {
  message: string;
  email: string;
  email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<RegistrationResponse>;
  verifyEmail: (
    email: string,
    otpCode: string,
  ) => Promise<VerificationResponse>;
  resendVerification: (email: string) => Promise<RegistrationResponse>;
  logout: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      verifyToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data);
    } catch {
      localStorage.removeItem("token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
      email,
      password,
    });
    localStorage.setItem("token", response.data.access_token);
    await verifyToken(response.data.access_token);
  };

  const register = async (email: string, password: string) => {
    const response = await axios.post<RegistrationResponse>(
      `${API_BASE_URL}/auth/register`,
      {
        email,
        password,
      },
    );
    return response.data;
  };

  const verifyEmail = async (email: string, otpCode: string) => {
    const response = await axios.post<VerificationResponse>(
      `${API_BASE_URL}/auth/verify-email`,
      {
        email,
        otp_code: otpCode,
      },
    );
    return response.data;
  };

  const resendVerification = async (email: string) => {
    const response = await axios.post<RegistrationResponse>(
      `${API_BASE_URL}/auth/resend-verification`,
      {
        email,
      },
    );
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  const getToken = () => localStorage.getItem("token");

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        verifyEmail,
        resendVerification,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
