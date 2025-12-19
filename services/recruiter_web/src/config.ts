import type { AppConfig } from './types';

/**
 * Конфигурация приложения.
 * 
 * Читает значения из env-переменных, установленных на этапе сборки.
 * В dev-окружении auth отключён, в prod — работает через Ory.
 */
export const config: AppConfig = {
  environment: (import.meta.env.VITE_ENVIRONMENT as 'dev' | 'prod') || 'dev',
  orySdkUrl: import.meta.env.VITE_ORY_SDK_URL || '',
  apiUrl: import.meta.env.VITE_API_URL || '/api',
};

/**
 * Проверяет, включена ли авторизация.
 * Auth включён только в prod-окружении при наличии URL Ory SDK.
 */
export const isAuthEnabled = (): boolean => {
  return config.environment === 'prod' && config.orySdkUrl.length > 0;
};

