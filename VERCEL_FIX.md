# Исправление ошибки на Vercel

## Проблема
Сайт на Vercel выдает ошибку 500: `FUNCTION_INVOCATION_FAILED`

## Решение

### 1. Обновить переменные окружения в Vercel

В настройках проекта Vercel (Settings → Environment Variables) добавьте:

```env
GOOGLE_CLIENT_ID=ваш_client_id
GOOGLE_CLIENT_SECRET=ваш_client_secret
GOOGLE_REDIRECT_URI=https://vidcourse-lesson-manager.vercel.app/auth/callback
FLASK_SECRET_KEY=сгенерируйте-случайную-строку-минимум-32-символа
FLASK_ENV=production
VERCEL=1
```

### 2. Проверить логи

1. Откройте Vercel Dashboard
2. Перейдите в ваш проект
3. Откройте вкладку "Functions" или "Logs"
4. Проверьте ошибки в логах

### 3. Возможные проблемы

#### Проблема: Отсутствуют переменные окружения
**Решение:** Добавьте все необходимые переменные в Vercel Settings

#### Проблема: Ошибка импорта модулей
**Решение:** Убедитесь, что все файлы загружены на GitHub и `requirements.txt` содержит все зависимости

#### Проблема: Сессии не работают
**Решение:** На Vercel сессии хранятся в памяти. Для production используйте:
- Vercel KV (Redis) для сессий
- База данных для пользователей (Vercel Postgres, MongoDB Atlas)

### 4. Пересобрать проект

После обновления переменных окружения:
1. Перейдите в Vercel Dashboard
2. Откройте ваш проект
3. Нажмите "Redeploy" или дождитесь автоматического деплоя после push в GitHub

### 5. Проверить Google OAuth

Убедитесь, что в Google Cloud Console добавлен redirect URI:
- `https://vidcourse-lesson-manager.vercel.app/auth/callback`

## Быстрая проверка

1. ✅ Все файлы загружены на GitHub
2. ✅ `vercel.json` настроен правильно
3. ✅ `api/index.py` существует и правильно импортирует app
4. ✅ Все переменные окружения добавлены в Vercel
5. ✅ Google OAuth redirect URI настроен
6. ✅ Проект пересобран после изменений

## Если проблема сохраняется

1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что все зависимости в `requirements.txt`
3. Проверьте, что Flask app правильно экспортируется в `api/index.py`
4. Рассмотрите использование базы данных вместо JSON файла для пользователей