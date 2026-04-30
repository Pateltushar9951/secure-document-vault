import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, Lock, Shield } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="sticky top-0 z-40 bg-gradient-to-b from-gray-950 via-gray-950 to-transparent border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
            <Shield className="relative w-8 h-8 text-white p-1.5 bg-gray-900 rounded-lg" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            Secure Vault
          </h1>
        </Link>

        {/* User Info & Logout */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800/50 border border-gray-700">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-gray-300">{user?.email}</span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium
                     bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600
                     text-white rounded-lg transition-all duration-300
                     hover:shadow-lg hover:shadow-red-500/20
                     active:scale-95"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
