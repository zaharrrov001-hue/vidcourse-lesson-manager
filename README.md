# VidCourse Lesson Manager

A program to fetch lessons from Google Drive, process/edit them, and send them to GetCourse via API.

## Features

- 📥 Fetch lessons from Google Drive
- ✏️ Process and edit lesson content
- 🚀 Send lessons to GetCourse via API
- 🔐 Google OAuth authentication
- 🌐 Web interface with shadcn-ui style
- 🔧 Configurable and extensible

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google OAuth (see `OAUTH_SETUP.md`)

3. Configure `.env` file:
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/callback
FLASK_SECRET_KEY=your-secret-key
```

4. Run the web application:
```bash
python web_app.py
```

5. Open http://localhost:8080 and login with Google

## Documentation

- `QUICK_START.md` - Quick start guide
- `OAUTH_SETUP.md` - Google OAuth setup instructions
- `SETUP.md` - Detailed setup instructions

## Project Structure

```
getcurs/
├── web_app.py              # Web application with OAuth
├── main.py                 # CLI entry point
├── auth.py                 # Authentication module
├── config.py              # Configuration management
├── google_drive.py        # Google Drive integration
├── getcourse_api.py       # GetCourse API client
├── lesson_processor.py    # Lesson processing/editing
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## License

MIT