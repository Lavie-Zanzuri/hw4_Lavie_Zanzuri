from flask import Flask, jsonify, request, send_file
from ninja_api import get_pet_type_data
from config import PORT, HOST
from image_handler import download_and_save_image, delete_image, get_image_path
from db_handler import get_db
from datetime import datetime
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


def is_valid_date(date_str):
    """Check if date is in DD-MM-YYYY format"""
    if date_str == "NA":
        return True
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except:
        return False


@app.route('/pet-types', methods=['GET', 'POST'])
def handle_pet_types():
    """Handle /pet-types endpoint"""
    
    if request.method == 'POST':
        
        if 'application/json' not in request.headers.get('Content-Type', ''):
            return jsonify({"error": "Expected application/json media type"}), 415
        
        data = request.get_json()
        
        # validate required field
        if 'type' not in data:
            return jsonify({"error": "Malformed data"}), 400
        
        animal_type = data['type']
        
        # check if the pet type already exists
        if db.pet_type_exists(animal_type):
            return jsonify({"error": "Malformed data"}), 400
        
        try:
            # get data from Ninja API
            ninja_data = get_pet_type_data(animal_type)
            
            # create PetType in database
            pet_type = db.create_pet_type(ninja_data)
            
            return jsonify(pet_type), 201
        
        except ValueError as e:
            # didn't succeed to find animal in API ninja
            return jsonify({"error": "Malformed data"}), 400
        
        except Exception as e:
            error_msg = str(e)
            return jsonify({"server error": error_msg}), 500
    
    else:  # GET
        
        filters = {}
        
        if request.args.get('family'):
            filters['family'] = request.args.get('family')
        if request.args.get('genus'):
            filters['genus'] = request.args.get('genus')
        if request.args.get('type'):
            filters['type'] = request.args.get('type')
        if request.args.get('id'):
            filters['id'] = request.args.get('id')
        if request.args.get('lifespan'):
            filters['lifespan'] = request.args.get('lifespan')
        if request.args.get('hasAttribute'):
            filters['hasAttribute'] = request.args.get('hasAttribute')
        
        result = db.get_all_pet_types(filters)
        
        return jsonify(result), 200


@app.route('/pet-types/<id>', methods=['GET', 'DELETE'])
def handle_pet_type(id):
    """Handle /pet-types/{id} endpoint"""
    
    if request.method == 'GET':
        # check if pet type exists
        pet_type = db.get_pet_type_by_id(id)
        
        if not pet_type:
            return jsonify({"error": "Not found"}), 404
        
        return jsonify(pet_type), 200
    
    elif request.method == 'DELETE':
        # check if pet type exists
        pet_type = db.get_pet_type_by_id(id)
        
        if not pet_type:
            return jsonify({"error": "Not found"}), 404
        
        # check if pet type has pets
        if len(pet_type['pets']) > 0:
            return jsonify({"error": "Malformed data"}), 400
        
        # delete the pet type
        db.delete_pet_type(id)
        
        return "", 204


