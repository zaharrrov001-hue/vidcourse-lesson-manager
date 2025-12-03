# Настройка Vercel через API

## Быстрый старт

### Вариант 1: Интерактивный (рекомендуется)

```bash
# 1. Получите Vercel API токен
# Откройте https://vercel.com/account/tokens
# Создайте новый токен и скопируйте его

# 2. Экспортируйте токен
export VERCEL_TOKEN=your_vercel_token_here

# 3. Запустите скрипт
python3 setup_vercel.py
```

Скрипт попросит ввести:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET

Остальные переменные будут настроены автоматически.

### Вариант 2: Полностью автоматический

```bash
# 1. Экспортируйте все необходимые переменные
export VERCEL_TOKEN=your_vercel_token_here
export GOOGLE_CLIENT_ID=your_google_client_id
export GOOGLE_CLIENT_SECRET=your_google_client_secret

# 2. Запустите автоматический скрипт
python3 setup_vercel_auto.py
```

## Что делает скрипт

1. ✅ Генерирует `FLASK_SECRET_KEY` (64 символа)
2. ✅ Добавляет все переменные окружения в Vercel:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI` (автоматически)
   - `FLASK_SECRET_KEY` (автоматически)
   - `FLASK_ENV=production`
   - `VERCEL=1`
3. ✅ Настраивает переменные для всех окружений (Production, Preview, Development)
4. ✅ Обновляет существующие переменные, если они уже есть

## Получение Vercel API токена

1. Откройте https://vercel.com/account/tokens
2. Нажмите "Create Token"
3. Введите название (например: "VidCourse Setup")
4. Выберите срок действия
5. Скопируйте токен

⚠️ **Важно:** Токен показывается только один раз! Сохраните его.

## Получение Google OAuth Credentials

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Перейдите в **APIs & Services** → **Credentials**
3. Создайте **OAuth 2.0 Client ID** (тип: Web application)
4. Добавьте redirect URI: `https://vidcourse-lesson-manager.vercel.app/auth/callback`
5. Скопируйте **Client ID** и **Client Secret**

## После настройки

1. Пересоберите проект в Vercel Dashboard:
   - Откройте проект → Deployments
   - Нажмите ⋮ → Redeploy

2. Проверьте работу:
   - Откройте https://vidcourse-lesson-manager.vercel.app/
   - Нажмите "Войти через Google"

## Troubleshooting

### Ошибка "VERCEL_TOKEN не найден"
- Убедитесь, что токен экспортирован: `echo $VERCEL_TOKEN`
- Или передайте напрямую: `VERCEL_TOKEN=token python3 setup_vercel.py`

### Ошибка "Google OAuth credentials не найдены"
- Для автоматического режима установите переменные:
  ```bash
  export GOOGLE_CLIENT_ID=your_id
  export GOOGLE_CLIENT_SECRET=your_secret
  ```
- Или используйте интерактивный режим: `python3 setup_vercel.py`

### Ошибка 401 Unauthorized
- Проверьте правильность Vercel токена
- Убедитесь, что токен не истек

### Ошибка 404 Not Found
- Проверьте Project ID в скрипте (должен быть: `prj_7iRRCewLVR3MFUFKUI27EG6SNzvY`)
- Убедитесь, что проект существует в вашем аккаунте

## Project ID

Текущий Project ID: `prj_7iRRCewLVR3MFUFKUI27EG6SNzvY`

Если нужно изменить, отредактируйте переменную `VERCEL_PROJECT_ID` в скриптах.