import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { Task } from '../../types';
import './TaskCard.css';

interface TaskCardProps {
  task: Task;
}

/**
 * Форматирует дату в читаемый вид.
 */
function formatDate(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return `Сегодня, ${date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    })}`;
  }

  if (diffDays === 1) {
    return `Вчера, ${date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    })}`;
  }

  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Карточка задачи в канбан-доске.
 * 
 * Поддерживает drag & drop для перемещения между колонками.
 */
export function TaskCard({ task }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: task.id,
    data: {
      type: 'task',
      task,
    },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`task-card ${isDragging ? 'task-card--dragging' : ''}`}
      {...attributes}
      {...listeners}
    >
      <p className="task-card__description">{task.description}</p>
      <time className="task-card__date" dateTime={task.createdAt}>
        {formatDate(task.createdAt)}
      </time>
    </div>
  );
}

/**
 * Оверлей карточки при перетаскивании.
 */
export function TaskCardOverlay({ task }: TaskCardProps) {
  return (
    <div className="task-card task-card--overlay">
      <p className="task-card__description">{task.description}</p>
      <time className="task-card__date" dateTime={task.createdAt}>
        {formatDate(task.createdAt)}
      </time>
    </div>
  );
}

