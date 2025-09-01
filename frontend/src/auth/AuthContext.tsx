import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMeApi, loginApi, registerApi } from "../api/auth";

type AuthState = {
  token: string | null;
  user: { email: string; workspace_name: string } | null;
  login: (email: string, password: string) => Promise<void>;
  registerAndLogin: (email: string, password: string, workspaceName: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [user, setUser] = useState<{ email: string; workspace_name: string } | null>(null);

  useEffect(() => {
    if (!token) return;
    getMeApi()
      .then((me) => setUser(me))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      });
  }, [token]);

  const value = useMemo(
    () => ({
      token,
      user,
      login: async (email: string, password: string) => {
        const data = await loginApi(email, password);
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        const me = await getMeApi();
        setUser(me);
      },
      registerAndLogin: async (email: string, password: string, workspaceName: string) => {
        const workspaceSlug =
          workspaceName
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-+|-+$/g, "") || "workspace";
        await registerApi({
          email,
          password,
          workspace_name: workspaceName,
          workspace_slug: workspaceSlug,
        });
        const data = await loginApi(email, password);
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        const me = await getMeApi();
        setUser(me);
      },
      logout: () => {
        localStorage.clear();
        setToken(null);
        setUser(null);
      },
    }),
    [token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
