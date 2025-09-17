#!/usr/bin/env python3
"""
Quick script to change dashboard background
Run this script to easily change your dashboard background without editing files.
"""

import os

def change_background(background_type):
    """
    Change the dashboard background by updating the configuration file.
    
    Args:
        background_type (str): "v.gif", "tenor.gif", "solid", or "performance"
    """
    
    config_file = "dashboard_config.py"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found!")
        print("Make sure you're running this from the project root directory.")
        return False
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Define the changes
    changes = {
        "v.gif": {
            "use_gif_background": "True",
            "preferred_background": '"v.gif"'
        },
        "tenor.gif": {
            "use_gif_background": "True", 
            "preferred_background": '"tenor.gif"'
        },
        "solid": {
            "use_gif_background": "False",
            "preferred_background": '"none"'
        },
        "performance": {
            "use_gif_background": "False",
            "preferred_background": '"none"'
        }
    }
    
    if background_type not in changes:
        print(f"❌ Invalid background type: {background_type}")
        print("Valid options: v.gif, tenor.gif, solid, performance")
        return False
    
    # Apply changes
    new_content = content
    for key, value in changes[background_type].items():
        # Find and replace the line
        import re
        pattern = rf'(\s*"{key}":\s*){value}'
        replacement = rf'\1{value}'
        new_content = re.sub(pattern, replacement, new_content)
    
    # Write updated config
    with open(config_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Background changed to: {background_type}")
    print("🔄 Restart your dashboard application to see the changes!")
    return True

def show_current_background():
    """Show the current background setting."""
    try:
        from dashboard_config import DASHBOARD_BACKGROUND
        current = DASHBOARD_BACKGROUND
        print(f"Current Background: {current['preferred_background']}")
        print(f"GIF Enabled: {current['use_gif_background']}")
    except ImportError:
        print("Configuration file not found or invalid")

def main():
    print("🎨 Dashboard Background Changer")
    print("=" * 40)
    
    show_current_background()
    print()
    
    print("Available backgrounds:")
    print("  1. v.gif - Full animation (6.0MB, may affect performance)")
    print("  2. tenor.gif - Light animation (232KB, balanced)")
    print("  3. solid - No animation (best performance)")
    print("  4. performance - No animation (best performance)")
    print()
    
    choice = input("Enter your choice (1-4) or type the background name: ").strip()
    
    # Map choices to background types
    choice_map = {
        "1": "v.gif",
        "2": "tenor.gif", 
        "3": "solid",
        "4": "performance"
    }
    
    if choice in choice_map:
        background_type = choice_map[choice]
    else:
        background_type = choice
    
    if change_background(background_type):
        print(f"\n🎉 Successfully changed background to: {background_type}")
        print("💡 Tip: You can also edit dashboard_config.py directly for more options")

if __name__ == "__main__":
    main()

