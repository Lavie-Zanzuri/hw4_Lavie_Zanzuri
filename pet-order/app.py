from flask import Flask, jsonify, request
from config import PORT, HOST, OWNER_PASSWORD, PET_STORE1_URL, PET_STORE2_URL
from db_handler import get_db
import requests
import random
import os

app = Flask(__name__)
app.url_map.strict_slashes = False  

# Initialize database connection
db = None

@app.before_request
def before_request():
    """Initialize DB connection before first request"""
    global db
    if db is None:
        db = get_db()


def get_pet_types_from_store(store_num):
    """Get all pet-types from a specific store"""
    store_url = PET_STORE1_URL if store_num == 1 else PET_STORE2_URL
    
    try:
        response = requests.get(f"{store_url}/pet-types", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_pets_from_store(store_num, pet_type_id):
    """Get all pets of a specific pet-type from a store"""
    store_url = PET_STORE1_URL if store_num == 1 else PET_STORE2_URL
    
    try:
        response = requests.get(f"{store_url}/pet-types/{pet_type_id}/pets", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def delete_pet_from_store(store_num, pet_type_id, pet_name):
    """Delete a pet from a store after purchase"""
    store_url = PET_STORE1_URL if store_num == 1 else PET_STORE2_URL
    
    try:
        response = requests.delete(f"{store_url}/pet-types/{pet_type_id}/pets/{pet_name}", timeout=5)
        return response.status_code == 204
    except:
        return False


def find_pet_to_purchase(pet_type_name, store=None, pet_name=None):
    """
    Find a pet to purchase based on the request parameters.
    
    Returns: (store_num, pet_type_id, pet_name, pet_type_name) or None if not found
    """
    
    
    if store is not None and pet_name is not None:
        # Check if the specific pet exists in the specific store
        pet_types = get_pet_types_from_store(store)
        
        for pt in pet_types:
            if pt['type'].lower() == pet_type_name.lower():
                pets = get_pets_from_store(store, pt['id'])
                
                for pet in pets:
                    if pet['name'].lower() == pet_name.lower():
                        return (store, pt['id'], pet['name'], pt['type'])
        
        return None
    
    
    elif store is not None and pet_name is None:
        pet_types = get_pet_types_from_store(store)
        
        # Find matching pet-type in the store
        matching_pet_types = [pt for pt in pet_types if pt['type'].lower() == pet_type_name.lower()]
        
        if not matching_pet_types:
            return None
        
        pet_type = matching_pet_types[0]
        pets = get_pets_from_store(store, pet_type['id'])
        
        if not pets:
            return None
        
        # Choose random pet
        chosen_pet = random.choice(pets)
        return (store, pet_type['id'], chosen_pet['name'], pet_type['type'])
    
    
    elif store is None and pet_name is not None:
        # Try both stores
        for store_num in [1, 2]:
            pet_types = get_pet_types_from_store(store_num)
            
            for pt in pet_types:
                if pt['type'].lower() == pet_type_name.lower():
                    pets = get_pets_from_store(store_num, pt['id'])
                    
                    for pet in pets:
                        if pet['name'].lower() == pet_name.lower():
                            return (store_num, pt['id'], pet['name'], pt['type'])
        
        return None
    
    
    else:
        # Try both stores
        all_options = []
        
        for store_num in [1, 2]:
            pet_types = get_pet_types_from_store(store_num)
            
            for pt in pet_types:
                if pt['type'].lower() == pet_type_name.lower():
                    pets = get_pets_from_store(store_num, pt['id'])
                    
                    for pet in pets:
                        all_options.append((store_num, pt['id'], pet['name'], pt['type']))
        
        if not all_options:
            return None
        
        # Choose random option
        return random.choice(all_options)


@app.route('/purchases', methods=['POST'])
def create_purchase():
    """Handle POST /purchases endpoint"""
    
    # Check Content Type
    if 'application/json' not in request.headers.get('Content-Type', ''):
        return jsonify({"error": "Expected application/json media type"}), 415
    
    data = request.get_json()
    
    # Validate required fields
    if not data or 'purchaser' not in data or 'pet-type' not in data:
        return jsonify({"error": "Malformed data"}), 400
    
    purchaser = data['purchaser']
    pet_type = data['pet-type']
    store = data.get('store')
    pet_name = data.get('pet-name')
    
    # Validate store if provided
    if store is not None:
        if store not in [1, 2]:
            return jsonify({"error": "Malformed data"}), 400
    
    
    if pet_name is not None and store is None:
        return jsonify({"error": "Malformed data"}), 400
    
    # Find a pet to purchase
    result = find_pet_to_purchase(pet_type, store, pet_name)
    
    if result is None:
        return jsonify({"error": "No pet of this type is available"}), 400
    
    chosen_store, pet_type_id, chosen_pet_name, chosen_pet_type = result
    
    # Delete the pet from the store
    if not delete_pet_from_store(chosen_store, pet_type_id, chosen_pet_name):
        return jsonify({"error": "Failed to complete purchase"}), 500
    
    # Create transaction in database
    purchase_data = {
        'purchaser': purchaser,
        'pet-type': chosen_pet_type,
        'store': chosen_store,
        'pet-name': chosen_pet_name
    }
    
    purchase_id = db.create_transaction(purchase_data)
    
    # Return purchase details
    response = {
        'purchaser': purchaser,
        'pet-type': chosen_pet_type,
        'store': chosen_store,
        'pet-name': chosen_pet_name,
        'purchase-id': purchase_id
    }
    
    return jsonify(response), 201


@app.route('/transactions', methods=['GET'])
def get_transactions():
    """Handle GET /transactions endpoint (owner only)"""
    
    # Check authentication
    owner_pc = request.headers.get('OwnerPC')
    if owner_pc != OWNER_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get query parameters for filtering
    filters = {}
    
    if request.args.get('store'):
        filters['store'] = request.args.get('store')
    if request.args.get('pet-type'):
        filters['pet-type'] = request.args.get('pet-type')
    if request.args.get('purchase-id'):
        filters['purchase-id'] = request.args.get('purchase-id')
    if request.args.get('purchaser'):
        filters['purchaser'] = request.args.get('purchaser')
    
    # Get transactions from database
    transactions = db.get_all_transactions(filters)
    
    return jsonify(transactions), 200


if __name__ == '__main__':
    print("Pet-Order Service starting on http://{}:{}".format(HOST, PORT))
    print("Connected to pet-store1: {}".format(PET_STORE1_URL))
    print("Connected to pet-store2: {}".format(PET_STORE2_URL))
    app.run(host=HOST, port=PORT, debug=True)
