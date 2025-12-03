# Настройка VidCourse Lesson Manager

## Быстрая настройка

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка Google Drive API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Drive API
4. Создайте OAuth 2.0 credentials (Desktop app)
5. Скачайте credentials и сохраните как `credentials.json` в корне проекта

### 3. Настройка GetCourse API

Ваши данные из URL `https://riprokurs.getcourse.ru/teach/control/stream/view/id/934935666`:

- **Аккаунт**: `riprokurs`
- **Stream ID**: `934935666`
- **API ключ**: `yezZCp4OLvY9DGQP192xGDulkfwMACJ5q27lTAXqEiBbgpNtmBrvfbSgionbcEiyX6OvRcQGbONFyYfsJOsFjIRdzjSBXbTTpSL0x3MpoHLXBX6OOBVBdZbOSneZJ8Hw`

### 4. Создание файла .env

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json

# GetCourse API Configuration
GETCOURSE_API_KEY=yezZCp4OLvY9DGQP192xGDulkfwMACJ5q27lTAXqEiBbgpNtmBrvfbSgionbcEiyX6OvRcQGbONFyYfsJOsFjIRdzjSBXbTTpSL0x3MpoHLXBX6OOBVBdZbOSneZJ8Hw
GETCOURSE_API_URL=https://api.getcourse.ru
GETCOURSE_ACCOUNT=riprokurs
```

**Важно**: Замените `your_google_drive_folder_id_here` на ID папки в Google Drive, где хранятся ваши уроки.

### 5. Как найти ID папки Google Drive

1. Откройте папку в Google Drive
2. Скопируйте URL из адресной строки
3. ID папки находится в URL после `/folders/`
   - Например: `https://drive.google.com/drive/folders/1ABC123xyz...`
   - ID: `1ABC123xyz...`

## Использование

### Просмотр доступных уроков
```bash
python main.py --list
```

### Обработка всех уроков и отправка в GetCourse
```bash
python main.py --process-all --stream-id 934935666
```

### Обработка конкретного урока
```bash
python main.py --lesson-id "google_drive_file_id" --stream-id 934935666
```

### Обработка без создания в GetCourse (только подготовка)
```bash
python main.py --process-all --no-create
```

## Структура проекта

```
getcurs/
├── main.py                 # Главная точка входа
├── config.py              # Управление конфигурацией
├── google_drive.py        # Интеграция с Google Drive
├── getcourse_api.py       # Клиент API GetCourse
├── lesson_processor.py    # Обработка и редактирование уроков
├── utils.py               # Вспомогательные функции
├── requirements.txt       # Зависимости Python
├── README.md              # Документация
└── SETUP.md               # Инструкция по настройке
```

## Примечания

- При первом запуске программа откроет браузер для авторизации Google Drive
- Токен авторизации сохранится в `token.json` для последующих запусков
- Убедитесь, что у вас есть доступ к API GetCourse (требуется платный тариф)