import threading
import time
import logging
import schedule
from browser_manager import BrowserManager
from database import Database
from config import MAX_BROWSERS, DEFAULT_KEYS_TO_GENERATE, KEY_GENERATION_INTERVAL

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class KeyGenerator:
    def __init__(self):
        logger.info("Initializing KeyGenerator")
        self.browser_manager = BrowserManager(max_browsers=MAX_BROWSERS)
        self.db = Database()
        self.is_generating = False
        self.generation_thread = None
        self.scheduled_job = None
        
        # Start initial key generation
        logger.info("Starting initial key generation")
        self.start_background_generation(count=DEFAULT_KEYS_TO_GENERATE)
    
    def generate_keys(self, count=DEFAULT_KEYS_TO_GENERATE):
        """Generate Apple TV keys and store them in the database"""
        if self.is_generating:
            logger.info("Key generation already in progress")
            return False, "Key generation already in progress"
        
        self.is_generating = True
        keys_generated = []
        
        try:
            logger.info(f"Generating {count} keys")
            keys = self.browser_manager.generate_keys(count)
            
            for key in keys:
                logger.info(f"Generated key: {key}")
                if key and self.db.add_key(key):
                    keys_generated.append(key)
            
            logger.info(f"Successfully generated {len(keys_generated)} keys")
            return True, f"Generated {len(keys_generated)} keys"
        except Exception as e:
            logger.error(f"Error generating keys: {str(e)}")
            return False, f"Error generating keys: {str(e)}"
        finally:
            self.is_generating = False
    
    def start_background_generation(self, count=DEFAULT_KEYS_TO_GENERATE):
        """Start key generation in a background thread"""
        if self.is_generating:
            logger.info("Key generation already in progress")
            return False, "Key generation already in progress"
        
        def generate_in_background():
            logger.info(f"Background generation started for {count} keys")
            success, message = self.generate_keys(count)
            logger.info(f"Background generation completed: {message}")
            
            # Schedule the next generation if scheduled job is active
            if self.scheduled_job:
                logger.info("Scheduling next generation")
                self.schedule_generation()
        
        logger.info(f"Starting background generation of {count} keys")
        self.generation_thread = threading.Thread(target=generate_in_background)
        self.generation_thread.daemon = True
        self.generation_thread.start()
        
        return True, f"Started background generation of {count} keys"
    
    def schedule_generation(self, interval=KEY_GENERATION_INTERVAL, count=DEFAULT_KEYS_TO_GENERATE):
        """Schedule periodic key generation"""
        if self.scheduled_job:
            logger.info("Key generation already scheduled")
            return False, "Key generation already scheduled"
        
        def scheduled_task():
            if not self.is_generating:
                logger.info("Running scheduled key generation")
                self.start_background_generation(count)
        
        schedule.every(interval).seconds.do(scheduled_task)
        
        # Start the scheduler in a background thread
        def run_scheduler():
            logger.info("Scheduler thread started")
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        self.scheduled_job = True
        logger.info(f"Scheduled generation of {count} keys every {interval} seconds")
        return True, f"Scheduled generation of {count} keys every {interval} seconds"
    
    def stop_scheduled_generation(self):
        """Stop scheduled key generation"""
        if not self.scheduled_job:
            logger.info("No scheduled generation to stop")
            return False, "No scheduled generation to stop"
        
        schedule.clear()
        self.scheduled_job = None
        logger.info("Stopped scheduled key generation")
        return True, "Stopped scheduled key generation"
    
    def get_key_stats(self):
        """Get statistics about available keys"""
        unused_count = self.db.get_key_count(used=False)
        used_count = self.db.get_key_count(used=True)
        total_count = unused_count + used_count
        
        logger.info(f"Key stats: total={total_count}, unused={unused_count}, used={used_count}, is_generating={self.is_generating}")
        return {
            "total": total_count,
            "unused": unused_count,
            "used": used_count,
            "is_generating": self.is_generating
        }
    
    def get_keys(self, count=1, mark_as_used=True):
        """Get keys from the database"""
        keys = self.db.get_keys(count=count, used=False)
        
        if mark_as_used:
            for key_obj in keys:
                self.db.mark_key_as_used(key_obj["key"])
        
        return [key_obj["key"] for key_obj in keys]
    
    def cleanup(self):
        """Clean up resources"""
        if self.scheduled_job:
            self.stop_scheduled_generation()
        
        self.browser_manager.close_all()
        self.db.close() 