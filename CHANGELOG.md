# Changelog

All notable changes to WordCloud Magic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2] - 2025-08-01

### Fixed
- **GitHub Actions**: Fixed unnecessary UPX download - now uses bundled UPX from repository
- **Source Releases**: Cleaned up source archive to exclude all build artifacts (*.exe, *.zip, version files)
- **Build Process**: Simplified workflow by removing redundant UPX setup steps

### Changed
- **CI/CD Pipeline**: Optimized to use existing resources instead of downloading dependencies

## [0.3.1] - 2025-08-01

### Added
- **Author Attribution**: Added "Created by Ghost-ng | © 2025" footer to main window
- **Enhanced About Dialog**: Now displays author name and GitHub repository link
- **Executable Metadata**: Windows exe files now include proper version information:
  - Company Name: Ghost-ng
  - File Description: WordCloud Magic - Modern Word Cloud Generator
  - Copyright: © 2025 Ghost-ng. All rights reserved.
- **Professional Build Script**: New `build_exe.py` with automatic version management
- **Build Artifacts Exclusion**: Added `.gitattributes` to exclude build files from source releases

### Changed
- **GitHub Actions**: Updated workflow to use unified `build_exe.py` script
- **PyInstaller Configuration**: Optimized spec file for better compression and metadata handling
- **Version Resource**: Properly formatted version information following PyInstaller best practices

### Fixed
- **Source Releases**: Build artifacts (exe files) no longer included in GitHub source code archives
- **Build Process**: Improved handling of file locks in OneDrive-synced directories
- **Theme Compatibility**: Footer text color now adjusts properly with light/dark theme changes

## [0.3.0] - 2025-01-30

### Changed
- **App Data Location**: Configs and logs now stored in platform-specific directories:
  - Windows: `%APPDATA%/WordCloudMagic/`
  - Linux/Mac: `~/.wordcloudmagic/`
- Automatic migration of existing configs to new location on first run

### Fixed
- Fixed AttributeError when outline_width_scale is None in RGBA mode switching

## [0.2.0] - 2025-01-30

### Added
- **Recursive File Search**: Added subfolder depth control (0-10 levels) with spinbox selector
- **Refresh Button**: Manual file list refresh with ↻ button in working folder section
- **File Loading Progress**: Progress bar appears when loading file contents
- **Folder Search Progress**: Progress bar shows during recursive file searches
- **Improved File Display**: Files in subdirectories shown with 📁 icon, root files with 📄 icon

### Fixed
- **Toast Notifications**: Fixed inconsistent sizing - all toasts now have uniform 400px width
- **Toast Height Issue**: Capped maximum toast height to prevent oversized notifications
- **Thread Safety**: File operations now run in background threads to prevent UI freezing

### Changed
- File paths now display relative to working directory for better readability
- Toast notifications repositioning improved for better stack management
- Progress indicators use indeterminate mode with striped styling
- **App Data Location**: Configs and logs now stored in platform-specific directories:
  - Windows: `%APPDATA%/WordCloudMagic/`
  - Linux/Mac: `~/.wordcloudmagic/`
- Automatic migration of existing configs to new location on first run

## [0.1.0] - 2025-01-29

### Initial Release
- Multiple input sources (PDF, DOCX, PPTX, TXT)
- Advanced word filtering with min/max length
- Customizable forbidden words list
- 16+ built-in color schemes
- Support for image and text masks
- Adjustable canvas dimensions
- RGB/RGBA mode support
- Export to PNG, JPEG, and SVG
- Modern UI with 18 themes
- Auto-save configuration
- Built-in help documentation