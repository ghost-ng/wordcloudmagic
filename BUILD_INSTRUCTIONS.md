# WordCloud Magic - Build Instructions

This document provides detailed instructions for building WordCloud Magic as a standalone executable.

## Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** activated (recommended)
3. **All dependencies installed**: `pip install -r requirements.txt`
4. **PyInstaller**: `pip install pyinstaller`

## Quick Build

The easiest way to build the executable:

```bash
python build_exe.py --clean
```

This will:
- Clean previous build artifacts
- Check dependencies
- Build a single-file executable
- Place it in the `dist/` directory

## Build Options

### Debug Build
For troubleshooting build issues:
```bash
python build_exe.py --debug
```

### Directory Distribution
Instead of a single file, create a folder with all dependencies:
```bash
python build_exe.py --onedir
```

### Create Installer (Windows)
Generate an Inno Setup script:
```bash
python build_exe.py --installer
```

## Manual Build Process

If you prefer to use PyInstaller directly:

### Using the Spec File
```bash
pyinstaller wordcloud_app.spec
```

### From Scratch
```bash
pyinstaller --name=WordCloudMagic \
            --onefile \
            --windowed \
            --icon=icons/icon_256.ico \
            --add-data="assets;assets" \
            --add-data="configs;configs" \
            --add-data="templates;templates" \
            --add-data="icons/icon_256.ico;." \
            --hidden-import=ttkbootstrap \
            --hidden-import=matplotlib.backends.backend_tkagg \
            --hidden-import=PIL._tkinter_finder \
            --hidden-import=markdown2 \
            wordcloud_app.py
```

## Important Notes

### File Structure
The application expects the following structure:
```
WordCloudMagic.exe (or WordCloudMagic/)
├── assets/
│   ├── btn_*.svg (button icons)
│   └── tab_*.svg (tab icons)
├── configs/
│   ├── default.json (default configuration)
│   ├── wordcloud_config.json (auto-saved user config)
│   └── theme.json (theme preferences)
├── templates/
│   ├── help.md
│   └── help_template.html
└── icons/
    └── icon_256.ico
```

### Data Files
All non-Python files are bundled using PyInstaller's `--add-data` option:
- Configuration files in `configs/`
- Help templates in `templates/`
- Application icon `icon.png`

### Hidden Imports
Some packages require explicit imports:
- `ttkbootstrap` and its themes
- `matplotlib.backends.backend_tkagg`
- `PIL._tkinter_finder` (for Tkinter integration)
- `markdown2` (for help system)

### Platform-Specific Notes

#### Windows
- The executable will be around 50-100 MB due to bundled dependencies
- Windows Defender may flag new executables - consider code signing
- Use `--windowed` to prevent console window

#### macOS
- May require additional steps for code signing
- Consider creating a .app bundle
- Use `py2app` as an alternative to PyInstaller

#### Linux
- The executable should work on most distributions
- May need to set execute permissions: `chmod +x WordCloudMagic`
- Consider creating an AppImage for better compatibility

## Troubleshooting

### Windows Taskbar Icon Not Updating

If the taskbar shows the default Python/Tkinter icon instead of the WordCloud Magic icon:

1. **Run the icon cache cleaner**:
   ```batch
   clear_icon_cache.bat
   ```
   This will clear Windows' icon cache and restart Explorer.

2. **Manually refresh the icon cache**:
   - Close all instances of WordCloud Magic
   - Open Task Manager and end all Python processes
   - Delete `%localappdata%\IconCache.db`
   - Restart Windows Explorer or reboot

3. **Pin to taskbar method**:
   - Right-click the exe and select "Pin to taskbar"
   - The pinned icon should show correctly
   - Launch from the pinned icon

This is a Windows limitation where it aggressively caches taskbar icons, especially for Python applications.

### Common Issues

1. **Missing modules at runtime**
   - Add to `hiddenimports` in spec file
   - Or use `--hidden-import` flag

2. **Data files not found**
   - Ensure paths in `--add-data` are correct
   - Check the `_MEIPASS` handling in the code

3. **Large executable size**
   - Use UPX compression (enabled by default)
   - Consider `--onedir` instead of `--onefile`
   - Exclude unnecessary modules with `--exclude-module`

4. **Antivirus false positives**
   - Common with PyInstaller executables
   - Consider code signing certificate
   - Submit to antivirus vendors for whitelisting

### Debug Steps

1. Run with console enabled:
   ```bash
   pyinstaller --console wordcloud_app.py
   ```

2. Check the build warnings:
   ```bash
   pyinstaller --log-level=WARN wordcloud_app.spec
   ```

3. Test in a clean environment without Python installed

## Distribution

### Preparing for Distribution

1. **Test thoroughly** on target platforms
2. **Code signing** (recommended for Windows/macOS)
3. **Create installer** using:
   - Windows: Inno Setup, NSIS, or MSI
   - macOS: DMG with create-dmg
   - Linux: AppImage, Snap, or Flatpak

4. **Documentation** should include:
   - System requirements
   - Installation instructions
   - Known limitations
   - License information

### File Size Optimization

To reduce executable size:
1. Use `--onedir` mode
2. Exclude test files: `--exclude-module=test`
3. Strip debug symbols: `--strip`
4. Use UPX with maximum compression: `--upx-dir=/path/to/upx`

## Version Management

Update version information in:
1. `wordcloud_app.py` (VERSION constant)
2. `wordcloud_app.spec` (version_file)
3. `version.txt` (for Windows version info)

## Continuous Integration

### GitHub Actions Workflows

The project includes automated build workflows:

1. **Build Release** (`.github/workflows/build-release.yml`)
   - Triggers on version tags (e.g., `v1.1.0`)
   - Creates Windows executable
   - Generates ZIP archive with SHA256 checksums
   - Creates draft GitHub release

2. **Test Build** (`.github/workflows/test-build.yml`)
   - Triggers on pushes to main branches
   - Validates build process
   - No artifacts produced

To trigger a release:
```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## Support

If you encounter issues:
1. Check the PyInstaller log files in `build/`
2. Run with `--debug` flag
3. Test with `--onedir` first before `--onefile`
4. Verify all dependencies are installed

## License

Ensure your distribution complies with all dependency licenses. Major dependencies:
- ttkbootstrap: MIT License
- wordcloud: MIT License
- matplotlib: PSF License
- Pillow: HPND License

Remember to include license files in your distribution.