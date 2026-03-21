# Telegram Channel Analytics MVP

## О проекте

Это MVP для поиска сильных Telegram-постов в заранее заданных каналах.

Проект:

- берет список каналов из конфига
- через `Telethon` заходит в них под user session
- сохраняет посты и метрики в `PostgreSQL`
- считает ранний сигнал поста относительно обычной динамики канала
- помечает пост как alert candidate, если за первые 8 часов он набрал сильные просмотры
- показывает результат через `FastAPI` и `Next.js`

Смысл проекта простой: не просто смотреть “у какого поста много просмотров вообще”, а быстро находить посты, которые для своего канала полетели unusually хорошо в самом начале.

## Что нужно сделать, чтобы запустить проект

### 1. Подготовить env-файлы

Создай:

- `backend/.env` из `backend/.env.example`
- `frontend/.env.local` из `frontend/.env.example`
- root `.env` из `.env.example`, если хочешь запускать через `docker compose`

В `backend/.env` обязательно укажи:

- `DATABASE_URL`
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`
- `TELETHON_SESSION_NAME`
- `TELEGRAM_CHANNELS`

Пример `TELEGRAM_CHANNELS`:

```env
TELEGRAM_CHANNELS=durov,telegram,habr
```

В `frontend/.env.local` укажи:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 2. Поднять базу и прогнать миграции

Локально:

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
alembic upgrade head
```

Если через Docker:

```bash
docker compose up --build
```

Backend сам прогонит миграции при старте.

### 3. Сделать первый Telethon login

```bash
cd backend
python scripts/create_telethon_session.py
```

После этого в `backend/sessions/` должен появиться session file.

### 4. Запустить backend

Локально:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Запустить frontend

Локально:

```bash
cd frontend
npm install
npm run dev
```

Открывай:

```text
http://localhost:3000
```

### 6. Запустить первый sync

Когда backend уже поднят:

```bash
curl -X POST http://localhost:8000/api/sync
```

После этого проект начнет сохранять посты и считать сигналы.

## Что нужно сделать, чтобы проект реально работал

Тут уже именно ручные шаги, без которых код сам по себе не оживет.

### 1. Получить `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`

1. Открой `https://my.telegram.org`
2. Залогинься своим Telegram-аккаунтом
3. Открой `API development tools`
4. Создай application
5. Скопируй `api_id`
6. Скопируй `api_hash`

Их нельзя хардкодить в коде. Клади только в backend env.

### 2. Подготовить Telegram-аккаунт для Telethon

Проект парсит каналы не через Bot API, а через обычный Telegram user session.

Значит:

- нужен живой Telegram-аккаунт
- нужен номер телефона этого аккаунта
- нужно один раз пройти login через Telethon script

### 3. Создать бота в `@BotFather`

Бот нужен не для scraping, а для открытия frontend как Mini App.

Шаги:

1. Открой `@BotFather`
2. Запусти `/newbot`
3. Создай бота
4. Сохрани bot token в безопасное место

Bot token не надо хранить во frontend code.

### 4. Настроить Mini App / Web App URL

Если хочешь открыть проект внутри Telegram:

1. Открой `@BotFather`
2. Запусти `/mybots`
3. Выбери своего бота
4. Открой `Bot Settings`
5. Найди настройку `Menu Button` или Web App / Mini App
6. Укажи HTTPS URL твоего frontend

Важно:

- для Telegram нужен именно публичный `HTTPS`
- `localhost` внутри реального Telegram не подойдет

### 5. Указать отслеживаемые каналы

Проект следит только за теми каналами, которые ты явно прописал в:

```env
TELEGRAM_CHANNELS=durov,telegram,habr
```

Если канала нет в этом списке, проект его не анализирует.

## Как проверить, что всё работает

### Backend health

Открой:

```text
http://localhost:8000/health
```

### Список каналов

Открой:

```text
http://localhost:8000/api/channels
```

### Ручной sync

Запусти:

```bash
curl -X POST http://localhost:8000/api/sync
```

### Проверка top posts

Открой:

```text
http://localhost:8000/api/posts/top?period=7d&limit=20
```

### Проверка recent posts

Открой:

```text
http://localhost:8000/api/posts/recent?limit=20
```

### Проверка frontend

Открой:

```text
http://localhost:3000
```

Ты должен увидеть:

- список каналов
- фильтр периода
- список постов
- пометки alert candidate у сильных ранних постов

## Как работает анализ

Сейчас логика простая и намеренно без ML.

Для каждого канала проект берет уже сохраненные посты за последние `90 дней` и считает по ним медиану просмотров.

Дальше для нового поста:

1. смотрим, сколько у него просмотров в момент sync
2. смотрим, не старше ли он `8 часов`
3. считаем порог:

```text
alert_threshold = median_views_of_channel * 0.5
```

4. если посту не больше `8 часов` и его `views >= alert_threshold`, пост помечается как `alert candidate`

Дополнительно считается `alert score`:

```text
alert_score = views / alert_threshold * 100
```

Примеры:

- `100` = пост ровно дошел до порога
- `120` = пост сильнее порога на 20%
- `200` = пост набрал в 2 раза больше нужного минимума

Во frontend и API top posts сортируются так, чтобы alert candidate поднимались выше обычных постов.

## Нюансы аналитики

### 1. Каналы со временем растут

Да, это влияет на baseline.

Сейчас проект это специально не усложняет: он просто берет медиану просмотров канала за последние `90 дней`.

Из-за этого возможны два эффекта:

- быстро растущий канал может получать слишком “мягкий” baseline
- падающий канал может получать слишком “жесткий” baseline

На текущем этапе это нормально.

### 2. Порог `50%` не высечен в камне

Сейчас захардкожена простая граница:

```text
50% от медианы просмотров канала
```

Если увидишь слишком много ложных алертов, можно поднять threshold:

- до `60%`

Если наоборот проект пропускает хорошие посты, можно опустить:

- до `40%`

### 3. Важен интервал sync

Проект ловит сильный ранний сигнал только если успевает увидеть пост в окне первых `8 часов`.

Поэтому:

- слишком редкий sync может пропускать нужные посты
- слишком частый sync может сильнее упираться в Telegram rate limits

### 4. Сейчас главный сигнал — просмотры

Проект сохраняет также:

- `forwards`
- `replies_count`
- `reactions_total`

Но текущий alert строится в первую очередь на `views` против медианы канала.

То есть сейчас это именно детектор сильного раннего охвата, а не сложная модель “хайповости”.
