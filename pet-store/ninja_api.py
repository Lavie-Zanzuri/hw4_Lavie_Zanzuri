import requests
import re
from typing import Optional, List
from config import NINJA_API_KEY, NINJA_API_URL

def fetch_animal_data(animal_name: str) -> Optional[dict]:
    """
    Fetch animal data from Ninja API
    Returns the exact match for the animal name
    """
    headers = {'X-Api-Key': NINJA_API_KEY}
    params = {'name': animal_name}
    
    try:
        response = requests.get(NINJA_API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # try to find a match 
            for animal in data:
                if animal.get('name', '').lower() == animal_name.lower():
                    return animal
            
            # didnt succeedd to find a match
            return None
        else:
            raise Exception(f"API response code {response.status_code}")
    
    except Exception as e:
        raise Exception(f"API response code {response.status_code if 'response' in locals() else 'unknown'}")

def extract_lifespan(lifespan_str: str) -> Optional[int]:
    """
    Extract the minimum lifespan from strings like:
    - "up to 41 years" -> 41
    - "10-12 years" -> 10
    - "from 2 to 5 years" -> 2
    """
    if not lifespan_str:
        return None
    
    # find all the numbers in the string
    numbers = re.findall(r'\d+', lifespan_str)
    
    if numbers:
        # return the smallest number 
        return int(min(numbers, key=int))
    
    return None

def extract_attributes(temperament: str) -> List[str]:
    """
    Convert temperament string to list of attributes
    "Gentle and intelligent but stubborn" -> ["Gentle", "and", "intelligent", "but", "stubborn"]
    Remove punctuation
    """
    if not temperament:
        return []
    
    # remove punctuation and split by spaces
    words = re.sub(r'[^\w\s]', '', temperament).split()
    return words

def get_pet_type_data(animal_type: str) -> dict:
    """
    Get formatted pet type data from Ninja API
    """
    animal_data = fetch_animal_data(animal_type)
    
    if not animal_data:
        raise ValueError(f"Animal type '{animal_type}' not found")
    
    
    taxonomy = animal_data.get('taxonomy', {})
    family = taxonomy.get('family', '')
    genus = taxonomy.get('genus', '')
    
    # get characteristics
    characteristics = animal_data.get('characteristics', {})
    
    # prefer temperament over group_behavior
    temperament = characteristics.get('temperament', '')
    if not temperament:
        temperament = characteristics.get('group_behavior', '')
    
    attributes = extract_attributes(temperament)
    
    
    lifespan_str = characteristics.get('lifespan', '')
    lifespan = extract_lifespan(lifespan_str)
    
    return {
        'type': animal_data.get('name', animal_type),
        'family': family,
        'genus': genus,
        'attributes': attributes,
        'lifespan': lifespan
    }
