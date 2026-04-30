const rawApiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.trim() ||
  "https://secure-document-vault-l7v2.onrender.com";

const normalizedApiBaseUrl = rawApiBaseUrl.replace(/\/$/, "");

export const API_BASE_URL = normalizedApiBaseUrl.endsWith("/api/v1")
  ? normalizedApiBaseUrl
  : `${normalizedApiBaseUrl}/api/v1`;
