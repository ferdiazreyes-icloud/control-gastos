import { Category, Movement, MovementStatus, ProcessResult, Tag } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Movements
export const getMovements = (params?: {
  status?: MovementStatus;
  date_from?: string;
  date_to?: string;
}) => {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.date_from) searchParams.set("date_from", params.date_from);
  if (params?.date_to) searchParams.set("date_to", params.date_to);
  const query = searchParams.toString();
  return apiFetch<Movement[]>(`/api/movements/${query ? `?${query}` : ""}`);
};

export const updateMovement = (
  id: string,
  data: Partial<Movement> & { tag_ids?: string[] }
) => apiFetch<Movement>(`/api/movements/${id}`, {
  method: "PATCH",
  body: JSON.stringify(data),
});

export const deleteMovement = (id: string) =>
  apiFetch<void>(`/api/movements/${id}`, { method: "DELETE" });

// Categories
export const getCategories = () =>
  apiFetch<Category[]>("/api/categories/");

export const createCategory = (data: {
  name: string;
  icon?: string;
  color?: string;
}) => apiFetch<Category>("/api/categories/", {
  method: "POST",
  body: JSON.stringify(data),
});

export const deleteCategory = (id: string) =>
  apiFetch<void>(`/api/categories/${id}`, { method: "DELETE" });

// Tags
export const getTags = () => apiFetch<Tag[]>("/api/tags/");

export const createTag = (data: { name: string; color?: string }) =>
  apiFetch<Tag>("/api/tags/", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const deleteTag = (id: string) =>
  apiFetch<void>(`/api/tags/${id}`, { method: "DELETE" });

// Email processing
export const processEmails = (maxResults = 20) =>
  apiFetch<ProcessResult>(`/api/emails/process?max_results=${maxResults}`, {
    method: "POST",
  });

// Auth
export const getAuthStatus = () =>
  apiFetch<{ authenticated: boolean; message: string }>("/auth/status");
