import type { Task, TaskStatus } from '../types';
import { config } from '../config';

/**
 * Mock данные для разработки.
 * 
 * В реальном приложении эти данные будут приходить с бэкенда.
 */
const MOCK_TASKS: Task[] = [
  {
    id: '1',
    description: 'Кандидат Иванов И.И. не нашёл подходящий слот для интервью на позицию Python Developer',
    status: 'backlog',
    createdAt: '2024-12-19T10:30:00Z',
  },
  {
    id: '2',
    description: 'Необходимо согласовать перенос интервью с кандидатом Петрова А.С. на следующую неделю',
    status: 'backlog',
    createdAt: '2024-12-19T09:15:00Z',
  },
  {
    id: '3',
    description: 'Кандидат Сидоров М.В. запросил уточнение по условиям оффера',
    status: 'backlog',
    createdAt: '2024-12-18T16:45:00Z',
  },
  {
    id: '4',
    description: 'Проверить резюме кандидата без стандартного формата — требуется ручная оценка',
    status: 'backlog',
    createdAt: '2024-12-18T14:20:00Z',
  },
  {
    id: '5',
    description: 'Связаться с кандидатом Козловым Д.А. — не отвечает в боте более 3 дней',
    status: 'in_progress',
    createdAt: '2024-12-17T11:00:00Z',
  },
  {
    id: '6',
    description: 'Согласовать дополнительное интервью для кандидата Новикова Е.П.',
    status: 'in_progress',
    createdAt: '2024-12-17T09:30:00Z',
  },
  {
    id: '7',
    description: 'Успешно согласован перенос интервью для кандидата Морозовой К.Л.',
    status: 'done',
    createdAt: '2024-12-16T15:00:00Z',
  },
  {
    id: '8',
    description: 'Кандидат Волков Р.С. отказался от участия в процессе',
    status: 'rejected',
    createdAt: '2024-12-16T12:30:00Z',
  },
];

/**
 * Имитация задержки сети.
 */
const delay = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Получает список задач рекрутера.
 * 
 * В dev-окружении возвращает mock данные.
 * В prod-окружении делает запрос к API.
 */
export async function getTasks(): Promise<Task[]> {
  // В dev-окружении используем mock данные
  if (config.environment === 'dev') {
    await delay(300); // Имитируем задержку сети
    return [...MOCK_TASKS];
  }

  const response = await fetch(`${config.apiUrl}/recruiter/tasks`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.status}`);
  }

  return response.json();
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
  // В dev-окружении обновляем mock данные
  if (config.environment === 'dev') {
    await delay(200);
    const task = MOCK_TASKS.find((t) => t.id === taskId);
    if (!task) {
      throw new Error(`Task not found: ${taskId}`);
    }
    task.status = newStatus;
    return { ...task };
  }

  const response = await fetch(`${config.apiUrl}/recruiter/tasks/${taskId}`, {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status: newStatus }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update task: ${response.status}`);
  }

  return response.json();
}

