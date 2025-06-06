import pymongo
import time
from datetime import datetime
from config import MONGODB_URI, DB_NAME, KEYS_COLLECTION

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.keys_collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB and set up collections"""
        try:
            print("Connecting to MongoDB...")
            # Try to connect to MongoDB
            self.client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Check if the connection is working
            self.client.admin.command('ping')
            
            self.db = self.client[DB_NAME]
            self.keys_collection = self.db[KEYS_COLLECTION]
            
            # Create indexes if they don't exist
            self.keys_collection.create_index("key", unique=True)
            self.keys_collection.create_index("used")
            
            print("Successfully connected to MongoDB")
            return True
        except pymongo.errors.ServerSelectionTimeoutError:
            print("Could not connect to MongoDB. Make sure MongoDB is running.")
            print("Falling back to in-memory storage.")
            self.use_memory_storage()
            return False
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            print("Falling back to in-memory storage.")
            self.use_memory_storage()
            return False
    
    def use_memory_storage(self):
        """Use in-memory storage when MongoDB is not available"""
        print("Using in-memory storage for keys")
        self.in_memory = True
        self.memory_keys = []
    
    def add_key(self, key):
        """Add a new key to the database"""
        if hasattr(self, 'in_memory'):
            # Check if key already exists in memory
            if any(k.get('key') == key for k in self.memory_keys):
                return False
            
            self.memory_keys.append({
                "key": key,
                "created_at": datetime.now(),
                "used": False
            })
            return True
        else:
            try:
                self.keys_collection.insert_one({
                    "key": key,
                    "created_at": datetime.now(),
                    "used": False
                })
                return True
            except pymongo.errors.DuplicateKeyError:
                return False
            except Exception as e:
                print(f"Error adding key to database: {e}")
                return False
    
    def get_keys(self, count=1, used=False):
        """Get unused keys from the database"""
        if hasattr(self, 'in_memory'):
            keys = [k for k in self.memory_keys if k['used'] == used][:count]
            return keys
        else:
            try:
                keys = list(self.keys_collection.find({"used": used}).limit(count))
                return keys
            except Exception as e:
                print(f"Error getting keys from database: {e}")
                return []
    
    def mark_key_as_used(self, key):
        """Mark a key as used"""
        if hasattr(self, 'in_memory'):
            for k in self.memory_keys:
                if k['key'] == key:
                    k['used'] = True
                    k['used_at'] = datetime.now()
                    break
        else:
            try:
                self.keys_collection.update_one(
                    {"key": key},
                    {"$set": {"used": True, "used_at": datetime.now()}}
                )
            except Exception as e:
                print(f"Error marking key as used: {e}")
    
    def get_key_count(self, used=None):
        """Get count of keys in database"""
        if hasattr(self, 'in_memory'):
            if used is not None:
                return len([k for k in self.memory_keys if k['used'] == used])
            return len(self.memory_keys)
        else:
            try:
                query = {}
                if used is not None:
                    query["used"] = used
                return self.keys_collection.count_documents(query)
            except Exception as e:
                print(f"Error getting key count: {e}")
                return 0
    
    def close(self):
        """Close database connection"""
        if self.client and not hasattr(self, 'in_memory'):
            try:
                self.client.close()
            except:
                pass 