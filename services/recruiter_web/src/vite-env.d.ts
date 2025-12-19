/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Окружение: dev или prod */
  readonly VITE_ENVIRONMENT: 'dev' | 'prod';
  
  /** URL Ory SDK для авторизации */
  readonly VITE_ORY_SDK_URL: string;
  
  /** URL API */
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
