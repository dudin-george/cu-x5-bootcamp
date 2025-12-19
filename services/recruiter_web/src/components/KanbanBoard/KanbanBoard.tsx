import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
} from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import type { Task, TaskStatus, Column as ColumnType } from '../../types';
import { getTasks, updateTaskStatus } from '../../api';
import { Column } from './Column';
import { TaskCardOverlay } from './TaskCard';
import './KanbanBoard.css';

/**
 * Конфигурация колонок канбан-доски.
 */
const COLUMNS: ColumnType[] = [
  { id: 'backlog', title: 'Бэклог' },
  { id: 'in_progress', title: 'В работе' },
  { id: 'done', title: 'Выполнено' },
  { id: 'rejected', title: 'Отклонено' },
];

/**
 * Канбан-доска задач рекрутера.
 * 
 * Отображает 4 колонки с задачами.
 * Поддерживает drag & drop для перемещения задач между колонками.
 */
export function KanbanBoard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTask, setActiveTask] = useState<Task | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  /**
   * Загружает задачи при монтировании.
   */
  useEffect(() => {
    const loadTasks = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getTasks();
        setTasks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tasks');
      } finally {
        setIsLoading(false);
      }
    };

    loadTasks();
  }, []);

  /**
   * Группирует задачи по статусам.
   */
  const tasksByStatus = useMemo(() => {
    const grouped: Record<TaskStatus, Task[]> = {
      backlog: [],
      in_progress: [],
      done: [],
      rejected: [],
    };

    for (const task of tasks) {
      grouped[task.status].push(task);
    }

    // Сортируем по дате создания (новые сверху)
    for (const status of Object.keys(grouped) as TaskStatus[]) {
      grouped[status].sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
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
   * Обработчик перемещения над зоной.
   */
  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Находим статус целевой колонки
    const overColumn = COLUMNS.find((col) => col.id === overId);
    const overTask = tasks.find((t) => t.id === overId);
    
    let newStatus: TaskStatus | null = null;
    
    if (overColumn) {
      newStatus = overColumn.id;
    } else if (overTask) {
      newStatus = overTask.status;
    }

    if (!newStatus) return;

    // Обновляем статус задачи в локальном состоянии
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === activeId ? { ...task, status: newStatus } : task
      )
    );
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
      const task = tasks.find((t) => t.id === activeId);

      if (!task) return;

      // Сохраняем на сервере
      try {
        await updateTaskStatus(activeId, task.status);
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
          <p>Ошибка загрузки: {error}</p>
          <button onClick={() => window.location.reload()}>
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
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

