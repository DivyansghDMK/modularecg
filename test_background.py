#!/usr/bin/env python3
"""
Test script to verify background functionality
"""
import os

def get_asset_path(asset_name):
    """
    Get the absolute path to an asset file in a portable way.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, "assets"),
        os.path.join(script_dir, "src", "assets"),
        os.path.join(script_dir, "src", "dashboard", "..", "..", "assets"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return os.path.join(path, asset_name)
    
    return os.path.join(script_dir, "assets", asset_name)

def test_backgrounds():
    print("=== Testing Background Assets ===")
    
    backgrounds = ["plasma.gif", "tenor.gif", "v.gif"]
    
    for bg in backgrounds:
        path = get_asset_path(bg)
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        size_mb = size / (1024 * 1024) if size > 0 else 0
        
        print(f"{bg}: {'✓' if exists else '✗'} - {path}")
        if exists:
            print(f"  Size: {size_mb:.1f} MB")
        else:
            print(f"  Warning: {bg} not found!")
    
    print("\n=== Background Test Complete ===")
    print("\nRecommendations:")
    print("- tenor.gif (232KB) is the smallest and most suitable for background")
    print("- v.gif (6.0MB) is very large and may cause performance issues")
    print("- plasma.gif doesn't exist, so tenor.gif will be used as default")

if __name__ == "__main__":
    test_backgrounds()

