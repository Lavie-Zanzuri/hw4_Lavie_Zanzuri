import os

# Server configuration
PORT = 5003
HOST = '0.0.0.0'

# MongoDB configuration - pet-order uses its own MongoDB instance
MONGO_HOST = os.environ.get('MONGO_HOST', 'mongodb-order')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))

# Pet store services URLs 
PET_STORE1_URL = os.environ.get('PET_STORE1_URL', 'http://pet-store1:5001')
PET_STORE2_URL = os.environ.get('PET_STORE2_URL', 'http://pet-store2:5001')

# Owner password for transactions endpoint
OWNER_PASSWORD = "LovesPetsL2M3n4"
