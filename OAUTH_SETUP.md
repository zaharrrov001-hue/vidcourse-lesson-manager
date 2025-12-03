# Настройка Google OAuth для VidCourse

## Шаг 1: Создание OAuth 2.0 Credentials в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите **Google Drive API** и **Google+ API** (или People API)
4. Перейдите в **APIs & Services** → **Credentials**
5. Нажмите **Create Credentials** → **OAuth client ID**
6. Если впервые, настройте **OAuth consent screen**:
   - Выберите **External** (для тестирования)
   - Заполните обязательные поля (App name, User support email, Developer contact)
   - Добавьте scopes:
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
     - `https://www.googleapis.com/auth/drive.readonly`
   - Добавьте тестовых пользователей (если нужно)
7. Создайте **OAuth 2.0 Client ID**:
   - Application type: **Web application**
   - Name: VidCourse Lesson Manager
   - Authorized redirect URIs:
     - `http://localhost:8080/auth/callback` (для локальной разработки)
     - `https://yourdomain.com/auth/callback` (для production)
8. Скопируйте **Client ID** и **Client Secret**

## Шаг 2: Настройка .env файла

Добавьте в ваш `.env` файл:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/callback

# Flask Secret Key (для сессий)
FLASK_SECRET_KEY=your-random-secret-key-here

# GetCourse API (пользователь введет через интерфейс, но можно задать по умолчанию)
GETCOURSE_API_KEY=yezZCp4OLvY9DGQP192xGDulkfwMACJ5q27lTAXqEiBbgpNtmBrvfbSgionbcEiyX6OvRcQGbONFyYfsJOsFjIRdzjSBXbTTpSL0x3MpoHLXBX6OOBVBdZbOSneZJ8Hw
GETCOURSE_ACCOUNT=riprokurs
```

## Шаг 3: Запуск приложения

```bash
python3 web_app.py
```

## Шаг 4: Использование

1. Откройте http://localhost:8080
2. Нажмите **"Войти через Google"**
3. Выберите свой Google аккаунт
4. Разрешите доступ к:
   - Email адресу
   - Профилю
   - Google Drive (только чтение)
5. После входа настройте:
   - GetCourse API Key
   - GetCourse Account
   - Google Drive Folder ID
6. Нажмите **"Сохранить настройки"**
7. Теперь можете загружать и обрабатывать уроки!

## Важные замечания

- **Redirect URI** должен точно совпадать с тем, что указано в Google Cloud Console
- Для production измените `GOOGLE_REDIRECT_URI` на ваш домен
- `FLASK_SECRET_KEY` должен быть случайной строкой (используйте `openssl rand -hex 32`)
- Данные пользователей сохраняются в `users.json` (в production используйте базу данных)

## Troubleshooting

### Ошибка "redirect_uri_mismatch"
- Убедитесь, что redirect URI в `.env` точно совпадает с тем, что в Google Cloud Console
- Проверьте, что нет лишних пробелов или символов

### Ошибка "access_denied"
- Проверьте, что все необходимые scopes добавлены в OAuth consent screen
- Убедитесь, что приложение опубликовано или вы добавлены как тестовый пользователь

### Ошибка "invalid_client"
- Проверьте правильность Client ID и Client Secret в `.env`