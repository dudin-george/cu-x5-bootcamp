import { useDroppable } from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import type { Task, TaskStatus, Column as ColumnType } from '../../types';
import { TaskCard } from './TaskCard';
import './Column.css';

interface ColumnProps {
  column: ColumnType;
  tasks: Task[];
}

/**
 * Возвращает цвет акцента для колонки по статусу.
 */
function getColumnAccentColor(status: TaskStatus): string {
  switch (status) {
    case 'backlog':
      return 'var(--accent-amber)';
    case 'in_progress':
      return 'var(--accent-blue)';
    case 'done':
      return 'var(--x5-green)';
    case 'rejected':
      return 'var(--accent-red)';
    default:
      return 'var(--text-muted)';
  }
}

/**
 * Колонка канбан-доски.
 * 
 * Содержит заголовок, счётчик задач и список карточек.
 * Является droppable зоной для перетаскивания карточек.
 */
export function Column({ column, tasks }: ColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
    data: {
      type: 'column',
      column,
    },
  });

  const taskIds = tasks.map((task) => task.id);
  const accentColor = getColumnAccentColor(column.id);

  return (
    <div
      className={`column ${isOver ? 'column--over' : ''}`}
      style={{ '--column-accent': accentColor } as React.CSSProperties}
    >
      <div className="column__header">
        <div className="column__title-row">
          <span className="column__indicator" />
          <h2 className="column__title">{column.title}</h2>
        </div>
        <span className="column__count">{tasks.length}</span>
      </div>

      <div ref={setNodeRef} className="column__content">
        <SortableContext items={taskIds} strategy={verticalListSortingStrategy}>
          {tasks.length === 0 ? (
            <div className="column__empty">
              Нет задач
            </div>
          ) : (
            tasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))
          )}
        </SortableContext>
      </div>
    </div>
  );
}

