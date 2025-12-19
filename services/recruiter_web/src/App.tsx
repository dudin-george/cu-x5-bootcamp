import { AuthProvider, useAuth } from './auth';
import { UserMenu } from './components/UserMenu';
import { KanbanBoard } from './components/KanbanBoard';
import { config } from './config';
import './App.css';

/**
 * Основной контент приложения.
 * Показывается после загрузки авторизации.
 */
function AppContent() {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="app">
        <div className="app__loading">
          <div className="app__loading-spinner" />
          <span>Загрузка...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header__left">
          <div className="logo">
            <span className="logo__x5">X5</span>
            <span className="logo__divider">/</span>
            <span className="logo__text">HIRING</span>
          </div>
        </div>

        <div className="header__right">
          {config.environment === 'dev' && (
            <span className="env-badge">DEV</span>
          )}
          <UserMenu />
        </div>
      </header>

      <main className="main">
        <KanbanBoard />
      </main>
    </div>
  );
}

/**
 * Корневой компонент приложения.
 */
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
