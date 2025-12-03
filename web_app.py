"""Web interface for VidCourse Lesson Manager with Google OAuth authentication."""
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sys
import os
import json
from typing import Dict, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import requests

from auth import User, AuthManager
from getcourse_api import GetCourseAPI
from lesson_processor_v2 import LessonProcessor

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure session for Vercel (serverless)
# Use secure cookies and set proper domain
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Auth manager
auth_manager = AuthManager(app)

# OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive.readonly'
]


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return auth_manager.get_user(user_id)


def get_google_flow():
    """Create Google OAuth flow."""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/auth/callback')
    
    if not client_id or not client_secret:
        return None
    
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow


def get_user_drive_client(user):
    """Get Google Drive client for user."""
    creds_data = session.get('google_credentials')
    if not creds_data:
        return None
    
    creds = Credentials(
        token=creds_data['token'],
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data.get('client_secret'),
        scopes=creds_data['scopes']
    )
    
    # Refresh if needed
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            session['google_credentials'] = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None
    
    return build('drive', 'v3', credentials=creds)


class UserManager:
    """Manages user-specific operations."""
    
    def __init__(self, user):
        self.user = user
        self.drive_service = get_user_drive_client(user)
        
        if user.getcourse_api_key and user.getcourse_account:
            self.getcourse_api = GetCourseAPI(
                api_key=user.getcourse_api_key,
                account=user.getcourse_account
            )
        else:
            self.getcourse_api = None
        
        if self.drive_service:
            self.processor = LessonProcessor(self.drive_service)
        else:
            self.processor = None
    
    def list_lessons(self, folder_id=None):
        """List lessons from Google Drive."""
        if not self.drive_service:
            raise ValueError("Google Drive not connected")
        
        folder_id = folder_id or self.user.drive_folder_id
        if not folder_id:
            raise ValueError("Google Drive folder ID not set")
        
        files = []
        page_token = None
        
        while True:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.drive_service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)",
                pageToken=page_token
            ).execute()
            
            files.extend(results.get('files', []))
            page_token = results.get('nextPageToken')
            
            if not page_token:
                break
        
        return files
    
    def process_lesson(self, file_metadata, stream_id=None, course_id=None):
        """Process a lesson."""
        if not self.processor:
            raise ValueError("Lesson processor not available")
        
        lesson_data = self.processor.process_file(file_metadata)
        
        if self.getcourse_api:
            try:
                result = self.getcourse_api.create_lesson(
                    title=lesson_data['title'],
                    description=lesson_data['description'],
                    content=lesson_data['content'],
                    course_id=course_id,
                    stream_id=stream_id,
                )
                lesson_data['getcourse_id'] = result.get('lesson_id')
                lesson_data['getcourse_result'] = result
                lesson_data['success'] = True
            except Exception as e:
                lesson_data['getcourse_error'] = str(e)
                lesson_data['success'] = False
        else:
            lesson_data['success'] = False
            lesson_data['getcourse_error'] = 'GetCourse API not configured'
        
        return lesson_data


