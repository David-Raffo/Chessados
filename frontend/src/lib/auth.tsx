import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { ApiError, api, getToken, setToken } from "./api";
import type { User } from "./types";

interface AuthState {
  user: User | null;
  loading: boolean;
  /** No se pudo contactar con el servidor al abrir la app (la sesión se conserva) */
  offline: boolean;
  retry: () => void;
  login: (username: string, password: string) => Promise<void>;
  register: (data: { username: string; password: string; level: number; invite_code: string | null }) => Promise<void>;
  logout: () => void;
  setUser: (u: User) => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(!!getToken());
  const [offline, setOffline] = useState(false);

  const loadMe = useCallback(() => {
    if (!getToken()) return;
    setLoading(true);
    setOffline(false);
    api<User>("/me")
      .then(setUser)
      .catch((e) => {
        // Solo un 401 significa sesión no válida; si el servidor no responde, se conserva el token
        if (e instanceof ApiError && e.status === 401) setToken(null);
        else setOffline(true);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(loadMe, [loadMe]);

  const login = useCallback(async (username: string, password: string) => {
    const r = await api<{ token: string; user: User }>("/auth/login", { body: { username, password } });
    setToken(r.token);
    setUser(r.user);
  }, []);

  const register = useCallback(async (data: { username: string; password: string; level: number; invite_code: string | null }) => {
    const r = await api<{ token: string; user: User }>("/auth/register", { body: data });
    setToken(r.token);
    setUser(r.user);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, offline, retry: loadMe, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth fuera de AuthProvider");
  return ctx;
}
