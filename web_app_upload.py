"""Простая версия VidCourse - загрузка файлов напрямую, без Google Drive API."""
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import secrets
from werkzeug.utils import secure_filename
from typing import Dict
from getcourse_api import GetCourseAPI

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Настройки загрузки
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'md',
    'jpg', 'jpeg', 'png', 'gif', 'webp',
    'mp4', 'avi', 'mov', 'mkv',
    'html', 'htm'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Создаем папку для загрузок
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Проверка расширения файла."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_file_content(filepath: str) -> str:
    """Читает содержимое файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return f"[Binary file: {os.path.basename(filepath)}]"


def process_file_content(content: str, filename: str) -> Dict:
    """Обрабатывает содержимое файла."""
    # Извлекаем заголовок
    title = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Пытаемся найти заголовок в содержимом
    lines = content.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) < 100 and line[0].isupper():
            title = line
            break
    
    # Описание - первые 200 символов
    description = content[:200].strip().replace('\n', ' ') if content else f"Lesson from {filename}"
    if len(description) > 200:
        description = description[:200] + "..."
    
    # Форматируем контент в HTML
    if content.strip():
        # Простое форматирование
        html_content = f"""
        <div class="lesson-content">
            <pre style="white-space: pre-wrap; font-family: Arial, sans-serif; line-height: 1.6;">
{content}
            </pre>
        </div>
        """
    else:
        html_content = f"<p>File: {filename}</p>"
    
    return {
        'title': title,
        'description': description,
        'content': html_content
    }


# HTML Template
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VidCourse - Простая загрузка</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="min-h-screen">
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 py-4">
                <h1 class="text-2xl font-bold text-gray-900">VidCourse Lesson Manager</h1>
                <p class="text-sm text-gray-600 mt-1">Простая загрузка файлов - без Google Drive API</p>
            </div>
        </header>

        <div class="max-w-7xl mx-auto px-4 py-8">
            <!-- Upload Section -->
            <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Загрузить файлы</h2>
                
                <form id="uploadForm" enctype="multipart/form-data" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Выберите файлы (текст, изображения, видео)
                        </label>
                        <input type="file" id="fileInput" multiple 
                               accept=".txt,.pdf,.doc,.docx,.md,.jpg,.jpeg,.png,.gif,.webp,.mp4,.avi,.mov,.mkv,.html,.htm"
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                        <p class="text-xs text-gray-500 mt-1">
                            Поддерживаются: текст, изображения, видео (до 500MB)
                        </p>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Stream ID</label>
                        <input type="text" id="streamId" value="934935666" 
                               class="w-full px-4 py-2 border border-gray-300 rounded-lg">
                    </div>
                    
                    <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                        Загрузить и отправить в GetCourse
                    </button>
                </form>
                
                <div id="uploadProgress" class="hidden mt-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div class="flex items-center gap-3">
                            <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                            <span class="text-blue-700">Загрузка и обработка...</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Results -->
            <div id="results" class="space-y-4"></div>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById('fileInput');
            const streamId = document.getElementById('streamId').value;
            const resultsDiv = document.getElementById('results');
            const progressDiv = document.getElementById('uploadProgress');
            
            if (fileInput.files.length === 0) {
                alert('Выберите файлы для загрузки');
                return;
            }
            
            progressDiv.classList.remove('hidden');
            resultsDiv.innerHTML = '';
            
            const formData = new FormData();
            for (let file of fileInput.files) {
                formData.append('files', file);
            }
            formData.append('stream_id', streamId);
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultsDiv.innerHTML = `
                        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                            <h3 class="font-semibold text-green-800 mb-2">✅ Успешно обработано!</h3>
                            <p class="text-green-700">Обработано файлов: ${data.processed}</p>
                            ${data.errors && data.errors.length > 0 ? 
                                '<p class="text-red-600 mt-2">Ошибки: ' + data.errors.join(', ') + '</p>' : ''}
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `
                        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                            <h3 class="font-semibold text-red-800 mb-2">❌ Ошибка</h3>
                            <p class="text-red-700">${data.error || 'Неизвестная ошибка'}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                        <h3 class="font-semibold text-red-800 mb-2">❌ Ошибка</h3>
                        <p class="text-red-700">${error.message}</p>
                    </div>
                `;
            } finally {
                progressDiv.classList.add('hidden');
                fileInput.value = '';
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Главная страница."""
    return render_template_string(MAIN_TEMPLATE)


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Загрузка и обработка файлов."""
    try:
        # Проверяем GetCourse API
        getcourse_api_key = os.getenv('GETCOURSE_API_KEY')
        getcourse_account = os.getenv('GETCOURSE_ACCOUNT')
        
        if not getcourse_api_key or not getcourse_account:
            return jsonify({
                'success': False,
                'error': 'GetCourse API не настроен. Установите GETCOURSE_API_KEY и GETCOURSE_ACCOUNT'
            }), 500
        
        getcourse_api = GetCourseAPI(api_key=getcourse_api_key, account=getcourse_account)
        stream_id = request.form.get('stream_id')
        
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'Файлы не выбраны'}), 400
        
        files = request.files.getlist('files')
        processed = 0
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
            
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: неподдерживаемый формат")
                continue
            
            try:
                # Сохраняем файл
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Читаем содержимое
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov', '.mkv')):
                    # Для изображений и видео - просто ссылка
                    content = f'<p><img src="/uploads/{filename}" alt="{filename}" style="max-width: 100%;"></p>'
                    if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                        content = f'<p><video controls style="max-width: 100%;"><source src="/uploads/{filename}"></video></p>'
                else:
                    # Для текстовых файлов - читаем содержимое
                    content = read_file_content(filepath)
                
                # Обрабатываем
                lesson_data = process_file_content(content, filename)
                
                # Отправляем в GetCourse
                result = getcourse_api.create_lesson(
                    title=lesson_data['title'],
                    description=lesson_data['description'],
                    content=lesson_data['content'],
                    stream_id=stream_id
                )
                
                processed += 1
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
                # Удаляем файл при ошибке
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return jsonify({
            'success': True,
            'processed': processed,
            'total': len(files),
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Отдача загруженных файлов."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    print("🚀 Starting VidCourse - Simple Upload Version")
    print("📝 Make sure to set:")
    print("   - GETCOURSE_API_KEY")
    print("   - GETCOURSE_ACCOUNT")
    print(f"\n🌐 Web interface: http://localhost:8080")
    print("📁 Upload folder: uploads/\n")
    
    port = 8080
    app.run(host='0.0.0.0', port=port, debug=True)