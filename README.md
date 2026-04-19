# Telegram Channel Analytics MVP

## О проекте

Это MVP для поиска сильных постов в Telegram-каналах. Проект через `Telethon` забирает посты из заданных каналов, сохраняет метрики в `PostgreSQL`, считает ранний сигнал популярности и показывает результат во frontend на `Next.js`.

## Что уже настроено

- Backend: `FastAPI`
- Frontend: `Next.js`
- Database: `PostgreSQL`
- Docker: `docker-compose.yml`
- Telegram scraping: `Telethon`
- Scheduler: `APScheduler`
- Channels for demo: `tproger,habr_com`
- API load protection:
  - `FETCH_LIMIT=30`
  - `SYNC_INTERVAL_MINUTES=120`
  - `TELEGRAM_REQUEST_PAUSE_SECONDS=3`

## Важное про секреты

Файлы с секретами уже должны быть локальными и не должны попадать в Git:

- `.env`
- `backend/.env`
- `frontend/.env.local`
- `backend/sessions/*.session`

Проверяй перед пушем:

```bash
git status --short
```

В GitHub не должны появляться:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`
- `.session` файл
- bot token

## Как запустить через Docker

Из корня проекта:

```bash
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker compose ps
```

Открыть frontend:

```text
http://localhost:3000
```

Проверить backend:

```text
http://localhost:8000/health
```

## Первый Telethon login

Первый Telegram login делается локально:

```bash
cd backend
python scripts/create_telethon_session.py
```

После этого появится файл:

```text
backend/sessions/telegram_user.session
```

Этот файл нельзя коммитить. Для сервера его нужно перенести вручную в такую же папку:

```text
backend/sessions/
```

## Запуск первого sync

Когда backend уже работает и session создана:

```bash
curl -X POST http://localhost:8000/api/sync
```

Проверить посты:

```text
http://localhost:8000/api/posts/top?period=7d&limit=20
```

## Как работает анализ

Проект берет посты канала за последние `90 дней` и считает медиану просмотров.

Дальше новый пост считается сильным, если:

```text
post_age <= 8 hours
views >= median_channel_views * 0.5
```

То есть если пост за первые 8 часов уже набрал хотя бы 50% от медианного поста этого канала, он помечается как `alert candidate`.

`alert score` считается так:

```text
alert_score = views / alert_threshold * 100
```

## Нюансы аналитики

- Сейчас основной сигнал — просмотры.
- `forwards`, `replies_count`, `reactions_total` сохраняются, но не являются главным alert-сигналом.
- Если будет слишком много ложных alert, threshold можно поднять с `50%` до `60%`.
- Если проект пропускает хорошие посты, threshold можно опустить до `40%`.
- Каналы растут или падают, поэтому медиана за 90 дней не идеальна, но для MVP этого достаточно.

## Что делать для cloud deploy

Самый простой путь для финального проекта:

1. Создать VM на Huawei Cloud / Oracle Cloud / Google Cloud.
2. Установить Docker и Git.
3. Склонировать repo.
4. Создать `.env` на сервере.
5. Перенести `backend/sessions/telegram_user.session` на сервер.
6. Запустить:

```bash
docker compose up -d --build
```

Для demo можно открыть:

```text
http://SERVER_IP:3000
```

Для Telegram Mini App нужен публичный `HTTPS`.

## Если секреты утекли

Если утекли `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`, это плохо, но это еще не полный доступ к аккаунту. Их могут использовать для попыток создать Telegram API client от имени твоего приложения.

Если утек `.session` файл, это намного опаснее: через него можно получить доступ к Telegram-аккаунту без одноразового кода.

Что делать при утечке:

1. Удалить `.session` файл с сервера и локально.
2. В Telegram завершить подозрительные активные сессии.
3. Создать новый Telethon login.
4. По возможности создать новое Telegram app на `my.telegram.org`.
5. Обновить `.env`.
6. Проверить, что секреты не попали в Git history.
