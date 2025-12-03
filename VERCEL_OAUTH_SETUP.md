# Настройка Google OAuth на Vercel - Пошаговая инструкция

## Проблема
Ошибка: `{"error":"Google OAuth not configured"}`

Это означает, что переменные окружения для Google OAuth не настроены в Vercel.

## Решение

### Шаг 1: Получить Google OAuth Credentials

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите проект или создайте новый
3. Перейдите в **APIs & Services** → **Credentials**
4. Нажмите **Create Credentials** → **OAuth client ID**
5. Если впервые, настройте **OAuth consent screen**:
   - Выберите **External**
   - Заполните обязательные поля
   - Добавьте scopes:
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
     - `https://www.googleapis.com/auth/drive.readonly`
6. Создайте **OAuth 2.0 Client ID**:
   - Application type: **Web application**
   - Name: VidCourse Lesson Manager
   - **Authorized redirect URIs:**
     - `https://vidcourse-lesson-manager.vercel.app/auth/callback`
7. Скопируйте **Client ID** и **Client Secret**

### Шаг 2: Добавить переменные окружения в Vercel

1. Откройте [Vercel Dashboard](https://vercel.com/dashboard)
2. Выберите проект **vidcourse-lesson-manager**
3. Перейдите в **Settings** → **Environment Variables**
4. Добавьте следующие переменные:

#### Переменная 1: GOOGLE_CLIENT_ID
- **Key:** `GOOGLE_CLIENT_ID`
- **Value:** ваш Client ID (например: `123456789-abcdefghijklmnop.apps.googleusercontent.com`)
- **Environment:** Production, Preview, Development (выберите все)

#### Переменная 2: GOOGLE_CLIENT_SECRET
- **Key:** `GOOGLE_CLIENT_SECRET`
- **Value:** ваш Client Secret
- **Environment:** Production, Preview, Development (выберите все)

#### Переменная 3: GOOGLE_REDIRECT_URI
- **Key:** `GOOGLE_REDIRECT_URI`
- **Value:** `https://vidcourse-lesson-manager.vercel.app/auth/callback`
- **Environment:** Production, Preview, Development (выберите все)

#### Переменная 4: FLASK_SECRET_KEY
- **Key:** `FLASK_SECRET_KEY`
- **Value:** сгенерируйте случайную строку (минимум 32 символа)
  - Можно использовать: `openssl rand -hex 32` в терминале
  - Или онлайн генератор: https://randomkeygen.com/
- **Environment:** Production, Preview, Development (выберите все)

#### Переменная 5: FLASK_ENV
- **Key:** `FLASK_ENV`
- **Value:** `production`
- **Environment:** Production, Preview, Development (выберите все)

#### Переменная 6: VERCEL (опционально)
- **Key:** `VERCEL`
- **Value:** `1`
- **Environment:** Production, Preview, Development (выберите все)

### Шаг 3: Пересобрать проект

После добавления всех переменных:

1. В Vercel Dashboard откройте ваш проект
2. Перейдите на вкладку **Deployments**
3. Найдите последний deployment
4. Нажмите на три точки (⋮) → **Redeploy**
5. Или просто сделайте новый commit в GitHub - Vercel автоматически пересоберет проект

### Шаг 4: Проверить работу

1. Откройте https://vidcourse-lesson-manager.vercel.app/
2. Нажмите **"Войти через Google"**
3. Должна открыться страница авторизации Google
4. После авторизации вы будете перенаправлены обратно на сайт

## Проверка переменных окружения

Если ошибка сохраняется, проверьте:

1. ✅ Все переменные добавлены в Vercel
2. ✅ Переменные добавлены для всех окружений (Production, Preview, Development)
3. ✅ Значения переменных скопированы правильно (без лишних пробелов)
4. ✅ `GOOGLE_REDIRECT_URI` точно совпадает с тем, что в Google Cloud Console
5. ✅ Проект пересобран после добавления переменных

## Генерация FLASK_SECRET_KEY

В терминале выполните:
```bash
openssl rand -hex 32
```

Или используйте Python:
```python
import secrets
print(secrets.token_hex(32))
```

## Важно

- **Redirect URI** должен точно совпадать в Google Cloud Console и Vercel
- Используйте HTTPS для production (Vercel автоматически использует HTTPS)
- Не делитесь Client Secret публично
- После изменения переменных окружения нужно пересобрать проект

## Troubleshooting

### Ошибка "redirect_uri_mismatch"
- Проверьте, что redirect URI в Vercel точно совпадает с Google Cloud Console
- Убедитесь, что используется HTTPS

### Ошибка "invalid_client"
- Проверьте правильность Client ID и Client Secret
- Убедитесь, что нет лишних пробелов при копировании

### Ошибка все еще появляется
- Убедитесь, что проект пересобран после добавления переменных
- Проверьте логи в Vercel Dashboard → Functions → Logs
- Убедитесь, что переменные добавлены для всех окружений