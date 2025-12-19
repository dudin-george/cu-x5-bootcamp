import { useDraggable } from '@dnd-kit/core';
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
 * Порядок карточек определяется датой создания (не drag & drop).
 */
export function TaskCard({ task }: TaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging,
  } = useDraggable({
    id: task.id,
    data: {
      type: 'task',
      task,
    },
  });

  const style = {
    transform: CSS.Translate.toString(transform),
  };

  // Показываем title, а description как дополнение если есть
  const displayText = task.description || task.title;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`task-card ${isDragging ? 'task-card--dragging' : ''}`}
      {...attributes}
      {...listeners}
    >
      <span className="task-card__type">{task.task_type_name}</span>
      <p className="task-card__description">{displayText}</p>
      {task.created_at && (
        <time className="task-card__date" dateTime={task.created_at}>
          {formatDate(task.created_at)}
        </time>
      )}
    </div>
  );
}

/**
 * Оверлей карточки при перетаскивании.
 */
export function TaskCardOverlay({ task }: TaskCardProps) {
  const displayText = task.description || task.title;

  return (
    <div className="task-card task-card--overlay">
      <span className="task-card__type">{task.task_type_name}</span>
      <p className="task-card__description">{displayText}</p>
      {task.created_at && (
        <time className="task-card__date" dateTime={task.created_at}>
          {formatDate(task.created_at)}
        </time>
      )}
    </div>
  );
}
