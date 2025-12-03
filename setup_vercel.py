#!/usr/bin/env python3
"""Автоматическая настройка Vercel через API."""
import os
import sys
import secrets
import requests
import json

VERCEL_PROJECT_ID = "prj_7iRRCewLVR3MFUFKUI27EG6SNzvY"
VERCEL_API_URL = "https://api.vercel.com"

def generate_flask_secret_key():
    """Генерирует FLASK_SECRET_KEY."""
    return secrets.token_hex(32)

def get_vercel_token():
    """Получает Vercel API токен из переменной окружения."""
    token = os.getenv('VERCEL_TOKEN')
    if not token:
        print("❌ VERCEL_TOKEN не найден в переменных окружения")
        print("\n💡 Как получить токен:")
        print("1. Откройте https://vercel.com/account/tokens")
        print("2. Создайте новый токен")
        print("3. Экспортируйте: export VERCEL_TOKEN=your_token")
        print("4. Или запустите: VERCEL_TOKEN=your_token python3 setup_vercel.py")
        return None
    return token

def add_environment_variable(token, project_id, key, value, environments=None):
    """Добавляет переменную окружения в Vercel проект."""
    if environments is None:
        environments = ['production', 'preview', 'development']
    
    url = f"{VERCEL_API_URL}/v10/projects/{project_id}/env"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Добавляем для каждого окружения
    results = []
    for env in environments:
        payload = {
            "key": key,
            "value": value,
            "type": "encrypted",
            "target": [env]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                results.append(f"✅ {key} добавлена для {env}")
            elif response.status_code == 409:
                # Переменная уже существует, обновляем
                env_id = get_env_id(token, project_id, key, env)
                if env_id:
                    update_url = f"{VERCEL_API_URL}/v10/projects/{project_id}/env/{env_id}"
                    update_response = requests.patch(update_url, headers=headers, json={"value": value})
                    if update_response.status_code in [200, 201]:
                        results.append(f"✅ {key} обновлена для {env}")
                    else:
                        results.append(f"⚠️  {key} для {env}: {update_response.status_code} - {update_response.text}")
                else:
                    results.append(f"⚠️  {key} для {env}: уже существует, но не удалось обновить")
            else:
                results.append(f"❌ {key} для {env}: {response.status_code} - {response.text}")
        except Exception as e:
            results.append(f"❌ {key} для {env}: {str(e)}")
    
    return results

def get_env_id(token, project_id, key, target):
    """Получает ID существующей переменной окружения."""
    url = f"{VERCEL_API_URL}/v10/projects/{project_id}/env"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            envs = response.json().get('envs', [])
            for env in envs:
                if env.get('key') == key and target in env.get('target', []):
                    return env.get('id')
    except:
        pass
    return None

def setup_vercel():
    """Основная функция настройки."""
    print("🚀 Настройка Vercel через API\n")
    print("="*60)
    
    # Получаем токен
    token = get_vercel_token()
    if not token:
        return 1
    
    print(f"✅ Vercel токен найден\n")
    print(f"📦 Project ID: {VERCEL_PROJECT_ID}\n")
    print("="*60)
    
    # Генерируем FLASK_SECRET_KEY
    flask_secret_key = generate_flask_secret_key()
    print(f"\n🔐 Сгенерированный FLASK_SECRET_KEY: {flask_secret_key}\n")
    
    # Запрашиваем Google OAuth credentials
    print("📱 Google OAuth Credentials:")
    google_client_id = input("Введите GOOGLE_CLIENT_ID: ").strip()
    if not google_client_id:
        print("❌ GOOGLE_CLIENT_ID обязателен!")
        return 1
    
    google_client_secret = input("Введите GOOGLE_CLIENT_SECRET: ").strip()
    if not google_client_secret:
        print("❌ GOOGLE_CLIENT_SECRET обязателен!")
        return 1
    
    # Переменные для добавления
    env_vars = {
        "GOOGLE_CLIENT_ID": google_client_id,
        "GOOGLE_CLIENT_SECRET": google_client_secret,
        "GOOGLE_REDIRECT_URI": "https://vidcourse-lesson-manager.vercel.app/auth/callback",
        "FLASK_SECRET_KEY": flask_secret_key,
        "FLASK_ENV": "production",
        "VERCEL": "1"
    }
    
    print("\n" + "="*60)
    print("📝 Добавление переменных окружения...\n")
    
    all_results = []
    for key, value in env_vars.items():
        print(f"Добавление {key}...")
        results = add_environment_variable(token, VERCEL_PROJECT_ID, key, value)
        all_results.extend(results)
        for result in results:
            print(f"  {result}")
        print()
    
    print("="*60)
    print("\n📊 Итоги:\n")
    
    success_count = sum(1 for r in all_results if r.startswith("✅"))
    error_count = sum(1 for r in all_results if r.startswith("❌"))
    warning_count = sum(1 for r in all_results if r.startswith("⚠️"))
    
    print(f"✅ Успешно: {success_count}")
    if warning_count > 0:
        print(f"⚠️  Предупреждений: {warning_count}")
    if error_count > 0:
        print(f"❌ Ошибок: {error_count}")
    
    if error_count == 0:
        print("\n🎉 Настройка завершена!")
        print("\n💡 Следующие шаги:")
        print("1. Пересоберите проект в Vercel Dashboard")
        print("2. Убедитесь, что в Google Cloud Console добавлен redirect URI:")
        print("   https://vidcourse-lesson-manager.vercel.app/auth/callback")
        print("3. Проверьте работу сайта")
        return 0
    else:
        print("\n⚠️  Некоторые переменные не были добавлены. Проверьте ошибки выше.")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(setup_vercel())
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
