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

export async function apiFetch<ResponseBody>(
  path: string,
  options: RequestInit = {},
): Promise<ResponseBody> {
  if (API_BASE_URL === "") {
    throw new ApiError(0, "CONFIG_ERROR", "NEXT_PUBLIC_API_URL is not set");
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { Accept: "application/json", ...options.headers },
    });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Could not reach the backend");
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
