/**
 * Статусы задач рекрутера в канбан-доске.
 * 
 * - BACKLOG: общий пул задач, видимый всем рекрутерам
 * - IN_PROGRESS: задача взята в работу конкретным рекрутером
 * - COMPLETED: задача успешно выполнена
 * - REJECTED: задача отклонена
 */
export type TaskStatus = 'BACKLOG' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED';

/**
 * Задача рекрутера.
 * 
 * Представляет задачу, требующую ручного вмешательства рекрутера.
 * Например: кандидат не нашёл подходящий слот, нужен перенос интервью и т.д.
 */
export interface Task {
  /** Уникальный идентификатор задачи (UUID) */
  id: string;
  
  /** Название типа задачи */
  task_type_name: string;
  
  /** Заголовок задачи */
  title: string;
  
  /** Описание задачи */
  description: string | null;
  
  /** Текущий статус задачи */
  status: TaskStatus;
  
  /** Контекст задачи */
  context: Record<string, unknown>;
  
  /** Дата и время создания задачи (ISO 8601) — опционально, скоро появится */
  created_at?: string;
}

/**
 * Пользователь системы (рекрутер).
 */
export interface User {
  /** Уникальный идентификатор пользователя */
  id: string;
  
  /** Имя */
  firstName: string;
  
  /** Фамилия */
  lastName: string;
  
  /** Email */
  email: string;
}

/**
 * Колонка канбан-доски.
 */
export interface Column {
  /** Идентификатор колонки (совпадает со статусом) */
  id: TaskStatus;
  
  /** Заголовок колонки для отображения */
  title: string;
}

/**
 * Конфигурация окружения приложения.
 */
export interface AppConfig {
  /** Текущее окружение */
  environment: 'dev' | 'prod';
  
  /** URL Ory SDK (пустой для dev) */
  orySdkUrl: string;
  
  /** URL API */
  apiUrl: string;
}

