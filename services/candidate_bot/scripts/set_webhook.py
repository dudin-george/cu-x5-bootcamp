#!/usr/bin/env python3
"""Set Telegram webhook for candidate bot.

Run this once after deployment to register webhook URL with Telegram.

Usage:
    python set_webhook.py

Environment variables required:
    TELEGRAM_BOT_TOKEN_CANDIDATE - Bot token from @BotFather
    WEBHOOK_SECRET_CANDIDATE - Secret for webhook URL
    WEBHOOK_DOMAIN - Domain (e.g., dev.x5teamintern.ru)
"""

import os
import sys
import requests


def main():
    # Get config from env
    token = os.getenv("TELEGRAM_BOT_TOKEN_CANDIDATE") or os.getenv("TELEGRAM_BOT_TOKEN")
    secret = os.getenv("WEBHOOK_SECRET_CANDIDATE") or os.getenv("WEBHOOK_SECRET")
    domain = os.getenv("WEBHOOK_DOMAIN", "dev.x5teamintern.ru")
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN_CANDIDATE not set")
        sys.exit(1)
    
    if not secret:
        print("❌ Error: WEBHOOK_SECRET_CANDIDATE not set")
        sys.exit(1)
    
    # Build webhook URL
    webhook_url = f"https://{domain}/tg/candidate/{secret}"
    
    print(f"Setting webhook to: {webhook_url}")
    
    # Call Telegram API
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    response = requests.post(api_url, json={
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": True,  # Ignore old messages
    })
    
    result = response.json()
    
    if result.get("ok"):
        print("✅ Webhook set successfully!")
        print(f"   URL: {webhook_url}")
    else:
        print(f"❌ Failed to set webhook: {result}")
        sys.exit(1)
    
    # Verify webhook
    info_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    info = requests.get(info_url).json()
    
    if info.get("ok"):
        webhook_info = info.get("result", {})
        print(f"\n📊 Webhook Info:")
        print(f"   URL: {webhook_info.get('url')}")
        print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
        print(f"   Last error: {webhook_info.get('last_error_message', 'None')}")


if __name__ == "__main__":
    main()

