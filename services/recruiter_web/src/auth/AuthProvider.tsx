import { useEffect, useState, useCallback, type ReactNode } from 'react';
import type { Session } from '@ory/client';
import type { User } from '../types';
import { isAuthEnabled } from '../config';
import { getOryClient, getLoginUrl } from './ory';
import { AuthContext, type AuthState } from './AuthContext';

/**
 * Мок-пользователь для dev-окружения.
 */
const MOCK_USER: User = {
  id: 'dev-user-001',
  firstName: 'Dev',
  lastName: 'User',
  email: 'dev@x5teamintern.ru',
};

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Проверяет, является ли ошибка 401 (не авторизован).
 */
function isUnauthorizedError(error: unknown): boolean {
  if (error && typeof error === 'object') {
    // Axios-style error
    if ('response' in error) {
      const response = (error as { response?: { status?: number } }).response;
      return response?.status === 401;
    }
    // Ory client error
    if ('status' in error) {
      return (error as { status?: number }).status === 401;
    }
  }
  return false;
}

/**
 * Провайдер авторизации.
 * 
 * В prod-окружении использует Ory для проверки сессии.
 * В dev-окружении возвращает мок-пользователя без авторизации.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Извлекает данные пользователя из Ory сессии.
   */
  const extractUserFromSession = useCallback((session: Session): User => {
    const identity = session.identity;
    const traits = identity?.traits as Record<string, unknown> | undefined;

    return {
      id: identity?.id || '',
      firstName: (traits?.first_name as string) || '',
      lastName: (traits?.last_name as string) || '',
      email: (traits?.email as string) || '',
    };
  }, []);

  /**
   * Проверяет текущую сессию.
   */
  const checkSession = useCallback(async () => {
    // В dev-окружении сразу возвращаем мок-пользователя
    if (!isAuthEnabled()) {
      setUser(MOCK_USER);
      setIsLoading(false);
      return;
    }

    const oryClient = getOryClient();
    if (!oryClient) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const { data: session } = await oryClient.toSession();
      const extractedUser = extractUserFromSession(session);
      setUser(extractedUser);
      setError(null);
    } catch (err) {
      console.error('Auth check failed:', err);
      
      // Если 401 — пользователь не авторизован, редирект на логин
      if (isUnauthorizedError(err)) {
        const currentUrl = window.location.href;
        window.location.href = getLoginUrl(currentUrl);
        return;
      }
      
      // Другие ошибки (CORS, network) — показываем ошибку
      const errorMessage = err instanceof Error ? err.message : 'Ошибка авторизации';
      setError(errorMessage);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [extractUserFromSession]);

  /**
   * Выполняет логаут.
   */
  const logout = useCallback(async () => {
    // В dev-окружении просто очищаем пользователя
    if (!isAuthEnabled()) {
      setUser(null);
      return;
    }

    const oryClient = getOryClient();
    if (!oryClient) {
      return;
    }

    try {
      // Создаём logout flow и редиректим на logout URL
      const { data } = await oryClient.createBrowserLogoutFlow();
      window.location.href = data.logout_url;
    } catch (err) {
      console.error('Logout failed:', err);
    }
  }, []);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  const value: AuthState = {
    user,
    isLoading,
    isAuthenticated: user !== null,
    error,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
