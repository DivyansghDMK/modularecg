# ECG Monitor Application - Project Structure

## Overview
This document describes the clean, modular structure of the ECG Monitor Application after refactoring.

## Directory Structure

```
modularecg/
├── src/                           # Main application source code
│   ├── main.py                    # Application entry point
│   ├── splash_screen.py           # Application splash screen
│   │
│   ├── auth/                      # Authentication modules
│   │   ├── __init__.py
│   │   ├── sign_in.py            # User sign-in functionality
│   │   └── sign_out.py           # User sign-out functionality
│   │
│   ├── dashboard/                 # Dashboard and UI components
│   │   ├── __init__.py
│   │   ├── dashboard.py          # Main dashboard with live metrics
│   │   └── chatbot_dialog.py     # Chatbot interface
│   │
│   ├── ecg/                       # ECG processing and analysis
│   │   ├── __init__.py
│   │   ├── twelve_lead_test.py    # 12-lead ECG analysis
│   │   ├── expanded_lead_view.py  # Detailed lead analysis
│   │   ├── pan_tompkins.py       # Pan-Tompkins algorithm
│   │   ├── ecg_report_generator.py # PDF report generation
│   │   ├── demo_manager.py       # Demo data management
│   │   └── recording.py           # ECG recording functionality
│   │
│   ├── utils/                     # Utility functions and helpers
│   │   ├── __init__.py
│   │   ├── helpers.py            # General helper functions
│   │   ├── heartbeat_widget.py   # Heartbeat visualization
│   │   └── settings_manager.py   # Settings management
│   │
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Centralized configuration
│   │
│   └── core/                      # Core application modules
│       ├── __init__.py
│       ├── constants.py          # Application constants
│       ├── exceptions.py         # Custom exceptions
│       ├── validation.py         # Data validation utilities
│       └── logging_config.py     # Logging configuration
│
├── assets/                        # Images, sounds, and resources
│   ├── Deckmount.webp
│   ├── Deckmountimg.png
│   ├── ECG1.png
│   ├── heartbeat.wav
│   └── [other assets...]
│
├── clutter/                       # Archived/unused files
│   ├── change_background.py
│   ├── test_background.py
│   ├── test_paths.py
│   ├── seperate.py
│   ├── src/test_expanded_lead.py
│   ├── src/ecg/dummycsv.csv
│   ├── src/ecg/lead_grid_view.py
│   ├── src/ecg/lead_sequential_view.py
│   ├── src/nav_about.py
│   ├── src/nav_blog.py
│   ├── src/nav_home.py
│   ├── src/nav_pricing.py
│   ├── src/dashboard_config.py
│   ├── src/ecg_settings.json
│   ├── ASSET_PATHS_README.md
│   ├── ECG_FEATURES_DOCUMENTATION.md
│   └── [other archived files...]
│
├── main.py                        # Root launcher script
├── requirements.txt               # Python dependencies
├── launch_app.bat                # Windows batch launcher
├── launch_app.ps1                # PowerShell launcher
├── users.json                    # User data storage
├── ecg_settings.json             # Application settings
├── README.md                     # Project documentation
├── DOCUMENTATION.md              # Technical documentation
├── PROJECT_STRUCTURE.md          # This file
└── .gitignore                    # Git ignore rules
```

## Module Descriptions

### Core Modules (`src/core/`)
- **constants.py**: Application-wide constants and configuration values
- **exceptions.py**: Custom exception classes for error handling
- **validation.py**: Data validation utilities for ECG signals and metrics
- **logging_config.py**: Centralized logging configuration

### Configuration (`src/config/`)
- **settings.py**: Centralized configuration management with JSON file support

### Authentication (`src/auth/`)
- **sign_in.py**: User authentication and login functionality
- **sign_out.py**: User logout and session management

### Dashboard (`src/dashboard/`)
- **dashboard.py**: Main dashboard with real-time ECG metrics display
- **chatbot_dialog.py**: Interactive chatbot interface

### ECG Processing (`src/ecg/`)
- **twelve_lead_test.py**: Core 12-lead ECG analysis and visualization
- **expanded_lead_view.py**: Detailed individual lead analysis
- **pan_tompkins.py**: Pan-Tompkins algorithm for R-peak detection
- **ecg_report_generator.py**: PDF report generation
- **demo_manager.py**: Demo data management and simulation
- **recording.py**: ECG data recording functionality

### Utilities (`src/utils/`)
- **helpers.py**: General utility functions
- **heartbeat_widget.py**: Heartbeat visualization components
- **settings_manager.py**: Settings management utilities

## Key Improvements

### 1. **Modular Architecture**
- Clear separation of concerns
- Reusable components
- Easy to maintain and extend

### 2. **Error Handling**
- Custom exception classes
- Comprehensive error logging
- Graceful fallback mechanisms

### 3. **Configuration Management**
- Centralized configuration system
- Environment-specific settings
- Runtime configuration updates

### 4. **Logging System**
- Structured logging with rotation
- Performance monitoring
- Debug information capture

### 5. **Data Validation**
- Input validation for ECG signals
- Range checking for metrics
- Signal quality assessment

### 6. **Clean File Organization**
- Unused files moved to `clutter/` directory
- Clear naming conventions
- Proper Python package structure

## Benefits of New Structure

1. **Maintainability**: Clear module boundaries make code easier to understand and modify
2. **Testability**: Modular design enables better unit testing
3. **Scalability**: Easy to add new features without affecting existing code
4. **Robustness**: Comprehensive error handling and validation
5. **Documentation**: Self-documenting code with proper docstrings
6. **Performance**: Optimized logging and configuration management

## Migration Notes

- All unused files have been moved to the `clutter/` directory
- Core functionality remains unchanged
- New modules provide enhanced error handling and logging
- Configuration is now centralized and more flexible
- The application maintains backward compatibility

## Future Enhancements

- Add unit tests for each module
- Implement plugin architecture for ECG algorithms
- Add configuration GUI
- Enhance error recovery mechanisms
- Add performance monitoring dashboard
