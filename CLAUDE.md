# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python wordcloud_app.py

# Run with debug mode to see errors and debug info in console and save to log file
python wordcloud_app.py --debug
# Creates a debug log file in the logs directory: logs/wordcloud_debug_YYYYMMDD_HHMMSS.log
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Virtual Environment
The project uses a virtual environment located in the `venv` directory. Activate it with:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

## Architecture

### Main Application
The project is a single-file Tkinter application (`wordcloud_app.py`) that creates word clouds from various input sources. The architecture follows these patterns:

1. **ModernWordCloudApp** (line 171): Main application class that manages the GUI and orchestrates all functionality
2. **FontListbox** (line 30): Custom widget for font selection with visual preview
3. **Configuration Management**: Uses `configs/wordcloud_config.json` for persistent settings storage

### Key Components

- **UI Framework**: Built with ttkbootstrap for modern theming
- **Tab-based Interface**: Organized into Input, Filters, and Style tabs
- **Message System**: Toast notifications and persistent message display for user feedback
- **File Support**: PDF, DOCX, PPTX, and TXT file parsing
- **Image Export**: PNG, JPEG, and SVG output formats

### External Dependencies
- `ttkbootstrap`: Modern UI theming
- `wordcloud`: Core word cloud generation
- `matplotlib`: Visualization backend
- `Pillow`: Image processing
- `PyPDF2`: PDF text extraction
- `python-docx`: Word document parsing
- `python-pptx`: PowerPoint parsing

### Configuration Schema
The application uses two configuration files:
1. `configs/wordcloud_config.json` - Main settings:
   - forbidden_words: List of words to exclude
   - color settings: mode, scheme, custom colors
   - UI preferences: working directory
   - Style settings: mask, outline, orientation
   - Canvas settings: width, height, background

2. `configs/theme.json` - Theme preferences:
   - theme: Current UI theme name
   - dark_mode: Dark mode toggle state

### Threading Model
Long-running operations (word cloud generation) run in separate threads to keep the UI responsive. Look for `threading.Thread` usage in the generate methods.

### Recent UI/UX Improvements
- Toast messages with automatic text wrapping
- Fixed outline width parameter (use `contour_width` for WordCloud library)
- Added 6 new color presets: Volcano, Lilac, Cyberpunk, Tron, The Grid, Fiber
- Improved font selection with LabelFrame
- Fixed scrolling in font listbox and style tab
- Moved Canvas Settings above Word Orientation
- All scrollbars use ttkbootstrap primary-round style
- Fixed dark_mode initialization order
- Letter thickness functionality for text masks using stroke_width
- All meter descriptions positioned below meters for consistency

### Building Executable
Use `build_exe.py` to create a standalone executable:
```bash
python build_exe.py --clean  # Clean and build
python build_exe.py --onedir # Create directory distribution
python build_exe.py --debug  # Build with debug info
```