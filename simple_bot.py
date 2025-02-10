import logging
import requests
from telegram.ext import Updater, CommandHandler
import json

# Logging ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigürasyon
TOKEN = "8122795483:AAHlc9aAx6qJYFEaOnyUhAfTROomGPUnAws"
CHANNEL_ID = "-1002456190669"
CRYPTOPANIC_API_KEY = "dee2774f51374d4a39a1e5ae09e4cd8bfa34ebc4"
CHECK_INTERVAL = 900  # 15 dakika

def get_crypto_news():
    """CryptoPanic API'den haberleri al"""
    url = "https://cryptopanic.com/api/v1/posts/"
    params = {
        'auth_token': CRYPTOPANIC_API_KEY,
        'public': 'true',
        'kind': 'news',
        'filter': 'trending',
        'regions': 'en'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        logger.error(f"Haber alma hatası: {e}")
        return []

def format_message(news):
    """Haber mesajını formatla"""
    title = news.get('title', '')
    url = news.get('url', '')
    source = news.get('source', {}).get('title', 'Bilinmeyen Kaynak')
    
    return (
        f"📰 *{title}*\n\n"
        f"🔍 Kaynak: {source}\n\n"
        f"[Haberin Devamı]({url})"
    )

def send_news(context):
    """Haberleri gönder"""
    news_items = get_crypto_news()
    if not news_items:
        return
    
    for news in news_items[:3]:
        try:
            message = format_message(news)
            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            logger.info(f"Haber gönderildi: {news.get('title')}")
        except Exception as e:
            logger.error(f"Haber gönderme hatası: {e}")

def start(update, context):
    """Bot başlatma komutu"""
    update.message.reply_text('Bot aktif! 15 dakikada bir haberleri kontrol edeceğim.')

def main():
    """Bot'u başlat"""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    
    # Haber gönderme job'ını başlat
    updater.job_queue.run_repeating(send_news, interval=CHECK_INTERVAL, first=1)
    
    logger.info("Bot başlatılıyor...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
