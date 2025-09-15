export type BackendStatus = "checking" | "starting" | "ready";

function healthUrl() {
  const base = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
  return base ? `${base}/health` : "/api/health";
}

export async function pingBackend(timeoutMs = 70000): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(healthUrl(), { cache: "no-store", signal: controller.signal });
    if (!res.ok) return false;
    const body = await res.json();
    return body?.status === "ok";
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}
