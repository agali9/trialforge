import { useEffect, useState } from "react";
import { pingBackend, type BackendStatus } from "../api/backendStatus";

export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const started = Date.now();
    const tick = window.setInterval(() => {
      if (!cancelled) setElapsed(Math.floor((Date.now() - started) / 1000));
    }, 1000);
    const slow = window.setTimeout(() => {
      if (!cancelled) setStatus((current) => (current === "ready" ? current : "starting"));
    }, 1200);

    async function waitUntilReady() {
      while (!cancelled) {
        const ok = await pingBackend();
        if (cancelled) return;
        if (ok) {
          setStatus("ready");
          return;
        }
        setStatus("starting");
        await new Promise((resolve) => window.setTimeout(resolve, 3000));
      }
    }

    waitUntilReady();
    return () => {
      cancelled = true;
      window.clearInterval(tick);
      window.clearTimeout(slow);
    };
  }, []);

  return { status, elapsed };
}

export default function BackendStatusBanner({ status, elapsed }: { status: BackendStatus; elapsed: number }) {

  if (status === "ready") {
    return (
      <div className="mb-4 flex items-center gap-2 rounded border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-300">
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
        Backend is ready
      </div>
    );
  }

  const label = status === "checking" ? "Checking backend..." : "Backend is starting";

  return (
    <div className="mb-4 flex items-start gap-3 rounded border border-amber-500/40 bg-amber-500/10 px-3 py-3 text-sm text-amber-100">
      <div className="mt-0.5 h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-amber-200 border-t-transparent" />
      <div>
        <p className="font-medium">{label}</p>
        <p className="mt-1 text-amber-100/80">
          The Render service sleeps when idle and can take up to a minute to wake. You can wait here. {elapsed > 0 ? `Waiting ${elapsed}s.` : ""}
        </p>
      </div>
    </div>
  );
}
