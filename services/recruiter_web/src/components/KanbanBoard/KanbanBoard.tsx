import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
} from '@dnd-kit/core';
import type { Task, TaskStatus, Column as ColumnType } from '../../types';
import { getTasks, updateTaskStatus, ApiError } from '../../api';
import { Column } from './Column';
import { TaskCardOverlay } from './TaskCard';
import './KanbanBoard.css';

interface ErrorState {
  message: string;
  isNetworkError: boolean;
}

/**
 * Конфигурация колонок канбан-доски.
 */
const COLUMNS: ColumnType[] = [
  { id: 'BACKLOG', title: 'Бэклог' },
  { id: 'IN_PROGRESS', title: 'В работе' },
  { id: 'COMPLETED', title: 'Выполнено' },
  { id: 'REJECTED', title: 'Отклонено' },
];

/**
 * Канбан-доска задач рекрутера.
 * 
 * Отображает 4 колонки с задачами.
 * Поддерживает drag & drop для перемещения задач между колонками.
 * Порядок карточек определяется датой создания (новые сверху).
 */
export function KanbanBoard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ErrorState | null>(null);
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor)
  );

  /**
   * Загружает задачи.
   */
  const loadTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError({
          message: err.message,
          isNetworkError: err.isNetworkError,
        });
      } else {
        setError({
          message: 'Неизвестная ошибка при загрузке задач.',
          isNetworkError: false,
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Загружает задачи при монтировании.
   */
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  /**
   * Группирует задачи по статусам и сортирует по дате создания (когда появится).
   */
  const tasksByStatus = useMemo(() => {
    const grouped: Record<TaskStatus, Task[]> = {
      BACKLOG: [],
      IN_PROGRESS: [],
      COMPLETED: [],
      REJECTED: [],
    };

    for (const task of tasks) {
      grouped[task.status].push(task);
    }

    // Сортируем по дате создания (старые сверху, новые снизу)
    // Пока created_at не доступен — сохраняем порядок с сервера
    for (const status of Object.keys(grouped) as TaskStatus[]) {
      grouped[status].sort((a, b) => {
        if (a.created_at && b.created_at) {
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        }
        return 0; // Сохраняем порядок если даты нет
      });
    }

    return grouped;
  }, [tasks]);

  /**
   * Обработчик начала перетаскивания.
   */
  const handleDragStart = useCallback((event: DragStartEvent) => {
    const { active } = event;
    const task = tasks.find((t) => t.id === active.id);
    if (task) {
      setActiveTask(task);
    }
  }, [tasks]);

  /**
   * Обработчик завершения перетаскивания.
   */
  const handleDragEnd = useCallback(
    async (event: DragEndEvent) => {
      const { active, over } = event;
      setActiveTask(null);

      if (!over) return;

      const activeId = active.id as string;
      const overId = over.id as string;

      // Находим задачу
      const task = tasks.find((t) => t.id === activeId);
      if (!task) return;

      // Определяем целевую колонку
      const targetColumn = COLUMNS.find((col) => col.id === overId);
      if (!targetColumn) return;

      // Если статус не изменился — ничего не делаем
      if (task.status === targetColumn.id) return;

      const newStatus = targetColumn.id;

      // Обновляем локально
      setTasks((prevTasks) =>
        prevTasks.map((t) =>
          t.id === activeId ? { ...t, status: newStatus } : t
        )
      );

      // Сохраняем на сервере
      try {
        await updateTaskStatus(activeId, newStatus);
      } catch (err) {
        // При ошибке перезагружаем задачи
        console.error('Failed to update task status:', err);
        const data = await getTasks();
        setTasks(data);
      }
    },
    [tasks]
  );

  /**
   * Обработчик отмены перетаскивания.
   */
  const handleDragCancel = useCallback(() => {
    setActiveTask(null);
  }, []);

  if (isLoading) {
    return (
      <div className="kanban-board kanban-board--loading">
        <div className="kanban-board__loader">Загрузка задач...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="kanban-board kanban-board--error">
        <div className="kanban-board__error">
          <div className="kanban-board__error-icon">
            {error.isNetworkError ? '🔌' : '⚠️'}
          </div>
          <p className="kanban-board__error-message">{error.message}</p>
          <button 
            className="kanban-board__retry-btn"
            onClick={loadTasks}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className="kanban-board">
        {COLUMNS.map((column) => (
          <Column
            key={column.id}
            column={column}
            tasks={tasksByStatus[column.id]}
          />
        ))}
      </div>

      <DragOverlay>
        {activeTask && <TaskCardOverlay task={activeTask} />}
      </DragOverlay>
    </DndContext>
  );
}
