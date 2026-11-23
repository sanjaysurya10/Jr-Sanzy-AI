const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: Record<string, unknown>;

  constructor(status: number, code: string, message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export interface AuthHandlers {
  getAccessToken: () => Promise<string | null>;
  refreshAccessToken: () => Promise<string | null>;
  onSessionExpired: () => void;
}

let authHandlers: AuthHandlers | null = null;

export function setAuthHandlers(handlers: AuthHandlers | null): void {
  authHandlers = handlers;
}

interface ErrorEnvelope {
  error: { code: string; message: string; details?: Record<string, unknown> };
}

function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (typeof value !== "object" || value === null || !("error" in value)) {
    return false;
  }
  const { error } = value;
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    typeof error.code === "string" &&
    "message" in error &&
    typeof error.message === "string"
  );
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

async function send(path: string, options: RequestInit, token: string | null): Promise<Response> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (typeof options.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token !== null) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  try {
    return await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Could not reach the backend");
  }
}

export async function apiFetch<ResponseBody>(
  path: string,
  options: RequestInit = {},
): Promise<ResponseBody> {
  if (API_BASE_URL === "") {
    throw new ApiError(0, "CONFIG_ERROR", "NEXT_PUBLIC_API_URL is not set");
  }

  const token = authHandlers ? await authHandlers.getAccessToken() : null;
  let response = await send(path, options, token);

  // FR-AUTH-4: on 401 refresh the session once; if that fails the session is over.
  if (response.status === 401 && authHandlers) {
    const refreshedToken = await authHandlers.refreshAccessToken();
    if (refreshedToken !== null) {
      response = await send(path, options, refreshedToken);
    }
    if (response.status === 401) {
      authHandlers.onSessionExpired();
    }
  }

  const body = await readJson(response);

  if (!response.ok) {
    if (isErrorEnvelope(body)) {
      throw new ApiError(response.status, body.error.code, body.error.message, body.error.details);
    }
    throw new ApiError(response.status, "INTERNAL", `Request failed with status ${response.status}`);
  }

  return body as ResponseBody;
}
