
import os

def get_asset_path(filename):
    """
    Get the absolute path to an asset file.
    """
    # This file is in src/sun_earth/utils.py
    # Assets are in src/sun_earth/assets/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base_dir, 'assets', filename)
    
    if os.path.exists(asset_path):
        return asset_path
    else:
        return None
