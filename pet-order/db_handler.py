from pymongo import MongoClient
import os
from datetime import datetime

class DatabaseHandler:
    """Handler for MongoDB connection and operations for pet-order service"""
    
    def __init__(self):
        # Get MongoDB connection details from environment
        mongo_host = os.environ.get('MONGO_HOST', 'mongodb-order')
        mongo_port = int(os.environ.get('MONGO_PORT', 27017))
        
        # Connect to MongoDB
        self.client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/')
        self.db = self.client['pet_store_db']
        
        # Shared transactions collection 
        self.transactions_collection = self.db['transactions']
        
        print("Pet-Order: Connected to MongoDB")
    
    def get_next_purchase_id(self) -> str:
        """Get next available purchase ID"""
        # Find the maximum purchase_id
        max_doc = self.transactions_collection.find_one(
            sort=[("_numeric_id", -1)]
        )
        
        if max_doc and '_numeric_id' in max_doc:
            next_id = max_doc['_numeric_id'] + 1
        else:
            next_id = 1
        
        return str(next_id), next_id
    
    def create_transaction(self, transaction_data: dict) -> str:
        """Create a new transaction"""
        purchase_id_str, numeric_id = self.get_next_purchase_id()
        
        doc = {
            '_id': purchase_id_str,
            '_numeric_id': numeric_id,
            'purchase-id': purchase_id_str,
            'purchaser': transaction_data['purchaser'],
            'pet-type': transaction_data['pet-type'],
            'store': transaction_data['store'],
            'pet-name': transaction_data['pet-name'],
            'timestamp': datetime.utcnow()
        }
        
        self.transactions_collection.insert_one(doc)
        
        return purchase_id_str
    
    def get_all_transactions(self, filters: dict = None) -> list:
        """Get all transactions, optionally filtered"""
        query = {}
        
        if filters:
            for key, value in filters.items():
                if key == 'store':
                    
                    try:
                        query['store'] = int(value)
                    except:
                        query['store'] = value
                elif key == 'pet-type':
                   
                    query['pet-type'] = {'$regex': f'^{value}$', '$options': 'i'}
                elif key == 'purchase-id':
                    query['purchase-id'] = value
                elif key == 'purchaser':
                    
                    query['purchaser'] = {'$regex': f'^{value}$', '$options': 'i'}
        
        results = []
        for doc in self.transactions_collection.find(query).sort('_numeric_id', 1):
            
            result = {
                'purchase-id': doc['purchase-id'],
                'purchaser': doc['purchaser'],
                'pet-type': doc['pet-type'],
                'store': doc['store']
            }
            results.append(result)
        
        return results



_db = None

def get_db():
    """Get the database handler instance"""
    global _db
    if _db is None:
        _db = DatabaseHandler()
    return _db
