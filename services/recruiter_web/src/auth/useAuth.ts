import { useContext } from 'react';
import { AuthContext, type AuthState } from './AuthContext';

/**
 * Хук для доступа к состоянию авторизации.
 * 
 * @throws Error если используется вне AuthProvider
 */
export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  
  return context;
}