@app.route('/pet-types/<pet_type_id>/pets', methods=['GET', 'POST'])
def handle_pets(pet_type_id):
    """Handle /pet-types/{id}/pets endpoint"""
    
    # check if pet type exists
    pet_type = db.get_pet_type_by_id(pet_type_id)
    
    if not pet_type:
        return jsonify({"error": "Not found"}), 404
    
    if request.method == 'POST':
        # check Content type
        if 'application/json' not in request.headers.get('Content-Type', ''):
            return jsonify({"error": "Expected application/json media type"}), 415
        
        data = request.get_json()
        
        # checking the required field
        if 'name' not in data:
            return jsonify({"error": "Malformed data"}), 400
        
        pet_name = data['name']
        
        # check empty name
        if not pet_name or not pet_name.strip():
            return jsonify({"error": "Malformed data"}), 400
        
        # check if pet already exists
        if db.pet_exists(pet_type_id, pet_name):
            return jsonify({"error": "Malformed data"}), 400
        
        
        birthdate = data.get('birthdate')
        if not birthdate:  
            birthdate = 'NA'
        picture_url = data.get('picture-url', None)
        
        # birthdate format
        if not is_valid_date(birthdate):
            return jsonify({"error": "Malformed data"}), 400
        
        picture_filename = "NA"
        if picture_url:
            picture_filename = download_and_save_image(picture_url, pet_name, pet_type['type'])
        
        # create a pet object
        pet_data = {
            'name': pet_name,
            'birthdate': birthdate,
            'picture': picture_filename
        }
        
        # add to database
        db.create_pet(pet_type_id, pet_data)
        
        return jsonify(pet_data), 201
    
    else:  # GET
       
        filters = {}
        if request.args.get('birthdateGT'):
            filters['birthdateGT'] = request.args.get('birthdateGT')
        if request.args.get('birthdateLT'):
            filters['birthdateLT'] = request.args.get('birthdateLT')
        
        result = db.get_pets_by_type(pet_type_id, filters)
        
        return jsonify(result), 200


@app.route('/pet-types/<pet_type_id>/pets/<pet_name>', methods=['GET', 'DELETE', 'PUT'])
def handle_pet(pet_type_id, pet_name):
    """Handle /pet-types/{id}/pets/{name} endpoint"""
    
    # check if pet type exists
    pet_type = db.get_pet_type_by_id(pet_type_id)
    
    if not pet_type:
        return jsonify({"error": "Not found"}), 404
    
    # check if pet exists
    pet = db.get_pet(pet_type_id, pet_name)
    
    if not pet:
        return jsonify({"error": "Not found"}), 404
    
    if request.method == 'GET':
        return jsonify(pet), 200
    
    elif request.method == 'DELETE':
        # delete image if exists
        if pet['picture'] != "NA":
            delete_image(pet['picture'])
        
        # delete from database
        db.delete_pet(pet_type_id, pet_name)
        
        return "", 204
    
    elif request.method == 'PUT':
        # Check Content type
        if 'application/json' not in request.headers.get('Content-Type', ''):
            return jsonify({"error": "Expected application/json media type"}), 415
        
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({"error": "Malformed data"}), 400
        
        new_name = data['name']
        
        if new_name.lower() != pet_name.lower():
            return jsonify({"error": "Malformed data"}), 400
        
        new_birthdate = data.get('birthdate', pet['birthdate'])
        if new_birthdate is None or new_birthdate == "":
            new_birthdate = 'NA'
        new_picture_url = data.get('picture-url', None)
        
       
        if not is_valid_date(new_birthdate):
            return jsonify({"error": "Malformed data"}), 400
        
        new_picture = pet['picture']
        if new_picture_url:
            
            new_picture = download_and_save_image(new_picture_url, new_name, pet_type['type'])
            
            if pet['picture'] != "NA" and pet['picture'] != new_picture:
                delete_image(pet['picture'])
        
        # update pet in database
        updated_pet = {
            'name': new_name,
            'birthdate': new_birthdate,
            'picture': new_picture
        }
        
        db.update_pet(pet_type_id, pet_name, updated_pet)
        
        return jsonify(updated_pet), 200


@app.route('/pictures/<filename>', methods=['GET'])
def get_picture(filename):
    """Handle /pictures/{filename} endpoint"""
    filepath = get_image_path(filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "Not found"}), 404
    
    if filename.endswith('.png'):
        mimetype = 'image/png'
    else:
        mimetype = 'image/jpeg'
    
    return send_file(filepath, mimetype=mimetype)


if __name__ == '__main__':
    print("Server starting on http://{}:{}".format(HOST, PORT))
    print("Store ID: {}".format(os.environ.get('STORE_ID', '1')))
    app.run(host=HOST, port=PORT, debug=True)
