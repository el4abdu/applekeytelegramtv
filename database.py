import pymongo
from datetime import datetime
from config import MONGODB_URI, DB_NAME, KEYS_COLLECTION

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGODB_URI)
        self.db = self.client[DB_NAME]
        self.keys_collection = self.db[KEYS_COLLECTION]
        
        # Create indexes if they don't exist
        self.keys_collection.create_index("key", unique=True)
        self.keys_collection.create_index("used")
    
    def add_key(self, key):
        """Add a new key to the database"""
        try:
            self.keys_collection.insert_one({
                "key": key,
                "created_at": datetime.now(),
                "used": False
            })
            return True
        except pymongo.errors.DuplicateKeyError:
            return False
    
    def get_keys(self, count=1, used=False):
        """Get unused keys from the database"""
        keys = list(self.keys_collection.find({"used": used}).limit(count))
        return keys
    
    def mark_key_as_used(self, key):
        """Mark a key as used"""
        self.keys_collection.update_one(
            {"key": key},
            {"$set": {"used": True, "used_at": datetime.now()}}
        )
    
    def get_key_count(self, used=None):
        """Get count of keys in database"""
        query = {}
        if used is not None:
            query["used"] = used
        return self.keys_collection.count_documents(query)
    
    def close(self):
        """Close database connection"""
        self.client.close() 