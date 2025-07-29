#!/usr/bin/env python
"""
Build script for creating WordCloud Magic executable
This script handles the PyInstaller build process and post-build tasks
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse

def clean_build_dirs():
    """Remove previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Remove .spec file if it exists and we're regenerating
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        if spec_file.name != 'wordcloud_app.spec':
            print(f"Removing {spec_file}...")
            spec_file.unlink()

def check_dependencies():
    """Verify all required packages are installed"""
    print("Checking dependencies...")
    try:
        import ttkbootstrap
        import wordcloud
        import matplotlib
        import PIL
        import numpy
        import PyPDF2
        import docx
        import pptx
        import markdown2
        print("✓ All dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def create_version_file():
    """Create a version file for the executable (Windows only)"""
    version_content = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'WordCloud Magic'),
        StringStruct(u'FileDescription', u'WordCloud Magic - Create beautiful word clouds'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'WordCloudMagic'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025'),
        StringStruct(u'OriginalFilename', u'WordCloudMagic.exe'),
        StringStruct(u'ProductName', u'WordCloud Magic'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open('version.txt', 'w') as f:
        f.write(version_content)
    return 'version.txt'

def build_executable(debug=False, onefile=True):
    """Run PyInstaller to create the executable"""
    if not check_dependencies():
        return False
    
    print("\nBuilding executable...")
    
    # Base PyInstaller command
    cmd = [sys.executable, '-m', 'PyInstaller']
    
    # Use spec file if it exists
    if os.path.exists('wordcloud_app.spec'):
        cmd.append('wordcloud_app.spec')
    else:
        # Build command from scratch
        cmd.extend([
            '--name=WordCloudMagic',
            '--icon=icons/icon_256.ico',
            '--noconsole',  # No console window for GUI app
        ])
        
        if onefile:
            cmd.append('--onefile')
        
        if debug:
            cmd.extend(['--debug=all', '--log-level=DEBUG'])
        
        # Add data files
        cmd.extend([
            '--add-data=assets;assets',
            '--add-data=configs;configs',
            '--add-data=templates;templates',
            '--add-data=icons/icon_256.ico;.',
        ])
        
        # Add hidden imports
        hidden_imports = [
            'ttkbootstrap',
            'wordcloud',
            'matplotlib.backends.backend_tkagg',
            'PIL._tkinter_finder',
            'markdown2',
            'numpy',
            'scipy',
            'scipy.spatial',
        ]
        for imp in hidden_imports:
            cmd.extend(['--hidden-import', imp])
        
        # Add the main script
        cmd.append('wordcloud_app.py')
    
    # Run PyInstaller
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n✓ Build successful!")
        
        # Show output location
        if onefile:
            exe_path = Path('dist/WordCloudMagic.exe')
        else:
            exe_path = Path('dist/WordCloudMagic/WordCloudMagic.exe')
        
        if exe_path.exists():
            print(f"Executable created: {exe_path.absolute()}")
            print(f"File size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        return True
    else:
        print("\n✗ Build failed!")
        return False

def create_installer_script():
    """Create an Inno Setup script for Windows installer"""
    iss_content = """
[Setup]
AppName=WordCloud Magic
AppVersion=1.0
DefaultDirName={pf}\\WordCloud Magic
DefaultGroupName=WordCloud Magic
UninstallDisplayIcon={app}\\WordCloudMagic.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=WordCloudMagic_Setup

[Files]
Source: "dist\\WordCloudMagic.exe"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\\WordCloud Magic"; Filename: "{app}\\WordCloudMagic.exe"
Name: "{group}\\Uninstall WordCloud Magic"; Filename: "{uninstallexe}"
Name: "{commondesktop}\\WordCloud Magic"; Filename: "{app}\\WordCloudMagic.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
"""
    
    with open('installer.iss', 'w') as f:
        f.write(iss_content)
    print("Created installer.iss for Inno Setup")

def main():
    parser = argparse.ArgumentParser(description='Build WordCloud Magic executable')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before building')
    parser.add_argument('--debug', action='store_true', help='Build with debug information')
    parser.add_argument('--onedir', action='store_true', help='Create a directory distribution instead of single file')
    parser.add_argument('--installer', action='store_true', help='Create installer script (Windows)')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build_dirs()
    
    # Build the executable
    success = build_executable(debug=args.debug, onefile=not args.onedir)
    
    if success and args.installer and sys.platform == 'win32':
        create_installer_script()
    
    if success:
        print("\n" + "="*50)
        print("Build completed successfully!")
        print("="*50)
        print("\nNext steps:")
        print("1. Test the executable in dist/")
        print("2. Consider code signing for distribution")
        if sys.platform == 'win32':
            print("3. Create installer with Inno Setup (optional)")
        print("4. Create release notes and documentation")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())