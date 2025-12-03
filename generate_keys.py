#!/usr/bin/env python3
"""Генератор ключей для VidCourse."""
import secrets
import os

def generate_flask_secret_key():
    """Генерирует FLASK_SECRET_KEY."""
    return secrets.token_hex(32)

def check_env_vars():
    """Проверяет наличие необходимых переменных окружения."""
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET',
        'GOOGLE_REDIRECT_URI',
        'FLASK_SECRET_KEY',
        'FLASK_ENV'
    ]
    
    print("🔍 Проверка переменных окружения:\n")
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Скрываем секретные значения
            if 'SECRET' in var or 'CLIENT_SECRET' in var:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: НЕ НАЙДЕНА")
            missing.append(var)
    
    print("\n" + "="*60)
    
    if missing:
        print(f"\n⚠️  Отсутствуют переменные: {', '.join(missing)}")
        print("\n📋 Для Vercel добавьте следующие переменные:\n")
        for var in missing:
            if var == 'FLASK_SECRET_KEY':
                print(f"{var}={generate_flask_secret_key()}")
            elif var == 'GOOGLE_REDIRECT_URI':
                print(f"{var}=https://vidcourse-lesson-manager.vercel.app/auth/callback")
            elif var == 'FLASK_ENV':
                print(f"{var}=production")
            else:
                print(f"{var}=ваше_значение")
        return False
    else:
        print("\n✅ Все необходимые переменные окружения настроены!")
        return True

if __name__ == '__main__':
    print("🔑 VidCourse - Генератор ключей и проверка конфигурации\n")
    print("="*60)
    
    # Генерируем новый ключ
    new_key = generate_flask_secret_key()
    print(f"\n🔐 Сгенерированный FLASK_SECRET_KEY:\n{new_key}\n")
    print("="*60)
    
    # Проверяем переменные окружения
    check_env_vars()
    
    print("\n" + "="*60)
    print("\n💡 Инструкция:")
    print("1. Скопируйте FLASK_SECRET_KEY выше")
    print("2. Добавьте все переменные в Vercel Dashboard")
    print("3. Пересоберите проект в Vercel")
    print("\n📖 Подробная инструкция: VERCEL_OAUTH_SETUP.md")