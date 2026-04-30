import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Lock,
  Mail,
  AlertCircle,
  Eye,
  EyeOff,
  Check,
  ArrowRight,
} from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [resending, setResending] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [verificationStep, setVerificationStep] = useState(false);
  const [otpCode, setOtpCode] = useState("");
  const [verificationEmail, setVerificationEmail] = useState("");
  const { register, verifyEmail, resendVerification } = useAuth();
  const navigate = useNavigate();

  const validatePassword = (pwd: string) => {
    const hasUpper = /[A-Z]/.test(pwd);
    const hasLower = /[a-z]/.test(pwd);
    const hasDigit = /\d/.test(pwd);
    return pwd.length >= 8 && hasUpper && hasLower && hasDigit;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!validatePassword(password)) {
      setError(
        "Password must be at least 8 characters with uppercase, lowercase, and digits",
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const response = await register(email, password);
      setVerificationEmail(email);
      setVerificationStep(true);
      setOtpCode(response.verification_code || "");
      setMessage(response.message);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Registration failed. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!otpCode.trim()) {
      setError("Enter the verification code sent to your email.");
      return;
    }

    setVerifying(true);
    try {
      const response = await verifyEmail(verificationEmail, otpCode.trim());
      navigate("/login", { state: { message: response.message } });
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Email verification failed. Please try again.",
      );
    } finally {
      setVerifying(false);
    }
  };

  const handleResendVerification = async () => {
    setError("");
    setMessage("");
    setResending(true);

    try {
      const response = await resendVerification(verificationEmail);
      setMessage(response.message);
      if (response.verification_code) {
        setOtpCode(response.verification_code);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Unable to resend verification code.",
      );
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen px-4">
      <div className="w-full max-w-md">
        <div className="bg-slate-800 rounded-lg shadow-2xl border border-purple-500/20 p-8">
          <div className="flex justify-center mb-6">
            <Lock className="w-12 h-12 text-purple-400" />
          </div>
          <h1 className="text-3xl font-bold text-center text-white mb-2">
            Create Account
          </h1>
          <p className="text-center text-gray-400 mb-8">Join Secure Vault</p>

          {error && (
            <div className="mb-4 p-4 bg-red-900/20 border border-red-500/50 rounded-lg flex items-gap-2">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-300 text-sm ml-2">{error}</p>
            </div>
          )}

          {message && !error && (
            <div className="mb-4 p-4 bg-emerald-900/20 border border-emerald-500/50 rounded-lg flex items-start gap-2">
              <Check className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <p className="text-emerald-300 text-sm">{message}</p>
            </div>
          )}

          {!verificationStep ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 w-5 h-5 -translate-y-1/2 text-gray-500 pointer-events-none" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{ paddingLeft: "3.5rem" }}
                    className="w-full pl-14 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 w-5 h-5 -translate-y-1/2 text-gray-500 pointer-events-none" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{ paddingLeft: "3.5rem", paddingRight: "3.5rem" }}
                    className="w-full pl-14 pr-14 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Min 8 chars, 1 uppercase, 1 lowercase, 1 digit
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 w-5 h-5 -translate-y-1/2 text-gray-500 pointer-events-none" />
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    style={{ paddingLeft: "3.5rem", paddingRight: "3.5rem" }}
                    className="w-full pl-14 pr-14 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setShowConfirmPassword((current) => !current)
                    }
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition"
                    aria-label={
                      showConfirmPassword
                        ? "Hide confirm password"
                        : "Show confirm password"
                    }
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-6 py-2 bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-500 hover:to-purple-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
              >
                {loading ? "Creating account..." : "Register"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyEmail} className="space-y-4">
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
                <div className="flex items-start gap-2">
                  <Check className="mt-0.5 h-5 w-5 flex-shrink-0" />
                  <p>
                    We sent a verification code to{" "}
                    <span className="font-semibold">{verificationEmail}</span>.
                    Enter it below to activate your account.
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Verification Code
                </label>
                <input
                  type="text"
                  inputMode="numeric"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 tracking-[0.35em] text-center"
                  placeholder="123456"
                  maxLength={6}
                  required
                />
                <p className="text-xs text-gray-400 mt-1">
                  Check your inbox and spam folder if the code does not arrive.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={verifying}
                  className="flex-1 py-2 bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-500 hover:to-purple-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
                >
                  {verifying ? "Verifying..." : "Verify Email"}
                </button>
                <button
                  type="button"
                  onClick={handleResendVerification}
                  disabled={resending}
                  className="flex-1 py-2 border border-slate-600 text-gray-200 font-semibold rounded-lg transition hover:bg-slate-700 disabled:opacity-50"
                >
                  {resending ? "Resending..." : "Resend Code"}
                </button>
              </div>
            </form>
          )}

          <p className="text-center text-gray-400 mt-6">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-purple-400 hover:text-purple-300 font-semibold"
            >
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
