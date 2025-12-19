/**
 * Статусы задач рекрутера в канбан-доске.
 * 
 * - backlog: общий пул задач, видимый всем рекрутерам
 * - in_progress: задача взята в работу конкретным рекрутером
 * - done: задача успешно выполнена
 * - rejected: задача отклонена
 */
export type TaskStatus = 'backlog' | 'in_progress' | 'done' | 'rejected';

/**
 * Задача рекрутера.
 * 
 * Представляет задачу, требующую ручного вмешательства рекрутера.
 * Например: кандидат не нашёл подходящий слот, нужен перенос интервью и т.д.
 */
export interface Task {
  /** Уникальный идентификатор задачи (UUID) */
  id: string;
  
  /** Описание задачи */
  description: string;
  
  /** Текущий статус задачи */
  status: TaskStatus;
  
  /** Дата и время создания задачи (ISO 8601) */
  createdAt: string;
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

