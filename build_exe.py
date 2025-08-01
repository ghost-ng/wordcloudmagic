#!/usr/bin/env python3
"""
Build script for WordCloud Magic
Creates a professional Windows executable with proper metadata
"""
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Import version from the project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from __version__ import __version__

def create_version_file():
    """Create Windows version information file"""
    print("Creating version information file...")
    
    # Get current year for copyright
    current_year = datetime.now().year
    
    # Parse version for Windows format (needs 4 parts)
    version_parts = __version__.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    file_version = ', '.join(version_parts)
    
    version_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

VSVersionInfo(
  ffi=FixedFileInfo(
    # File version (must be a tuple of 4 integers)
    filevers=({file_version}),
    prodvers=({file_version}),
    # Contains a bitmask that specifies the valid bits 'flags'
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Ghost-ng'),
        StringStruct(u'FileDescription', u'WordCloud Magic - Modern Word Cloud Generator'),
        StringStruct(u'FileVersion', u'{__version__}.0'),
        StringStruct(u'InternalName', u'WordCloudMagic'),
        StringStruct(u'LegalCopyright', u'© {current_year} Ghost-ng. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'WordCloudMagic.exe'),
        StringStruct(u'ProductName', u'WordCloud Magic'),
        StringStruct(u'ProductVersion', u'{__version__}.0'),
        StringStruct(u'Comments', u'A modern, user-friendly word cloud generator with advanced features'),
        StringStruct(u'LegalTrademarks', u''),
        StringStruct(u'PrivateBuild', u''),
        StringStruct(u'SpecialBuild', u'')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_file = Path('file_version_info.txt')
    version_file.write_text(version_content, encoding='utf-8')
    print(f"Version file created: {version_file}")
    return version_file

def update_spec_file():
    """Update the spec file to include version information"""
    print("Updating spec file with version information...")
    
    spec_file = Path('wordcloud_app.spec')
    content = spec_file.read_text(encoding='utf-8')
    
    # Check if version_file is already set correctly
    if "version_file='file_version_info.txt'" in content:
        print("Spec file already has correct version information")
    elif 'version_file=' in content:
        # Update to use our version file
        import re
        content = re.sub(r"version_file='[^']*',", "version_file='file_version_info.txt',", content)
        spec_file.write_text(content, encoding='utf-8')
        print("Spec file updated with version information")
    else:
        print("Warning: Could not update spec file - version_file not found")

def run_clean_build():
    """Run the clean build script if it exists"""
    clean_script = Path('clean_build.bat')
    if clean_script.exists():
        print("Running clean build script...")
        result = subprocess.run([str(clean_script)], shell=True)
        if result.returncode != 0:
            print("Clean build script failed. Please check the script for errors.")
            return False
        print("Clean build script completed successfully.")
    else:
        print("No clean build script found. Continuing with build.")
    return True

def sign_exe_if_possible():
    """Provide instructions for code signing"""
    print("\n" + "="*50)
    print("CODE SIGNING INFORMATION")
    print("="*50)
    print("To make your executable more trustworthy:")
    print("1. Purchase a code signing certificate from a trusted CA")
    print("2. Use signtool.exe to sign the executable:")
    print("   signtool sign /a /t http://timestamp.digicert.com dist\\WordCloudMagic.exe")
    print("3. This prevents Windows SmartScreen warnings")
    print("="*50 + "\n")

def build():
    """Build the executable with all metadata"""
    print(f"Building WordCloud Magic v{__version__}")
    print("=" * 50)
    
    # Check if build/dist exist
    if Path('build').exists() or Path('dist').exists():
        print("Warning: 'build' or 'dist' directories already exist.")
        # In CI environment, continue without prompting
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            print("CI environment detected, continuing with build...")
        else:
            print("Running the clean build script")
            status = run_clean_build()
            if not status:
                print("Clean build script failed.")
                print("Continuing with build anyway, but this may cause issues.")

    # Create version file
    version_file = create_version_file()
    
    # Update spec file
    update_spec_file()
    
    # Build command
    cmd = ['pyinstaller', 'wordcloud_app.spec', '--noconfirm']
    
    # Add UPX directory if available
    upx_dir = os.environ.get('UPX_DIR', 'upx')
    if Path(upx_dir).exists() or os.environ.get('UPX_DIR'):
        cmd.extend(['--upx-dir', upx_dir])

    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        
        # Check exe size and details
        exe_path = Path('dist/WordCloudMagic.exe')
        if exe_path.exists():
            size = exe_path.stat().st_size
            print(f"\nExecutable Details:")
            print(f"  File: {exe_path}")
            print(f"  Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
            print(f"  Version: {__version__}")
            print(f"  Author: Ghost-ng")
            
            # Provide additional legitimacy tips
            print("\nTo improve legitimacy:")
            print("  1. The exe now includes proper version information")
            print("  2. Consider code signing (see instructions below)")
            print("  3. Submit to antivirus vendors for whitelisting")
            print("  4. Include the exe in your GitHub releases")
            
            sign_exe_if_possible()
        else:
            print("\nWarning: Executable not found!")
            return 1
    else:
        print("\n" + "="*50)
        print("BUILD FAILED!")
        print("="*50)
        print("Check the error messages above.")
        return 1
    
    # Clean up version file
    if version_file.exists():
        print(f"\nCleaning up {version_file}")
        version_file.unlink()
    
    return 0

def main():
    """Main entry point"""
    print("\nWordCloud Magic - Professional Build System")
    print("Author: Ghost-ng")
    print("=" * 50 + "\n")
    
    # Check for required files
    required_files = ['wordcloud_app.py', 'wordcloud_app.spec', '__version__.py']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("ERROR: Missing required files:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPlease ensure you're running this script from the project directory.")
        return 1
    
    return build()

if __name__ == "__main__":
    sys.exit(main())