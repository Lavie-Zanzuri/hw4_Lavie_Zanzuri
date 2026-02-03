import requests
import os
from config import IMAGES_DIR
from urllib.parse import urlparse

def download_and_save_image(url, pet_name, pet_type):
    """
    Download image from URL and save it locally
    Returns the filename or "NA" if failed
    """
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return "NA"
        
        
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # try to get extension from URL
        ext = os.path.splitext(path)[1]
        
        # .jpeg to .jpg
        if ext == '.jpeg':
            ext = '.jpg'
        
       
        if not ext or ext not in ['.jpg', '.png']:
            content_type = response.headers.get('Content-Type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            else:
                ext = '.jpg'  # default
        
        # create filename
        filename = "{}-{}{}".format(pet_name.replace(' ', '_'), 
                                   pet_type.replace(' ', '_'), 
                                   ext)
        
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # save image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filename
    
    except Exception as e:
        print("Error downloading image: {}".format(e))
        return "NA"

def delete_image(filename):
    """
    Delete image file
    """
    if filename == "NA":
        return
    
    try:
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print("Error deleting image: {}".format(e))

def get_image_path(filename):
    """
    Get full path to image
    """
    return os.path.join(IMAGES_DIR, filename)
