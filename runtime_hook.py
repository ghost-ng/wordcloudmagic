"""
Runtime hook for PyInstaller to set Windows App User Model ID
This runs before the main application starts
"""
import sys
import os

if sys.platform == 'win32':
    try:
        import ctypes
        from ctypes import wintypes
        
        # Set the App User Model ID as early as possible
        myappid = 'com.wordcloudmagic.app.1.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        print(f"Set Windows App User Model ID: {myappid}")
    except Exception as e:
        print(f"Failed to set App User Model ID: {e}")