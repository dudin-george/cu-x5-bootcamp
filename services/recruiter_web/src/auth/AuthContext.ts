import { createContext } from 'react';
import type { User } from '../types';

/**
 * Состояние авторизации.
 */
export interface AuthState {
  /** Текущий пользователь (null если не авторизован) */
  user: User | null;
  
  /** Идёт загрузка данных авторизации */
  isLoading: boolean;
  
  /** Пользователь авторизован */
  isAuthenticated: boolean;
  
  /** Ошибка авторизации (CORS, network и т.д.) */
  error: string | null;
  
  /** Выполнить логаут */
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthState | null>(null);
