const BASE = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export function token() {
  return localStorage.getItem("skillmatch_token") || "";
}

export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});

  if (token()) {
    headers.set("Authorization", `Bearer ${token()}`);
  }

  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  let response;

  try {
    response = await fetch(`${BASE}${path}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(
      `Cannot reach backend at ${BASE}. Please start FastAPI.`
    );
  }

  const contentType = response.headers.get("content-type") || "";

  let data;

  try {
    data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();
  } catch {
    data = null;
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    if (typeof data === "string" && data.trim()) {
      message = data;
    } else if (data && typeof data === "object") {
      const detail = data.detail || data.message;

      if (typeof detail === "string") {
        message = detail;
      } else if (detail) {
        message = JSON.stringify(detail);
      }
    }

    throw new Error(message);
  }

  return data;
}

export const json = (method, body) => ({
  method,
  body: JSON.stringify(body),
});