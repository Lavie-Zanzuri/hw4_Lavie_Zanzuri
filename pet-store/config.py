import os

# API ninjas configuration
NINJA_API_KEY = os.environ.get('NINJA_API_KEY', '')
NINJA_API_URL = 'https://api.api-ninjas.com/v1/animals'

# server configuration
PORT = 5001
HOST = '0.0.0.0'


IMAGES_DIR = 'images'
os.makedirs(IMAGES_DIR, exist_ok=True)
