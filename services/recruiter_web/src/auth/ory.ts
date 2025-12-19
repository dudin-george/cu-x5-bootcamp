import { Configuration, FrontendApi } from '@ory/client';
import { config, isAuthEnabled } from '../config';

/**
 * Экземпляр Ory Frontend API.
 * 
 * Используется для работы с сессиями, логином и логаутом.
 * В dev-окружении не инициализируется (auth отключён).
 */
let oryClient: FrontendApi | null = null;

/**
 * Получает экземпляр Ory клиента.
 * 
 * @returns Ory Frontend API или null если auth отключён
 */
export const getOryClient = (): FrontendApi | null => {
  if (!isAuthEnabled()) {
    return null;
  }

  if (!oryClient) {
    oryClient = new FrontendApi(
      new Configuration({
        basePath: config.orySdkUrl,
        baseOptions: {
          withCredentials: true,
        },
      })
    );
  }

  return oryClient;
};

/**
 * Получает URL страницы логина Ory.
 * 
 * @param returnTo - URL для редиректа после успешного логина
 * @returns URL страницы логина
 */
export const getLoginUrl = (returnTo?: string): string => {
  const loginPath = '/ui/login';
  const baseUrl = config.orySdkUrl;
  
  if (returnTo) {
    return `${baseUrl}${loginPath}?return_to=${encodeURIComponent(returnTo)}`;
  }
  
  return `${baseUrl}${loginPath}`;
};

/**
 * Получает URL страницы логаута Ory.
 * 
 * @returns URL страницы логаута
 */
export const getLogoutUrl = (): string => {
  return `${config.orySdkUrl}/ui/logout`;
};

