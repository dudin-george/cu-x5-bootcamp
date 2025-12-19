import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../auth';
import './UserMenu.css';

/**
 * Компонент меню пользователя.
 * 
 * Отображает иконку пользователя, при клике открывается dropdown
 * с именем пользователя и кнопкой выхода.
 */
export function UserMenu() {
  const { user, logout, isLoading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  /**
   * Закрывает меню при клике вне его.
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  /**
   * Закрывает меню при нажатии Escape.
   */
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const toggleMenu = () => {
    setIsOpen((prev) => !prev);
  };

  const handleLogout = async () => {
    setIsOpen(false);
    await logout();
  };

  if (isLoading) {
    return (
      <div className="user-menu">
        <div className="user-menu__button user-menu__button--loading">
          <span className="user-menu__icon">•••</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const initials = `${user.firstName.charAt(0)}${user.lastName.charAt(0)}`.toUpperCase();
  const fullName = `${user.firstName} ${user.lastName}`;

  return (
    <div className="user-menu" ref={menuRef}>
      <button
        className="user-menu__button"
        onClick={toggleMenu}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="Меню пользователя"
      >
        <span className="user-menu__initials">{initials}</span>
      </button>

      {isOpen && (
        <div className="user-menu__dropdown" role="menu">
          <div className="user-menu__info">
            <span className="user-menu__name">{fullName}</span>
            <span className="user-menu__email">{user.email}</span>
          </div>
          <div className="user-menu__divider" />
          <button
            className="user-menu__logout"
            onClick={handleLogout}
            role="menuitem"
          >
            Выйти
          </button>
        </div>
      )}
    </div>
  );
}

