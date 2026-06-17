const API_URL = process.env.NEXT_PUBLIC_API_URL;

export function buildHeaders(userId: string, email?: string | null): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Clerk-User-Id": userId,
    ...(email ? { "X-User-Email": email } : {}),
  };
}

export async function apiFetch(
  path: string,
  userId: string,
  email?: string | null,
  options: RequestInit = {}
): Promise<Response> {
  return fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...buildHeaders(userId, email),
      ...(options.headers || {}),
    },
  });
}
