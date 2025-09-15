import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import BackendStatusBanner, { useBackendStatus } from "../components/BackendStatusBanner";
import { useAuth } from "./AuthContext";

export default function LoginPage() {
  const [mode, setMode] = useState<"signin" | "register">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const navigate = useNavigate();
  const { login, registerAndLogin } = useAuth();
  const backend = useBackendStatus();
  const backendReady = backend.status === "ready";

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (mode === "register") {
      await registerAndLogin(email, password, workspaceName);
    } else {
      await login(email, password);
    }
    navigate("/experiments");
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md p-6 rounded border border-[var(--color-border)] bg-[var(--color-surface)]">
        <BackendStatusBanner status={backend.status} elapsed={backend.elapsed} />
        <div className="mb-4 flex rounded border border-[var(--color-border)] p-1">
          <button
            type="button"
            className={`w-1/2 rounded px-3 py-2 text-sm ${mode === "signin" ? "bg-[var(--color-accent)] text-white" : "text-[var(--color-muted)]"}`}
            onClick={() => setMode("signin")}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`w-1/2 rounded px-3 py-2 text-sm ${mode === "register" ? "bg-[var(--color-accent)] text-white" : "text-[var(--color-muted)]"}`}
            onClick={() => setMode("register")}
          >
            Register
          </button>
        </div>
        <h1 className="text-xl mb-4">{mode === "register" ? "Register" : "Login"}</h1>
        <input className="w-full mb-3 p-2 bg-transparent border border-[var(--color-border)]" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full mb-3 p-2 bg-transparent border border-[var(--color-border)]" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {mode === "register" && (
          <input
            className="w-full mb-3 p-2 bg-transparent border border-[var(--color-border)]"
            placeholder="Workspace name"
            value={workspaceName}
            onChange={(e) => setWorkspaceName(e.target.value)}
            required
          />
        )}
        <button className="w-full p-2 rounded bg-[var(--color-accent)] text-white disabled:opacity-50" disabled={!backendReady}>
          {backendReady ? (mode === "register" ? "Create account" : "Sign In") : "Waiting for backend..."}
        </button>
      </form>
    </div>
  );
}
