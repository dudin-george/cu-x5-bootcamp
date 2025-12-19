import type { Task, TaskStatus } from '../types';
import { config } from '../config';

/**
 * Ответ API со списком задач.
 */
interface TasksResponse {
  tasks: Task[];
}

/**
 * Кастомная ошибка API с понятным сообщением.
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public isNetworkError = false
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Получает список задач рекрутера.
 * 
 * Возвращает все задачи в BACKLOG + все задачи назначенные текущему рекрутеру.
 */
export async function getTasks(): Promise<Task[]> {
  let response: Response;

  try {
    response = await fetch(`${config.apiUrl}/tasks/`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    // Сетевая ошибка (API недоступен, нет интернета и т.д.)
    throw new ApiError(
      'Не удалось подключиться к серверу. Проверьте соединение или попробуйте позже.',
      undefined,
      true
    );
  }

  if (!response.ok) {
    // HTTP ошибка
    if (response.status === 401) {
      throw new ApiError('Сессия истекла. Пожалуйста, войдите снова.', 401);
    }
    if (response.status === 403) {
      throw new ApiError('Нет доступа к задачам.', 403);
    }
    if (response.status === 404) {
      throw new ApiError('API задач недоступен. Возможно, сервер обновляется.', 404);
    }
    if (response.status >= 500) {
      throw new ApiError('Ошибка сервера. Попробуйте позже.', response.status);
    }
    throw new ApiError(`Ошибка загрузки задач (${response.status})`, response.status);
  }

  // Парсим ответ
  let data: unknown;
  try {
    data = await response.json();
  } catch {
    throw new ApiError('Сервер вернул некорректный ответ.');
  }

  // Валидация структуры ответа
  if (!data || typeof data !== 'object') {
    throw new ApiError('Сервер вернул пустой ответ.');
  }

  const tasksResponse = data as TasksResponse;

  if (!Array.isArray(tasksResponse.tasks)) {
    // Если tasks нет или не массив — возвращаем пустой массив
    // Это нормально если бэк ещё не готов
    console.warn('API response missing tasks array, returning empty list');
    return [];
  }

  return tasksResponse.tasks;
}

/**
 * Обновляет статус задачи.
 * 
 * @param taskId - ID задачи
 * @param newStatus - Новый статус
 */
export async function updateTaskStatus(
  taskId: string,
  newStatus: TaskStatus
): Promise<Task> {
  let response: Response;

  try {
    response = await fetch(`${config.apiUrl}/tasks/${taskId}`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: newStatus }),
    });
  } catch (error) {
    throw new ApiError(
      'Не удалось подключиться к серверу.',
      undefined,
      true
    );
  }

  if (!response.ok) {
    if (response.status === 401) {
      throw new ApiError('Сессия истекла.', 401);
    }
    if (response.status === 404) {
      throw new ApiError('Задача не найдена.', 404);
    }
    if (response.status >= 500) {
      throw new ApiError('Ошибка сервера при обновлении задачи.', response.status);
    }
    throw new ApiError(`Не удалось обновить задачу (${response.status})`, response.status);
  }

  try {
    return await response.json();
  } catch {
    throw new ApiError('Сервер вернул некорректный ответ после обновления.');
  }
}
