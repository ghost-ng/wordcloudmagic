# WordCloud Magic - Modern Word Cloud Generator

A beautiful, modern word cloud generator built with Python and ttkbootstrap, featuring a clean interface with excellent readability and professional styling.

## Features

- **Multiple Input Sources**:
  - Load text from PDF, DOCX, PPTX, and TXT files
  - Paste text directly into the application
  - Select multiple files from a working directory

- **Advanced Filtering**:
  - Adjustable minimum and maximum word length filters
  - Customizable forbidden words list
  - Pre-populated with common stop words

- **Style Customization**:
  - 22+ color schemes including new themes: Volcano, Lilac, Cyberpunk, Tron, The Grid, Fiber
  - Support for image masks (PNG, JPG, etc.) and text masks with custom fonts
  - Outline options with adjustable width and color (when using masks)
  - Letter thickness and spacing controls for text masks
  - Word orientation control (0-100% horizontal preference)
  - Visual mask preview with borders

- **Canvas Options**:
  - Adjustable canvas size (width and height)
  - RGB mode for solid backgrounds
  - RGBA mode for transparent backgrounds
  - Custom background color picker
  - Dynamic preview resizing

- **Modern UI**:
  - Clean, light theme with Bootstrap-inspired design
  - Dynamic theme selector with 18 different themes and dark mode toggle
  - Organized tabbed interface with icons
  - Message system with success/info/warning/error notifications
  - Toast notifications with text wrapping for long messages
  - Progress indicators during generation
  - Responsive, resizable layout with improved scrollable sections
  - All meters standardized with descriptions below
  - Improved font selection with visual preview

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python wordcloud_app.py
   
   # Run with debug mode for detailed logging
   python wordcloud_app.py --debug
   ```

2. **Message System**:
   - Look for status messages at the top of the interface
   - Green (✓) = Success, Blue (ℹ) = Info, Yellow (⚠) = Warning, Red (✗) = Error
   - Messages auto-dismiss after 5 seconds (except errors)
   - Click the × button to manually dismiss any message

3. **Input Tab**:
   - Select a working folder containing your documents
   - Choose files from the list OR paste text directly
   - Click "Load Selected Files" or "Use Pasted Text"
   - Success messages show file count and total word count

4. **Filters Tab**:
   - Adjust word length limits using the sliders
   - Add/remove forbidden words in the text area
   - Click "Update Forbidden Words" to apply changes

5. **Style Tab**:
   - Select a color scheme from the radio buttons
   - Choose a mask image for custom shapes (enables contour options)
   - Adjust contour width and color when using masks
   - Set word orientation preference (horizontal vs vertical)
   - Configure canvas size and background options
   - Switch between RGB (solid) and RGBA (transparent) modes

6. **Theme Selection**:
   - Use the dropdown in the top-right to change the app theme
   - Choose from 18 different themes (light and dark options)

7. Click "Generate Word Cloud" to create your visualization
8. Save the result using "Save Image" (supports PNG, JPEG, and SVG formats)

## Supported File Formats

### Input Formats:
- **Text**: .txt
- **PDF**: .pdf
- **Word**: .docx
- **PowerPoint**: .pptx

### Mask Images:
- **Raster**: .png, .jpg, .jpeg, .bmp, .gif

### Export Formats:
- **PNG**: Best for web and presentations
- **JPEG**: Good for photos and complex backgrounds
- **SVG**: Vector format for scalable graphics

## Configuration & Settings

WordCloud Magic saves and loads settings automatically:
- Main settings: `configs/wordcloud_config.json`
- Theme preferences: `configs/theme.json`

All settings are preserved between sessions.

### Complete Settings Reference

**INPUT SETTINGS:**
- `working_directory` - Folder path containing your documents

**FILTER SETTINGS:**
- `min_length` (3-50) - Minimum word length to include
- `max_length` (3-50) - Maximum word length to include  
- `forbidden_words` - List of words to exclude (140+ common English stop words by default)

**COLOR SETTINGS:**
- `color_mode` - Color selection mode: "single", "preset", or "custom"
- `color_scheme` - Name of selected preset gradient (e.g., "Viridis", "Ocean", "Fire")
- `single_color` - Hex color for single color mode (e.g., "#0078D4")
- `custom_colors` - Array of hex colors for custom gradients

**STYLE SETTINGS:**
- `prefer_horizontal` (0.0-1.0) - Word orientation preference (0=all vertical, 1=all horizontal)
- `max_words` (1-2000) - Maximum number of words to display
- `scale` (0.1-5.0) - Quality vs performance tradeoff (higher=better quality)

**CANVAS SETTINGS:**
- `canvas_width` (400-4000) - Canvas width in pixels
- `canvas_height` (300-4000) - Canvas height in pixels
- `background_color` - Canvas background color in hex format
- `rgba_mode` - Enable transparent background (true/false)

**MASK SETTINGS:**
- `mask_type` - Type of mask: "no_mask", "image_mask", or "text_mask"
- `image_mask_file_path` - Full path to mask image file
- `text_mask_text` - Text to use for text mask
- `text_mask_font` - Font family name for text mask
- `text_mask_font_size` (10-2000) - Font size for text mask
- `text_mask_bold` - Bold text mask (true/false)
- `text_mask_italic` - Italic text mask (true/false)
- `text_mask_words_per_line` (1-10) - Words per line in text masks
- `letter_thickness` (0-5) - Stroke thickness for text mask letters
- `letter_spacing` (0-5) - Space between letters in text mask
- `outline_width` (0-30) - Mask outline thickness in pixels
- `outline_color` - Mask outline color in hex format

**UI SETTINGS:**
- `theme` - UI theme name (e.g., "cosmo", "darkly", "superhero")
- `default_forbidden` - Default forbidden words list (internal use)

### Debug Mode

Run with `--debug` flag to enable detailed logging:
```bash
python wordcloud_app.py --debug
```

Debug logs are saved to `logs/wordcloud_debug_YYYYMMDD_HHMMSS.log`

## Tips

- Use high-contrast mask images for best results
- White areas in mask images will be filled with words
- Adjust word length filters to focus on meaningful terms
- Try different color schemes to match your presentation style
- Use RGBA mode for transparent backgrounds when overlaying on other images
- Increase canvas size for higher resolution exports
- Set prefer horizontal to 100% for title-style word clouds
- Use contour options to make masked word clouds pop
- Configuration saves automatically on exit if you choose "Yes"
- Reset function restores defaults without saving

## Help Documentation

WordCloud Magic includes comprehensive built-in help documentation. Access it through:
- **File menu → Help** - Opens the help documentation in your web browser
- **F1 key** - Quick keyboard shortcut for help

The help system features:
- Interactive HTML documentation with smooth navigation
- Complete settings reference with value ranges
- Keyboard shortcuts guide
- Troubleshooting tips
- Visual examples and best practices

## Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- See requirements.txt for additional packages

## Theme Options

The app uses ttkbootstrap themes with a theme selector in the UI. Available themes include:

**Light Themes:**
- Cosmo (default) - Clean and modern
- Flatly - Minimalist design
- Litera - Literary and elegant  
- Minty - Fresh green accents
- Lumen - Light and airy
- Sandstone - Warm earth tones
- Yeti - Cool blue theme
- Pulse - Purple accents
- United - Orange highlights

**Dark Themes:**
- Darkly - Dark and elegant
- Cyborg - High-tech cyberpunk
- Vapor - Vaporwave aesthetic
- Superhero - Bold and dramatic
- Solar - Solarized dark
- Rose Pine - Soft dark theme
- Gruvbox - Retro warm dark
- Dracula - Classic dark purple
- Monokai - Developer favorite