# HTML Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход - VidCourse</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">VidCourse</h1>
            <p class="text-gray-600">Управление уроками из Google Drive в GetCourse</p>
        </div>
        
        <div class="space-y-4">
            <a href="/auth/google" class="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-300 rounded-lg px-6 py-3 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
                <svg class="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Войти через Google
            </a>
        </div>
        
        <div class="mt-6 text-center text-sm text-gray-500">
            <p>Войдите через Google, чтобы начать работу</p>
        </div>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VidCourse Lesson Manager</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <h1 class="text-2xl font-bold text-gray-900">VidCourse</h1>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-sm text-gray-600">{{ user.name }}</span>
                    <img src="{{ user.picture or '/static/default-avatar.png' }}" alt="Avatar" class="w-8 h-8 rounded-full">
                    <a href="/logout" class="text-sm text-red-600 hover:text-red-700">Выйти</a>
                </div>
            </div>
        </header>

        <div class="max-w-7xl mx-auto px-4 py-8">
            <!-- Settings Card -->
            <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Настройки</h2>
                
                <div id="settingsForm" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">GetCourse API Key</label>
                        <input type="text" id="getcourseApiKey" value="{{ user.getcourse_api_key or '' }}" 
                               placeholder="Введите API ключ GetCourse"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">GetCourse Account</label>
                        <input type="text" id="getcourseAccount" value="{{ user.getcourse_account or '' }}" 
                               placeholder="riprokurs"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Google Drive Folder ID</label>
                        <input type="text" id="driveFolderId" value="{{ user.drive_folder_id or '' }}" 
                               placeholder="ID папки в Google Drive"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    </div>
                    
                    <button onclick="saveSettings()" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        Сохранить настройки
                    </button>
                </div>
            </div>

            <!-- Actions -->
            <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Действия</h2>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Stream ID</label>
                        <input type="text" id="streamId" value="934935666" 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    </div>
                    <div class="flex gap-4">
                        <button onclick="loadLessons()" class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors">
                            Загрузить уроки
                        </button>
                        <button onclick="processAll()" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                            Обработать все
                        </button>
                    </div>
                </div>
            </div>

            <!-- Lessons List -->
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <h2 class="text-xl font-semibold mb-4">Уроки из Google Drive</h2>
                <div id="loading" class="hidden text-center py-8">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p class="mt-4 text-gray-600">Загрузка...</p>
                </div>
                <div id="lessonsList" class="space-y-4"></div>
            </div>

            <!-- Results -->
            <div id="processResults" class="mt-6"></div>
        </div>
    </div>

    <script>
        async function saveSettings() {
            const data = {
                getcourse_api_key: document.getElementById('getcourseApiKey').value,
                getcourse_account: document.getElementById('getcourseAccount').value,
                drive_folder_id: document.getElementById('driveFolderId').value
            };
            
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                alert('Настройки сохранены!');
            } else {
                alert('Ошибка: ' + (result.error || 'Неизвестная ошибка'));
            }
        }
        
        async function loadLessons() {
            const loading = document.getElementById('loading');
            const list = document.getElementById('lessonsList');
            
            loading.classList.remove('hidden');
            list.innerHTML = '';
            
            try {
                const response = await fetch('/api/lessons');
                const data = await response.json();
                
                if (data.error) {
                    list.innerHTML = '<div class="text-red-600">' + data.error + '</div>';
                    return;
                }
                
                const lessons = data.lessons || [];
                if (lessons.length === 0) {
                    list.innerHTML = '<p class="text-gray-600">Уроки не найдены</p>';
                    return;
                }
                
                list.innerHTML = lessons.map(lesson => `
                    <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <h3 class="font-semibold text-lg mb-2">${lesson.name || 'Без названия'}</h3>
                                <p class="text-sm text-gray-600">ID: ${lesson.id}</p>
                                <p class="text-sm text-gray-600">Тип: ${lesson.mimeType || 'Unknown'}</p>
                            </div>
                            <button onclick="processLesson('${lesson.id}')" class="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                Обработать
                            </button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                list.innerHTML = '<div class="text-red-600">Ошибка: ' + error.message + '</div>';
            } finally {
                loading.classList.add('hidden');
            }
        }
        
        async function processLesson(lessonId) {
            const streamId = document.getElementById('streamId').value;
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lesson_id: lessonId, stream_id: streamId})
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Урок обработан успешно!');
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        }
        
        async function processAll() {
            if (!confirm('Обработать все уроки?')) return;
            
            const streamId = document.getElementById('streamId').value;
            const response = await fetch('/api/process-all', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({stream_id: streamId})
            });
            
            const data = await response.json();
            if (data.success) {
                alert(`Обработано ${data.processed} из ${data.total} уроков`);
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page."""
    if current_user.is_authenticated:
        return render_template_string(MAIN_TEMPLATE, user=current_user)
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/auth/google')
def auth_google():
    """Start Google OAuth flow."""
    flow = get_google_flow()
    if not flow:
        # Показываем более понятную ошибку
        missing = []
        if not os.getenv('GOOGLE_CLIENT_ID'):
            missing.append('GOOGLE_CLIENT_ID')
        if not os.getenv('GOOGLE_CLIENT_SECRET'):
            missing.append('GOOGLE_CLIENT_SECRET')
        
        error_msg = f'Google OAuth not configured. Missing: {", ".join(missing)}. Please add these environment variables in Vercel Settings.'
        return jsonify({'error': error_msg, 'missing_vars': missing}), 500
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback."""
    flow = get_google_flow()
    if not flow:
        return redirect(url_for('login'))
    
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Get user info
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    
    # Create or update user
    user = auth_manager.create_or_update_user(user_info, credentials)
    login_user(user, remember=True)
    
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/settings', methods=['POST'])
@login_required
def api_settings():
    """Update user settings."""
    data = request.json
    user = auth_manager.update_user_settings(
        current_user.id,
        getcourse_api_key=data.get('getcourse_api_key'),
        getcourse_account=data.get('getcourse_account'),
        drive_folder_id=data.get('drive_folder_id')
    )
    
    if user:
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to update settings'}), 500


@app.route('/api/lessons')
@login_required
def api_lessons():
    """List lessons from Google Drive."""
    try:
        manager = UserManager(current_user)
        lessons = manager.list_lessons()
        return jsonify({'lessons': lessons})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process', methods=['POST'])
@login_required
def api_process():
    """Process a single lesson."""
    try:
        data = request.json
        manager = UserManager(current_user)
        
        lessons = manager.list_lessons()
        lesson = next((l for l in lessons if l['id'] == data.get('lesson_id')), None)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        result = manager.process_lesson(
            lesson,
            stream_id=data.get('stream_id'),
            course_id=data.get('course_id')
        )
        
        return jsonify({
            'success': result.get('success', False),
            'title': result.get('title'),
            'error': result.get('getcourse_error')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-all', methods=['POST'])
@login_required
def api_process_all():
    """Process all lessons."""
    try:
        data = request.json
        manager = UserManager(current_user)
        
        lessons = manager.list_lessons()
        processed = 0
        errors = []
        
        for lesson in lessons:
            try:
                result = manager.process_lesson(
                    lesson,
                    stream_id=data.get('stream_id'),
                    course_id=data.get('course_id')
                )
                if result.get('success'):
                    processed += 1
                else:
                    errors.append(f"{lesson.get('name')}: {result.get('getcourse_error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"{lesson.get('name')}: {str(e)}")
        
        return jsonify({
            'success': True,
            'processed': processed,
            'total': len(lessons),
            'errors': errors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting VidCourse Lesson Manager with OAuth...")
    print("📝 Make sure to set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
    print(f"\n🌐 Web interface: http://localhost:8080")
    print("📖 Users will login through Google OAuth\n")
    
    port = 8080
    app.run(host='0.0.0.0', port=port, debug=True)