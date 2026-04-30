import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Upload,
  Download,
  Trash2,
  File,
  Lock,
  AlertCircle,
  CheckCircle,
  Cloud,
  Calendar,
  HardDrive,
  Eye,
  EyeOff,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { API_BASE_URL } from "../config";

interface Document {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  uploaded_at: string;
}

interface Toast {
  id: string;
  type: "success" | "error";
  message: string;
}

export default function DashboardPage() {
  const { getToken, user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showOtpModal, setShowOtpModal] = useState(false);
  const [otpInput, setOtpInput] = useState("");
  const [pendingDocId, setPendingDocId] = useState<string>("");
  const [showOtpPassword, setShowOtpPassword] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    let isMounted = true;

    const refreshDocuments = async () => {
      if (!user) {
        setDocuments([]);
        setLoading(false);
        return;
      }

      try {
        const token = getToken();
        const response = await axios.get(`${API_BASE_URL}/documents/`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (isMounted) {
          setDocuments(response.data);
        }
      } catch {
        if (isMounted) {
          setDocuments([]);
          addToast("Failed to load documents", "error");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    setLoading(true);
    refreshDocuments();

    return () => {
      isMounted = false;
    };
  }, [user?.id]);

  const loadDocuments = async () => {
    try {
      const token = getToken();
      const response = await axios.get(`${API_BASE_URL}/documents/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDocuments(response.data);
    } catch (err) {
      setDocuments([]);
      addToast("Failed to load documents", "error");
    } finally {
      setLoading(false);
    }
  };

  const addToast = (message: string, type: "success" | "error") => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const token = getToken();
      await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      setSelectedFile(null);
      addToast("Document uploaded successfully!", "success");
      await loadDocuments();
    } catch (err: any) {
      addToast(err.response?.data?.detail || "Upload failed", "error");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string, docName: string) => {
    if (!window.confirm(`Delete "${docName}"? This action cannot be undone.`))
      return;

    try {
      const token = getToken();
      await axios.delete(`${API_BASE_URL}/documents/${docId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      addToast("Document deleted successfully", "success");
      await loadDocuments();
    } catch {
      addToast("Failed to delete document", "error");
    }
  };

  const handleRequestDownload = async (docId: string) => {
    try {
      const token = getToken();
      const response = await axios.post(
        `${API_BASE_URL}/documents/download/request/${docId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } },
      );

      setPendingDocId(docId);
      setOtpInput("");
      setShowOtpPassword(false);

      const otp = response.data.otp_code;
      if (otp) {
        setOtpInput(otp);
      }

      setShowOtpModal(true);
    } catch (err) {
      addToast("Failed to request download", "error");
    }
  };

  const handleVerifyAndDownload = async (docId: string, otp: string) => {
    try {
      const token = getToken();
      const response = await axios.post(
        `${API_BASE_URL}/documents/download/verify/${docId}`,
        { otp_code: otp },
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: "blob",
        },
      );

      const doc = documents.find((d) => d.id === docId);
      const url = window.URL.createObjectURL(response.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = doc?.original_filename || "download";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setShowOtpModal(false);
      setOtpInput("");
      setPendingDocId("");
      addToast("Document downloaded successfully", "success");
    } catch (err) {
      addToast("Failed to download document", "error");
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.includes("pdf")) return "📄";
    if (mimeType.includes("image")) return "🖼️";
    return "📎";
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gradient-to-b from-gray-950 to-gray-900/50">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-4xl font-bold text-white">Your Vault</h1>
            <div className="text-sm text-gray-400">
              {documents.length} document{documents.length !== 1 ? "s" : ""}
            </div>
          </div>
          <p className="text-gray-400">
            Securely store and manage your encrypted documents
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Upload Section */}
        <div className="mb-12">
          <form onSubmit={handleUpload} className="space-y-4">
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 ${
                dragActive
                  ? "border-indigo-600 bg-indigo-600/10"
                  : "border-gray-700 bg-gray-900/50 hover:border-gray-600"
              }`}
            >
              <div className="px-6 py-12 text-center">
                <div className="flex justify-center mb-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 to-purple-600/20 rounded-full blur-xl"></div>
                    <Cloud
                      className={`relative w-12 h-12 ${
                        dragActive ? "text-indigo-400" : "text-gray-500"
                      } transition-colors`}
                    />
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-white mb-2">
                  {dragActive
                    ? "Drop your files here"
                    : "Drag files here or click to select"}
                </h3>
                <p className="text-sm text-gray-400 mb-6">
                  Supports PDF, PNG, JPG • Max 10 MB
                </p>

                <label className="inline-block">
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={(e) =>
                      setSelectedFile(e.target.files?.[0] || null)
                    }
                    className="hidden"
                  />
                  <span className="inline-block px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-medium rounded-lg cursor-pointer transition-all duration-300 transform hover:scale-105 active:scale-95">
                    Select File
                  </span>
                </label>
              </div>
            </div>

            {selectedFile && (
              <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700 animate-fadeIn">
                <div className="flex items-center gap-3">
                  <File className="w-5 h-5 text-indigo-400" />
                  <div>
                    <p className="text-white font-medium">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-gray-400">
                      {formatSize(selectedFile.size)}
                    </p>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-medium rounded-lg transition-all duration-300 disabled:opacity-50 flex items-center gap-2"
                >
                  {uploading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Upload</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Documents Section */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="h-24 bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl animate-pulse"
              ></div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-24">
            <div className="flex justify-center mb-6">
              <div className="relative w-20 h-20">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 to-purple-600/20 rounded-full blur-xl"></div>
                <Lock className="relative w-20 h-20 text-gray-600" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">
              No Documents Yet
            </h3>
            <p className="text-gray-400 max-w-md mx-auto">
              Your vault is empty. Upload your first document to get started
              with secure, encrypted storage.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="group relative overflow-hidden rounded-xl border border-gray-800 bg-gradient-to-r from-gray-900 to-gray-800/50 p-5 transition-all duration-300 hover:border-indigo-600/50 hover:bg-gradient-to-r hover:from-gray-900/80 hover:to-indigo-900/20 hover:shadow-lg hover:shadow-indigo-600/10"
              >
                {/* Document Card */}
                <div className="flex items-center gap-4">
                  {/* Icon & Name */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="text-2xl">
                        {getFileIcon(doc.mime_type)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="text-lg font-semibold text-white truncate group-hover:text-indigo-300 transition-colors">
                          {doc.original_filename}
                        </h3>
                      </div>
                    </div>

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-4 text-sm text-gray-400">
                      <div className="flex items-center gap-1.5">
                        <HardDrive className="w-4 h-4" />
                        {formatSize(doc.file_size)}
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        {formatDate(doc.uploaded_at)}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 sm:gap-3">
                    <button
                      onClick={() => handleRequestDownload(doc.id)}
                      className="flex items-center gap-2 px-4 py-2.5 rounded-lg
                               bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600
                               text-white font-medium text-sm
                               transition-all duration-300 transform
                               hover:scale-105 active:scale-95
                               shadow-lg shadow-indigo-600/20 hover:shadow-indigo-600/40"
                      title="Download this document"
                    >
                      <Download className="w-4 h-4" />
                      <span className="hidden sm:inline">Download</span>
                    </button>
                    <button
                      onClick={() =>
                        handleDelete(doc.id, doc.original_filename)
                      }
                      className="flex items-center gap-2 px-4 py-2.5 rounded-lg
                               bg-red-600/20 hover:bg-red-600/30 border border-red-500/30
                               text-red-300 hover:text-red-200 font-medium text-sm
                               transition-all duration-300"
                      title="Delete this document"
                    >
                      <Trash2 className="w-4 h-4" />
                      <span className="hidden sm:inline">Delete</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* OTP Modal */}
      {showOtpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 py-8 bg-black/60 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md glass smooth-shadow rounded-2xl p-8 border border-gray-700 animate-slideInFromLeft">
            {/* Header */}
            <div className="mb-6">
              <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-indigo-600/20 to-purple-600/20 mx-auto mb-4">
                <Lock className="w-6 h-6 text-indigo-400" />
              </div>
              <h2 className="text-2xl font-bold text-white text-center mb-2">
                Verify Download
              </h2>
              <p className="text-center text-gray-400">
                {otpInput
                  ? "DEBUG MODE: OTP is pre-filled below"
                  : "Enter the 6-digit code sent to your email"}
              </p>
            </div>

            {/* OTP Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-3">
                One-Time Password
              </label>
              <div className="relative">
                <input
                  type={showOtpPassword ? "text" : "password"}
                  value={otpInput}
                  onChange={(e) => setOtpInput(e.target.value.slice(0, 6))}
                  placeholder="000000"
                  maxLength="6"
                  className="w-full px-4 py-4 bg-gray-800/50 border-2 border-gray-700 rounded-lg
                           text-white text-center text-3xl tracking-widest font-mono
                           placeholder-gray-600
                           focus:outline-none focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/50
                           transition-all duration-200"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowOtpPassword(!showOtpPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-400"
                >
                  {showOtpPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Enter the 6-digit code to proceed
              </p>
            </div>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowOtpModal(false);
                  setOtpInput("");
                  setPendingDocId("");
                }}
                className="flex-1 px-4 py-3 bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700
                         text-gray-300 font-medium rounded-lg transition-all duration-300"
              >
                Cancel
              </button>
              <button
                onClick={() => handleVerifyAndDownload(pendingDocId, otpInput)}
                disabled={otpInput.length !== 6}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700
                         hover:from-indigo-500 hover:to-indigo-600 text-white font-medium
                         rounded-lg transition-all duration-300 transform
                         hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                         flex items-center justify-center gap-2"
              >
                {otpInput.length === 6 && <CheckCircle className="w-4 h-4" />}
                <span>{otpInput.length === 6 ? "Download" : "Enter OTP"}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toasts */}
      <div className="fixed bottom-6 right-6 z-40 space-y-3">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg glass border animate-slideInFromLeft ${
              toast.type === "success"
                ? "bg-green-500/10 border-green-500/30 text-green-300"
                : "bg-red-500/10 border-red-500/30 text-red-300"
            }`}
          >
            {toast.type === "success" ? (
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            )}
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
