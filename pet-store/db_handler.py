from pymongo import MongoClient
import os
from typing import Optional, List, Dict

class DatabaseHandler:
    """Handler for MongoDB connection and operations"""
    
    def __init__(self):
        
        mongo_host = os.environ.get('MONGO_HOST', 'mongodb')
        mongo_port = int(os.environ.get('MONGO_PORT', 27017))
        self.store_id = os.environ.get('STORE_ID', '1')
        
        # Connect to MongoDB
        self.client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/')
        self.db = self.client['pet_store_db']
        
        
        self.pet_types_collection = self.db[f'pet_types_store{self.store_id}']
        self.pets_collection = self.db[f'pets_store{self.store_id}']
        
        
        self.metadata_collection = self.db['id_metadata']
        
        print(f"Connected to MongoDB for store {self.store_id}")
    
    def get_next_id(self) -> tuple:
        """
        Get next available ID for pet-type.
        IMPORTANT: Never reuse IDs, even after deletion!
        """
        metadata_key = f'max_pet_type_id_store{self.store_id}'
        
        
        metadata = self.metadata_collection.find_one({'_id': metadata_key})
        
        if metadata and 'max_id' in metadata:
            
            next_id = metadata['max_id'] + 1
        else:
            
            max_doc = self.pet_types_collection.find_one(
                sort=[("_numeric_id", -1)]
            )
            
            if max_doc and '_numeric_id' in max_doc:
                next_id = max_doc['_numeric_id'] + 1
            else:
                next_id = 1
        
       
        self.metadata_collection.update_one(
            {'_id': metadata_key},
            {'$set': {'max_id': next_id}},
            upsert=True
        )
        
        return str(next_id), next_id
    
    
    
    def create_pet_type(self, pet_type_data: dict) -> dict:
        """Create a new pet-type in the database"""
        id_str, numeric_id = self.get_next_id()
        
        doc = {
            '_id': id_str,
            '_numeric_id': numeric_id,
            'id': id_str,
            'type': pet_type_data['type'],
            'family': pet_type_data['family'],
            'genus': pet_type_data['genus'],
            'attributes': pet_type_data['attributes'],
            'lifespan': pet_type_data['lifespan'],
            'pets': []
        }
        
        self.pet_types_collection.insert_one(doc)
        
        
        result = dict(doc)
        result.pop('_id', None)
        result.pop('_numeric_id', None)
        return result
    
    def get_all_pet_types(self, filters: dict = None) -> List[dict]:
        """Get all pet-types, optionally filtered"""
        query = {}
        
        if filters:
           
            for key, value in filters.items():
                if key == 'hasAttribute':
                    
                    query['attributes'] = {'$elemMatch': {'$regex': f'^{value}$', '$options': 'i'}}
                elif key == 'lifespan':
                   
                    try:
                        query[key] = int(value)
                    except:
                        pass
                else:
                    
                    query[key] = {'$regex': f'^{value}$', '$options': 'i'}
        
        results = []
        for doc in self.pet_types_collection.find(query):
            result = dict(doc)
            result.pop('_id', None)
            result.pop('_numeric_id', None)
            results.append(result)
        
        return results
    
    def get_pet_type_by_id(self, pet_type_id: str) -> Optional[dict]:
        """Get a specific pet-type by ID"""
        doc = self.pet_types_collection.find_one({'_id': pet_type_id})
        
        if doc:
            result = dict(doc)
            result.pop('_id', None)
            result.pop('_numeric_id', None)
            return result
        
        return None
    
    def delete_pet_type(self, pet_type_id: str) -> bool:
        """Delete a pet-type by ID"""
        
        result = self.pet_types_collection.delete_one({'_id': pet_type_id})
        return result.deleted_count > 0
    
    def pet_type_exists(self, pet_type_name: str) -> bool:
        """Check if a pet-type with this name already exists"""
        count = self.pet_types_collection.count_documents(
            {'type': {'$regex': f'^{pet_type_name}$', '$options': 'i'}}
        )
        return count > 0
    
    
    
    def create_pet(self, pet_type_id: str, pet_data: dict) -> bool:
        """Add a pet to a pet-type"""
        # First add to pets collection
        pet_doc = {
            '_id': f"{pet_type_id}_{pet_data['name']}",
            'pet_type_id': pet_type_id,
            'name': pet_data['name'],
            'birthdate': pet_data['birthdate'],
            'picture': pet_data['picture']
        }
        
        self.pets_collection.insert_one(pet_doc)
        
        
        self.pet_types_collection.update_one(
            {'_id': pet_type_id},
            {'$push': {'pets': pet_data['name']}}
        )
        
        return True
    
    def get_pets_by_type(self, pet_type_id: str, filters: dict = None) -> List[dict]:
        """Get all pets of a specific pet-type"""
        query = {'pet_type_id': pet_type_id}
        
        results = []
        for doc in self.pets_collection.find(query):
            pet = {
                'name': doc['name'],
                'birthdate': doc['birthdate'],
                'picture': doc['picture']
            }
            
            
            if filters:
                birthdate_gt = filters.get('birthdateGT')
                birthdate_lt = filters.get('birthdateLT')
                
                if pet['birthdate'] == "NA":
                    
                    if birthdate_gt or birthdate_lt:
                        continue
                else:
                    
                    from datetime import datetime
                    try:
                        pet_date = datetime.strptime(pet['birthdate'], '%d-%m-%Y')
                        
                        if birthdate_gt:
                            try:
                                gt_date = datetime.strptime(birthdate_gt, '%d-%m-%Y')
                                if pet_date <= gt_date:
                                    continue
                            except:
                                pass
                        
                        if birthdate_lt:
                            try:
                                lt_date = datetime.strptime(birthdate_lt, '%d-%m-%Y')
                                if pet_date >= lt_date:
                                    continue
                            except:
                                pass
                    except:
                        pass
            
            results.append(pet)
        
        return results
    
    def get_pet(self, pet_type_id: str, pet_name: str) -> Optional[dict]:
        """Get a specific pet by name (case-insensitive)"""
        
        for doc in self.pets_collection.find({'pet_type_id': pet_type_id}):
            if doc['name'].lower() == pet_name.lower():
                return {
                    'name': doc['name'],
                    'birthdate': doc['birthdate'],
                    'picture': doc['picture']
                }
        
        return None
    
    def update_pet(self, pet_type_id: str, pet_name: str, pet_data: dict) -> bool:
        """Update a pet's information"""
        # Find the pet name 
        actual_name = None
        for doc in self.pets_collection.find({'pet_type_id': pet_type_id}):
            if doc['name'].lower() == pet_name.lower():
                actual_name = doc['name']
                break
        
        if not actual_name:
            return False
        
        # Update the pet document
        result = self.pets_collection.update_one(
            {'_id': f"{pet_type_id}_{actual_name}"},
            {'$set': {
                'birthdate': pet_data['birthdate'],
                'picture': pet_data['picture']
            }}
        )
        
        return result.modified_count > 0 or result.matched_count > 0
    
    def delete_pet(self, pet_type_id: str, pet_name: str) -> bool:
        """Delete a pet"""
        # Find the pet name 
        actual_name = None
        for doc in self.pets_collection.find({'pet_type_id': pet_type_id}):
            if doc['name'].lower() == pet_name.lower():
                actual_name = doc['name']
                break
        
        if not actual_name:
            return False
        
        # Delete from pets collection
        self.pets_collection.delete_one({'_id': f"{pet_type_id}_{actual_name}"})
        
        
        self.pet_types_collection.update_one(
            {'_id': pet_type_id},
            {'$pull': {'pets': actual_name}}
        )
        
        return True
    
    def pet_exists(self, pet_type_id: str, pet_name: str) -> bool:
        """Check if a pet with this name exists in this pet-type"""
        for doc in self.pets_collection.find({'pet_type_id': pet_type_id}):
            if doc['name'].lower() == pet_name.lower():
                return True
        return False

# Global database handler instance
db = None

def init_db():
    """Initialize the database connection"""
    global db
    if db is None:
        db = DatabaseHandler()
    return db

def get_db():
    """Get the database handler instance"""
    global db
    if db is None:
        db = init_db()
    return db
