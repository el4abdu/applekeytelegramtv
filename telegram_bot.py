import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from key_generator import KeyGenerator
from config import TELEGRAM_TOKEN, DEFAULT_KEYS_TO_GENERATE, MAX_KEYS_PER_REQUEST

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.key_generator = KeyGenerator()
        self.updater = Updater(token=TELEGRAM_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        # Register command handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register all command handlers"""
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("getkey", self.get_key_command))
        self.dispatcher.add_handler(CommandHandler("getkeys", self.get_keys_command))
        self.dispatcher.add_handler(CommandHandler("stock", self.stock_command))
        self.dispatcher.add_handler(CommandHandler("generate", self.generate_command))
        self.dispatcher.add_handler(CommandHandler("startgen", self.start_gen_command))
        self.dispatcher.add_handler(CommandHandler("stopgen", self.stop_gen_command))
        
        # Add error handler
        self.dispatcher.add_error_handler(self.error_handler)
    
    def start_command(self, update: Update, context: CallbackContext):
        """Handle the /start command"""
        user = update.effective_user
        message = (
            f"Hello {user.first_name}! Welcome to the Apple TV Keys Bot.\n\n"
            "Use /help to see available commands."
        )
        update.message.reply_text(message)
    
    def help_command(self, update: Update, context: CallbackContext):
        """Handle the /help command"""
        help_text = (
            "Available commands:\n\n"
            "/getkey - Get a single Apple TV key\n"
            "/getkeys <count> - Get multiple keys (max 10)\n"
            "/stock - Check available keys in stock\n"
            "/generate <count> - Generate keys in background\n"
            "/startgen - Start automatic key generation\n"
            "/stopgen - Stop automatic key generation\n"
            "/help - Show this help message"
        )
        update.message.reply_text(help_text)
    
    def get_key_command(self, update: Update, context: CallbackContext):
        """Handle the /getkey command"""
        keys = self.key_generator.get_keys(count=1)
        
        if keys:
            update.message.reply_text(f"Here's your Apple TV key:\n\n`{keys[0]}`", parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text("No keys available. Use /generate to generate more keys.")
    
    def get_keys_command(self, update: Update, context: CallbackContext):
        """Handle the /getkeys command"""
        try:
            count = 1
            if context.args:
                count = int(context.args[0])
                count = min(count, 10)  # Limit to 10 keys at once
            
            keys = self.key_generator.get_keys(count=count)
            
            if keys:
                keys_text = "\n".join([f"`{key}`" for key in keys])
                update.message.reply_text(f"Here are your {len(keys)} Apple TV keys:\n\n{keys_text}", parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text("No keys available. Use /generate to generate more keys.")
        
        except ValueError:
            update.message.reply_text("Please provide a valid number.")
    
    def stock_command(self, update: Update, context: CallbackContext):
        """Handle the /stock command"""
        stats = self.key_generator.get_key_stats()
        
        status = "🟢 Active" if stats["is_generating"] else "🔴 Inactive"
        
        stock_text = (
            f"🔑 *Apple TV Keys Stock*\n\n"
            f"Available Keys: *{stats['unused']}*\n"
            f"Used Keys: *{stats['used']}*\n"
            f"Total Keys: *{stats['total']}*\n\n"
            f"Generation Status: *{status}*"
        )
        
        update.message.reply_text(stock_text, parse_mode=ParseMode.MARKDOWN)
    
    def generate_command(self, update: Update, context: CallbackContext):
        """Handle the /generate command"""
        try:
            count = DEFAULT_KEYS_TO_GENERATE
            if context.args:
                count = int(context.args[0])
                count = min(count, MAX_KEYS_PER_REQUEST)
            
            success, message = self.key_generator.start_background_generation(count=count)
            
            if success:
                update.message.reply_text(f"✅ {message}")
            else:
                update.message.reply_text(f"❌ {message}")
        
        except ValueError:
            update.message.reply_text("Please provide a valid number.")
    
    def start_gen_command(self, update: Update, context: CallbackContext):
        """Handle the /startgen command"""
        success, message = self.key_generator.schedule_generation()
        
        if success:
            update.message.reply_text(f"✅ {message}")
        else:
            update.message.reply_text(f"❌ {message}")
    
    def stop_gen_command(self, update: Update, context: CallbackContext):
        """Handle the /stopgen command"""
        success, message = self.key_generator.stop_scheduled_generation()
        
        if success:
            update.message.reply_text(f"✅ {message}")
        else:
            update.message.reply_text(f"❌ {message}")
    
    def error_handler(self, update: Update, context: CallbackContext):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update:
            update.message.reply_text("An error occurred while processing your request.")
    
    def start(self):
        """Start the bot"""
        self.updater.start_polling()
        logger.info("Bot started")
        
        # Start automatic key generation
        self.key_generator.schedule_generation()
    
    def stop(self):
        """Stop the bot"""
        self.updater.stop()
        self.key_generator.cleanup()
        logger.info("Bot stopped") 