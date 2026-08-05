import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const MEDIA_BASE_URL = process.env.NEXT_PUBLIC_MEDIA_BASE_URL ?? API_BASE_URL.replace(/\/api\/v1\/?$/, "");

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: "application/json",
  },
});

export type ApiResponse<T> = {
  success?: boolean;
  data?: T;
};

export type PaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

export function unwrapApiData<T>(payload: unknown): T {
  if (payload && typeof payload === "object") {
    const response = payload as ApiResponse<T> & PaginatedResponse<T>;

    if (response.success && response.data !== undefined) {
      return response.data as T;
    }

    if (Array.isArray(response.results)) {
      return response.results as T;
    }

    if (Array.isArray((payload as { data?: unknown }).data)) {
      return (payload as { data: T }).data;
    }
  }

  return payload as T;
}

export function unwrapListData<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[];
  }

  if (payload && typeof payload === "object") {
    const response = payload as ApiResponse<T[]> & PaginatedResponse<T>;

    if (Array.isArray(response.data)) {
      return response.data as T[];
    }

    if (Array.isArray(response.results)) {
      return response.results as T[];
    }
  }

  return [];
}

export function buildMediaUrl(path?: string | null): string | null {
  if (!path) {
    return null;
  }

  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  const sanitizedPath = path.replace(/^\/+/, "");
  return `${MEDIA_BASE_URL.replace(/\/+$/, "")}/${sanitizedPath}`;
}

export function getCourseLabel(course: { name?: string | null; id?: number | null }): string {
  return course.name ?? `Course #${course.id ?? "unknown"}`;
}

export { API_BASE_URL, MEDIA_BASE_URL };
