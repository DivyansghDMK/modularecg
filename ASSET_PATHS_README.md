# Asset Paths in ECG Dashboard

## Overview
The ECG Dashboard has been updated to use portable, device-independent asset paths that will work for any user who clones the repository from GitHub.

## How It Works

### 1. Asset Path Helper Function
The dashboard uses a `get_asset_path()` function that automatically detects the correct path to the assets folder regardless of where the application is run from.

### 2. Multiple Path Detection
The function tries multiple possible locations for the assets folder:
- Standard project structure: `src/dashboard/dashboard.py` → `assets/`
- Alternative: if running from project root → `assets/`
- Alternative: if running from `src/` → `assets/`
- Alternative: if running from `dashboard/` → `../assets/`

### 3. Automatic Fallback
If no assets folder is found, the function provides a fallback path and logs warnings for debugging.

## Assets Used

### Images
- `her.png` - Heart rate overview image
- `ECG1.png` - ECG-related image
- `Deckmountimg.png` - Logo/branding image

### Animations
- `v.gif` - Background animation (fallback for plasma.gif)
- `plasma.gif` - Primary background animation (if available)
- `tenor.gif` - Additional animation

## Benefits

✅ **Portable**: Works on any device without hardcoded paths  
✅ **GitHub Compatible**: Will work for any user who clones the repo  
✅ **Robust**: Multiple fallback options for different execution contexts  
✅ **Debuggable**: Clear logging and error messages  
✅ **Maintainable**: Single function handles all asset path logic  
✅ **Customizable**: Easy background switching with built-in controls  

## Testing

Run the test script to verify asset paths are working:
```bash
python test_paths.py
```

This will show which assets are found and which are missing, helping with debugging.

## Background Control

The dashboard now includes built-in background control:

### Automatic Background Selection
- **Priority Order**: `plasma.gif` → `tenor.gif` → `v.gif` → solid color
- **Default**: `tenor.gif` (232KB, optimized for performance)
- **Fallback**: Solid gradient background if no GIFs found

### Manual Background Control
- **Background Button**: Click to cycle through options
- **Available Options**: 
  - `tenor.gif` (recommended - small, smooth)
  - `v.gif` (large - may affect performance)
  - Solid color (no animation, best performance)

### Performance Notes
- `tenor.gif`: 232KB - **Recommended for background**
- `v.gif`: 6.0MB - **May cause performance issues**
- `plasma.gif`: Not available in current assets

## File Structure
```
modularecg/
├── assets/
│   ├── her.png
│   ├── v.gif
│   ├── ECG1.png
│   └── ... (other assets)
├── src/
│   └── dashboard/
│       └── dashboard.py
└── test_paths.py
```

## Troubleshooting

If assets aren't loading:
1. Check the console output for path warnings
2. Verify the assets folder exists in the project root
3. Run `test_paths.py` to debug path issues
4. Ensure the project structure matches the expected layout
