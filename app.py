import signal
import sys
import logging
from telegram_bot import TelegramBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown"""
    logger.info("Shutting down...")
    bot.stop()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start the bot
    bot = TelegramBot()
    
    logger.info("Starting Apple TV Keys Telegram Bot...")
    bot.start()
    
    # Keep the main thread alive
    try:
        signal.pause()
    except AttributeError:
        # signal.pause() is not available on Windows
        # Use a loop instead
        while True:
            pass 