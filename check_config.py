#!/usr/bin/env python3
"""Проверка конфигурации VidCourse."""
import os
import sys

def check_config():
    """Проверяет конфигурацию приложения."""
    print("🔍 Проверка конфигурации VidCourse\n")
    print("="*60)
    
    errors = []
    warnings = []
    
    # Проверка Google OAuth
    print("\n📱 Google OAuth:")
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    
    if google_client_id:
        print(f"  ✅ GOOGLE_CLIENT_ID: {google_client_id[:20]}...")
    else:
        print("  ❌ GOOGLE_CLIENT_ID: НЕ НАЙДЕН")
        errors.append("GOOGLE_CLIENT_ID не настроен")
    
    if google_client_secret:
        print(f"  ✅ GOOGLE_CLIENT_SECRET: {google_client_secret[:10]}...")
    else:
        print("  ❌ GOOGLE_CLIENT_SECRET: НЕ НАЙДЕН")
        errors.append("GOOGLE_CLIENT_SECRET не настроен")
    
    if google_redirect_uri:
        print(f"  ✅ GOOGLE_REDIRECT_URI: {google_redirect_uri}")
        if not google_redirect_uri.startswith('https://'):
            warnings.append("GOOGLE_REDIRECT_URI должен использовать HTTPS для production")
    else:
        print("  ⚠️  GOOGLE_REDIRECT_URI: не установлен (будет использован localhost)")
        warnings.append("GOOGLE_REDIRECT_URI не установлен")
    
    # Проверка Flask
    print("\n🔐 Flask:")
    flask_secret_key = os.getenv('FLASK_SECRET_KEY')
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    if flask_secret_key:
        if len(flask_secret_key) >= 32:
            print(f"  ✅ FLASK_SECRET_KEY: установлен ({len(flask_secret_key)} символов)")
        else:
            print(f"  ⚠️  FLASK_SECRET_KEY: слишком короткий ({len(flask_secret_key)} символов)")
            warnings.append("FLASK_SECRET_KEY должен быть минимум 32 символа")
    else:
        print("  ❌ FLASK_SECRET_KEY: НЕ НАЙДЕН")
        errors.append("FLASK_SECRET_KEY не настроен")
    
    print(f"  ✅ FLASK_ENV: {flask_env}")
    
    # Проверка Vercel
    print("\n☁️  Vercel:")
    vercel = os.getenv('VERCEL')
    if vercel:
        print(f"  ✅ VERCEL: {vercel}")
    else:
        print("  ℹ️  VERCEL: не установлен (не критично)")
    
    # Итоги
    print("\n" + "="*60)
    
    if errors:
        print(f"\n❌ Найдено ошибок: {len(errors)}")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print(f"\n⚠️  Предупреждений: {len(warnings)}")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors and not warnings:
        print("\n✅ Конфигурация в порядке!")
        return 0
    elif errors:
        print("\n💡 Решение:")
        print("   1. Откройте Vercel Dashboard → Settings → Environment Variables")
        print("   2. Добавьте недостающие переменные")
        print("   3. Пересоберите проект")
        print("\n📖 Подробная инструкция: VERCEL_OAUTH_SETUP.md")
        return 1
    else:
        return 0

if __name__ == '__main__':
    sys.exit(check_config())