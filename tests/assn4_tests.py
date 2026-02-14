"""
Assignment 4 - Pet Store API Tests
"""
import pytest
import requests

# Base URLs
STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"
ORDER_URL = "http://localhost:5003"

# Pet Types payloads
PET_TYPE1 = {"type": "Golden Retriever"}
PET_TYPE2 = {"type": "Australian Shepherd"}
PET_TYPE3 = {"type": "Abyssinian"}
PET_TYPE4 = {"type": "bulldog"}

# Expected values after API enrichment
PET_TYPE1_VAL = {
    "type": "Golden Retriever",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": [],
    "lifespan": 12
}

PET_TYPE2_VAL = {
    "type": "Australian Shepherd",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": ["Loyal", "outgoing", "and", "friendly"],
    "lifespan": 15
}

PET_TYPE3_VAL = {
    "type": "Abyssinian",
    "family": "Felidae",
    "genus": "Felis",
    "attributes": ["Intelligent", "and", "curious"],
    "lifespan": 13
}

PET_TYPE4_VAL = {
    "type": "bulldog",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": ["Gentle", "calm", "and", "affectionate"],
    "lifespan": None
}

# Pets payloads
PET1_TYPE1 = {"name": "Lander", "birthdate": "14-05-2020"}
PET2_TYPE1 = {"name": "Lanky"}
PET3_TYPE1 = {"name": "Shelly", "birthdate": "07-07-2019"}
PET4_TYPE2 = {"name": "Felicity", "birthdate": "27-11-2011"}
PET5_TYPE3 = {"name": "Muscles"}
PET6_TYPE3 = {"name": "Junior"}
PET7_TYPE4 = {"name": "Lazy", "birthdate": "07-08-2018"}
PET8_TYPE4 = {"name": "Lemon", "birthdate": "27-03-2020"}

# Headers
HEADERS = {"Content-Type": "application/json"}

# Store IDs from POST requests
store1_ids = {}
store2_ids = {}


