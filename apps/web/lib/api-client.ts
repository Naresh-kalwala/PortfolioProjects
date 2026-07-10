const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(
  path: string,
  token: string | null,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body && !(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(response.status, detail || response.statusText);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function createApiClient(token: string | null) {
  return {
    get: <T>(path: string) => request<T>(path, token),
    post: <T>(path: string, body?: unknown) =>
      request<T>(path, token, {
        method: "POST",
        body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
      }),
    patch: <T>(path: string, body?: unknown) =>
      request<T>(path, token, { method: "PATCH", body: JSON.stringify(body ?? {}) }),
    put: <T>(path: string, body?: unknown) =>
      request<T>(path, token, { method: "PUT", body: JSON.stringify(body ?? {}) }),
    delete: <T>(path: string) => request<T>(path, token, { method: "DELETE" }),
  };
}
