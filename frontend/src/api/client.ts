// Thin fetch wrapper: JSON in, JSON out, and errors carry the backend's
// human-readable `detail` so components can show it directly.

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  let res: Response;
  try {
    const isForm = body instanceof FormData;
    res = await fetch(path, {
      method,
      body: isForm ? body : body === undefined ? undefined : JSON.stringify(body),
      headers: isForm || body === undefined ? undefined : { "Content-Type": "application/json" },
    });
  } catch {
    throw new ApiError(0, "Kuki's server isn't running. Start it with: python -m kuki");
  }
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new ApiError(res.status, messageFrom(data) ?? `Something went wrong (${res.status}).`);
  }
  return data as T;
}

function messageFrom(data: unknown): string | null {
  if (!data || typeof data !== "object" || !("detail" in data)) return null;
  const detail = (data as { detail: unknown }).detail;
  if (typeof detail === "string") return detail;
  // FastAPI validation errors arrive as a list of {msg} objects.
  if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
  return null;
}

export const http = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  patch: <T>(path: string, body: unknown) => request<T>("PATCH", path, body),
  del: (path: string) => request<void>("DELETE", path),
};