class TestPetStoreAPI:
    """Test class for Pet Store API"""
    
    # ========== Tests 1-2: POST pet-types to both stores ==========
    
    def test_01_post_pet_types_to_store1(self):
        """
        Test 1: Execute 3 POST /pet-types requests to pet store #1
        with payloads PET_TYPE1, PET_TYPE2, and PET_TYPE3
        """
        global store1_ids
        
        # POST PET_TYPE1
        response1 = requests.post(f"{STORE1_URL}/pet-types", json=PET_TYPE1, headers=HEADERS)
        assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        data1 = response1.json()
        assert 'id' in data1, "Response should contain 'id'"
        assert data1['family'] == PET_TYPE1_VAL['family'], f"Expected family {PET_TYPE1_VAL['family']}, got {data1.get('family')}"
        assert data1['genus'] == PET_TYPE1_VAL['genus'], f"Expected genus {PET_TYPE1_VAL['genus']}, got {data1.get('genus')}"
        store1_ids['id_1'] = data1['id']
        
        # POST PET_TYPE2
        response2 = requests.post(f"{STORE1_URL}/pet-types", json=PET_TYPE2, headers=HEADERS)
        assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
        data2 = response2.json()
        assert 'id' in data2, "Response should contain 'id'"
        assert data2['family'] == PET_TYPE2_VAL['family'], f"Expected family {PET_TYPE2_VAL['family']}, got {data2.get('family')}"
        assert data2['genus'] == PET_TYPE2_VAL['genus'], f"Expected genus {PET_TYPE2_VAL['genus']}, got {data2.get('genus')}"
        store1_ids['id_2'] = data2['id']
        
        # POST PET_TYPE3
        response3 = requests.post(f"{STORE1_URL}/pet-types", json=PET_TYPE3, headers=HEADERS)
        assert response3.status_code == 201, f"Expected 201, got {response3.status_code}"
        data3 = response3.json()
        assert 'id' in data3, "Response should contain 'id'"
        assert data3['family'] == PET_TYPE3_VAL['family'], f"Expected family {PET_TYPE3_VAL['family']}, got {data3.get('family')}"
        assert data3['genus'] == PET_TYPE3_VAL['genus'], f"Expected genus {PET_TYPE3_VAL['genus']}, got {data3.get('genus')}"
        store1_ids['id_3'] = data3['id']
        
        # Verify all IDs are unique
        ids = [store1_ids['id_1'], store1_ids['id_2'], store1_ids['id_3']]
        assert len(ids) == len(set(ids)), "All IDs should be unique"
    
    def test_02_post_pet_types_to_store2(self):
        """
        Test 2: Execute 3 POST /pet-types requests to pet store #2
        with payloads PET_TYPE1, PET_TYPE2, and PET_TYPE4
        """
        global store2_ids
        
        # POST PET_TYPE1
        response1 = requests.post(f"{STORE2_URL}/pet-types", json=PET_TYPE1, headers=HEADERS)
        assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        data1 = response1.json()
        assert 'id' in data1, "Response should contain 'id'"
        assert data1['family'] == PET_TYPE1_VAL['family'], f"Expected family {PET_TYPE1_VAL['family']}, got {data1.get('family')}"
        assert data1['genus'] == PET_TYPE1_VAL['genus'], f"Expected genus {PET_TYPE1_VAL['genus']}, got {data1.get('genus')}"
        store2_ids['id_4'] = data1['id']
        
        # POST PET_TYPE2
        response2 = requests.post(f"{STORE2_URL}/pet-types", json=PET_TYPE2, headers=HEADERS)
        assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
        data2 = response2.json()
        assert 'id' in data2, "Response should contain 'id'"
        assert data2['family'] == PET_TYPE2_VAL['family'], f"Expected family {PET_TYPE2_VAL['family']}, got {data2.get('family')}"
        assert data2['genus'] == PET_TYPE2_VAL['genus'], f"Expected genus {PET_TYPE2_VAL['genus']}, got {data2.get('genus')}"
        store2_ids['id_5'] = data2['id']
        
        # POST PET_TYPE4
        response3 = requests.post(f"{STORE2_URL}/pet-types", json=PET_TYPE4, headers=HEADERS)
        assert response3.status_code == 201, f"Expected 201, got {response3.status_code}"
        data3 = response3.json()
        assert 'id' in data3, "Response should contain 'id'"
        assert data3['family'] == PET_TYPE4_VAL['family'], f"Expected family {PET_TYPE4_VAL['family']}, got {data3.get('family')}"
        assert data3['genus'] == PET_TYPE4_VAL['genus'], f"Expected genus {PET_TYPE4_VAL['genus']}, got {data3.get('genus')}"
        store2_ids['id_6'] = data3['id']
        
        # Verify all IDs are unique
        ids = [store2_ids['id_4'], store2_ids['id_5'], store2_ids['id_6']]
        assert len(ids) == len(set(ids)), "All IDs should be unique"
    
    # ========== Tests 3-4: POST pets to store 1 ==========
    
    def test_03_post_pets_to_store1_type1(self):
        """
        Test 3: Execute POST /pet-types/{id_1}/pets to pet-store #1
        with payload PET1_TYPE1 and PET2_TYPE1
        """
        id_1 = store1_ids['id_1']
        
        # POST PET1_TYPE1
        response1 = requests.post(f"{STORE1_URL}/pet-types/{id_1}/pets", json=PET1_TYPE1, headers=HEADERS)
        assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        
        # POST PET2_TYPE1
        response2 = requests.post(f"{STORE1_URL}/pet-types/{id_1}/pets", json=PET2_TYPE1, headers=HEADERS)
        assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
    
    def test_04_post_pets_to_store1_type3(self):
        """
        Test 4: Execute POST /pet-types/{id_3}/pets to pet-store #1
        with payload PET5_TYPE3 and PET6_TYPE3
        """
        id_3 = store1_ids['id_3']
        
        # POST PET5_TYPE3
        response1 = requests.post(f"{STORE1_URL}/pet-types/{id_3}/pets", json=PET5_TYPE3, headers=HEADERS)
        assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        
        # POST PET6_TYPE3
        response2 = requests.post(f"{STORE1_URL}/pet-types/{id_3}/pets", json=PET6_TYPE3, headers=HEADERS)
        assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
    
    # ========== Tests 5-7: POST pets to store 2 ==========
    
    def test_05_post_pets_to_store2_type1(self):
        """
        Test 5: Execute POST /pet-types/{id_4}/pets to pet-store #2
        with payload PET3_TYPE1
        """
        id_4 = store2_ids['id_4']
        
        response = requests.post(f"{STORE2_URL}/pet-types/{id_4}/pets", json=PET3_TYPE1, headers=HEADERS)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    def test_06_post_pets_to_store2_type2(self):
        """
        Test 6: Execute POST /pet-types/{id_5}/pets to pet-store #2
        with payload PET4_TYPE2
        """
        id_5 = store2_ids['id_5']
        
        response = requests.post(f"{STORE2_URL}/pet-types/{id_5}/pets", json=PET4_TYPE2, headers=HEADERS)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    def test_07_post_pets_to_store2_type4(self):
        """
        Test 7: Execute POST /pet-types/{id_6}/pets to pet-store #2
        with payload PET7_TYPE4 and PET8_TYPE4
        """
        id_6 = store2_ids['id_6']
        
        # POST PET7_TYPE4
        response1 = requests.post(f"{STORE2_URL}/pet-types/{id_6}/pets", json=PET7_TYPE4, headers=HEADERS)
        assert response1.status_code == 201, f"Expected 201, got {response1.status_code}"
        
        # POST PET8_TYPE4
        response2 = requests.post(f"{STORE2_URL}/pet-types/{id_6}/pets", json=PET8_TYPE4, headers=HEADERS)
        assert response2.status_code == 201, f"Expected 201, got {response2.status_code}"
    
    # ========== Test 8: GET pet-type by ID ==========
    
    def test_08_get_pet_type_by_id(self):
        """
        Test 8: Execute GET /pet-types/{id2} to pet-store #1
        Verify JSON matches PET_TYPE2_VAL fields and status code is 200
        """
        id_2 = store1_ids['id_2']
        
        response = requests.get(f"{STORE1_URL}/pet-types/{id_2}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['type'] == PET_TYPE2_VAL['type'], f"Expected type {PET_TYPE2_VAL['type']}, got {data.get('type')}"
        assert data['family'] == PET_TYPE2_VAL['family'], f"Expected family {PET_TYPE2_VAL['family']}, got {data.get('family')}"
        assert data['genus'] == PET_TYPE2_VAL['genus'], f"Expected genus {PET_TYPE2_VAL['genus']}, got {data.get('genus')}"
        assert data['attributes'] == PET_TYPE2_VAL['attributes'], f"Expected attributes {PET_TYPE2_VAL['attributes']}, got {data.get('attributes')}"
        assert data['lifespan'] == PET_TYPE2_VAL['lifespan'], f"Expected lifespan {PET_TYPE2_VAL['lifespan']}, got {data.get('lifespan')}"
    
    # ========== Test 9: GET pets by pet-type ==========
    
    def test_09_get_pets_by_type(self):
        """
        Test 9: Execute GET /pet-types/{id6}/pets to pet-store #2
        Verify returned JSON array contains pets with fields from PET7_TYPE4 and PET8_TYPE4
        """
        id_6 = store2_ids['id_6']
        
        response = requests.get(f"{STORE2_URL}/pet-types/{id_6}/pets")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        # assert response.status_code == 404, f"Expected 200, got {response.status_code}"
        
        pets = response.json()
        assert isinstance(pets, list), "Response should be a list"
        assert len(pets) == 2, f"Expected 2 pets, got {len(pets)}"
        
        # Get pet names
        pet_names = [pet['name'] for pet in pets]
        
        # Verify PET7_TYPE4 (Lazy) is in the list
        assert PET7_TYPE4['name'] in pet_names, f"Expected {PET7_TYPE4['name']} in pets"
        
        # Verify PET8_TYPE4 (Lemon) is in the list
        assert PET8_TYPE4['name'] in pet_names, f"Expected {PET8_TYPE4['name']} in pets"
        
        # Verify birthdates
        for pet in pets:
            if pet['name'] == PET7_TYPE4['name']:
                assert pet['birthdate'] == PET7_TYPE4['birthdate'], f"Expected birthdate {PET7_TYPE4['birthdate']}"
            elif pet['name'] == PET8_TYPE4['name']:
                assert pet['birthdate'] == PET8_TYPE4['birthdate'], f"Expected birthdate {PET8_TYPE4['birthdate']}"
