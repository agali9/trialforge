import { BrowserRouter, Link, Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import LoginPage from "./auth/LoginPage";
import PrivateRoute from "./auth/PrivateRoute";
import { useAuth } from "./auth/AuthContext";
import BackendStatusBanner, { useBackendStatus } from "./components/BackendStatusBanner";
import HowItWorksPage from "./pages/HowItWorksPage";
import RunCompareView from "./pages/RunCompareView";
import RunDetailPage from "./pages/RunDetailPage";
import RunListPage from "./pages/RunListPage";

function AuthenticatedLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const backend = useBackendStatus();

  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      <nav className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-6 py-3">
          <Link to="/experiments" className="text-lg font-semibold text-[var(--color-accent)]">
            TrialForge
          </Link>
          <Link to="/how-it-works" className="text-sm text-[var(--color-muted)] hover:text-[var(--color-text)]">
            How it works
          </Link>
          <div className="ml-auto text-sm text-[var(--color-muted)]">
            <span className="text-[var(--color-text)]">{user?.email || "Loading user..."}</span>
            {" · "}
            <span>{user?.workspace_name || "Workspace"}</span>
          </div>
          <button
            className="rounded bg-[var(--color-accent)] px-3 py-2 text-sm font-medium text-white"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Logout
          </button>
        </div>
      </nav>
      <main className="mx-auto max-w-7xl px-6 py-6">
        <BackendStatusBanner status={backend.status} elapsed={backend.elapsed} />
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={
            <PrivateRoute>
              <AuthenticatedLayout />
            </PrivateRoute>
          }
        >
          <Route path="/experiments" element={<RunListPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/runs/:id" element={<RunDetailPage />} />
          <Route path="/compare" element={<RunCompareView />} />
        </Route>
        <Route
          path="/"
          element={
            <Navigate to="/experiments" />
          }
        />
        <Route path="*" element={<Navigate to="/experiments" />} />
      </Routes>
    </BrowserRouter>
  );
}
