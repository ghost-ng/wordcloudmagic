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
The `configs/wordcloud_config.json` file stores:
- forbidden_words: List of words to exclude
- color settings: mode, scheme, custom colors
- UI preferences: theme, working directory
- Style settings: mask, contour, orientation

### Threading Model
Long-running operations (word cloud generation) run in separate threads to keep the UI responsive. Look for `threading.Thread` usage in the generate methods.

### TODO Items
The codebase has several incomplete methods marked with TODO comments:
- `update_bg_preview()` (line 2740)
- `on_color_mode_change_canvas()` (line 2743)
- `update_contour_color_preview()` (line 2768)

These relate to preview functionality for background and contour color changes.