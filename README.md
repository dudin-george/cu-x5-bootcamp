# X5 Hiring Bootcamp

Платформа для автоматизации найма: Telegram-боты для кандидатов и HR + веб-интерфейс для рекрутеров.

## Сервисы

| Сервис | Описание |
|--------|----------|
| `core-api` | Основной API |
| `candidate-bot` | Telegram бот для кандидатов |
| `hm-bot` | Telegram бот для HR |
| `worker` | Фоновые задачи |
| `recruiter-web` | Веб-интерфейс рекрутера |

## Локальный запуск

```bash
# Установить зависимости
make install

# Запустить нужный сервис
make api           # http://localhost:8001
make candidate-bot # http://localhost:8002
make hm-bot        # http://localhost:8003
make worker
make web           # http://localhost:5173
```
