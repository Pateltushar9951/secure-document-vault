import React, { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Lock, Mail, AlertCircle, Eye, EyeOff, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const stateMessage = (location.state as { message?: string } | null)?.message;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gray-950">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-600/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600/20 rounded-full blur-3xl"></div>
      </div>

      {/* Content */}
      <div className="relative w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8 animate-slideInFromLeft">
          <div className="flex justify-center mb-4">
            <div className="relative w-16 h-16">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl blur-lg opacity-75"></div>
              <div className="relative w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center">
                <Lock className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400">
            Sign in to access your secure documents
          </p>
        </div>

        {/* Card */}
        <div className="glass smooth-shadow rounded-2xl p-8 space-y-6">
          {stateMessage && (
            <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex gap-3">
              <p className="text-emerald-300 text-sm">{stateMessage}</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex gap-3 animate-fadeIn">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 w-5 h-5 -translate-y-1/2 text-gray-500 pointer-events-none" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ paddingLeft: "3.5rem" }}
                  className="w-full pl-14 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg
                           text-white placeholder-gray-500
                           focus:outline-none focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600/50
                           transition-all duration-200"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
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
                  className="w-full pl-14 pr-14 py-3 bg-gray-800/50 border border-gray-700 rounded-lg
                           text-white placeholder-gray-500
                           focus:outline-none focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600/50
                           transition-all duration-200"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-400 transition"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-8 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 
                       hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold
                       rounded-lg transition-all duration-300 transform
                       hover:scale-105 active:scale-95
                       disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                       flex items-center justify-center gap-2
                       shadow-lg shadow-indigo-600/20 hover:shadow-indigo-600/40"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-900 text-gray-500">
                Don't have an account?
              </span>
            </div>
          </div>

          {/* Sign Up Link */}
          <Link
            to="/register"
            className="block w-full py-3 border border-gray-700 hover:border-indigo-600/50 rounded-lg
                     text-center text-gray-300 font-medium transition-all duration-300
                     hover:bg-indigo-600/10"
          >
            Create Account
          </Link>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          By signing in, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
}
