#!/usr/bin/env python3
"""
Test script to verify image paths are working correctly
"""
import os

def get_asset_path(asset_name):
    """
    Get the absolute path to an asset file in a portable way.
    This function will work regardless of where the script is run from.
    
    Args:
        asset_name (str): Name of the asset file (e.g., 'her.png', 'v.gif')
    
    Returns:
        str: Absolute path to the asset file
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for the assets folder
    possible_paths = [
        # Standard project structure: script in root -> assets/
        os.path.join(script_dir, "assets"),
        # Alternative: if running from src/
        os.path.join(script_dir, "src", "assets"),
        # Alternative: if running from dashboard/
        os.path.join(script_dir, "src", "dashboard", "..", "..", "assets"),
    ]
    
    # Find the first valid assets directory
    assets_dir = None
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            assets_dir = path
            break
    
    if assets_dir is None:
        print(f"Warning: Could not find assets directory. Tried paths: {possible_paths}")
        # Return a default path as fallback
        return os.path.join(script_dir, "assets", asset_name)
    
    # Return the full path to the asset
    asset_path = os.path.join(assets_dir, asset_name)
    
    return asset_path

def test_image_paths():
    print("=== Testing Asset Paths (Portable Version) ===")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    # Test common assets
    test_assets = ["her.png", "v.gif", "plasma.gif", "ECG1.png"]
    
    for asset in test_assets:
        path = get_asset_path(asset)
        exists = os.path.exists(path)
        print(f"{asset}: {'✓' if exists else '✗'} - {path}")
        
        if not exists:
            print(f"  Warning: {asset} not found!")
    
    # List all files in assets directory
    assets_dir = os.path.dirname(get_asset_path("her.png"))
    if os.path.exists(assets_dir):
        print(f"\nFiles in assets directory ({assets_dir}):")
        for file in os.listdir(assets_dir):
            print(f"  - {file}")
    else:
        print(f"\nAssets directory not found!")
    
    print("=== Asset Path Test Complete ===")

if __name__ == "__main__":
    test_image_paths()
