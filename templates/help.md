# WordCloud Magic {VERSION} - Comprehensive Help Guide

## Getting Started

1. **Input Tab**: Load text from files or paste directly
2. **Filters Tab**: Set word length limits and forbidden words  
3. **Style Tab**: Choose colors, shapes, and appearance
4. **Canvas Tab**: Configure output dimensions and transparency
5. Click **"Generate Word Cloud"** to create
6. Save your creation in PNG, JPEG, or SVG format

---

## Input Tab Features

### Working Directory
- Select the folder containing your documents
- The file list will update to show available files

### File Selection
- Multi-select files from the list using Ctrl+Click or Shift+Click
- Supported formats: PDF, DOCX, PPTX, TXT
- Selected files are highlighted in blue

### Direct Text Input
- Paste or type text directly in the text area
- Use this for quick word clouds from clipboard content

### Load Options
- **"Load Selected Files"**: Processes all selected files
- **"Use Pasted Text"**: Uses the text from the text area

### Status Display
- Shows count of loaded files
- Displays total word count after processing

---

## Filters Tab Features

### Word Length Filters
- **Minimum Length**: Filter out short words (default: 3)
- **Maximum Length**: Filter out long words (default: 30)
- Real-time slider adjustment with value display
- Prevents single letters and extremely long strings

### Forbidden Words
- Pre-populated with common English stop words
- Add custom words to exclude (one per line)
- Click **"Update Forbidden Words"** to apply changes
- Shows total count of forbidden words
- Useful for removing project-specific jargon

---

## Style Tab Features

### Color Schemes
Three color modes available via radio button selection:

#### 1. Single Color Mode
- Click the color picker button to choose any solid color
- Live preview of selected color
- Best for minimalist designs

#### 2. Preset Gradients Mode
- 30+ built-in gradients organized in a 4-column grid:
  - **Standard**: Viridis, Plasma, Inferno, Magma, Cividis
  - **Classic**: Cool, Hot, Spring, Summer, Autumn, Winter
  - **Special**: Rainbow, Ocean, Spectral, Jet, Turbo
  - **Custom**: Sunset Sky, Deep Ocean, Forest, Fire, Cotton Candy, Fall Leaves, Berry, Northern Lights, Coral Reef, Galaxy
  - **Themed**: Solarized Dark/Light, Rose Pine, Grape, Dracula, Gruvbox, Monokai, Army, Air Force, Cyber, Navy, Hacker

#### 3. Custom Gradient Mode
- Create gradients with 2 or more colors
- **"Choose"** button for each color stop
- **"Add Color"** / **"Remove Color"** buttons for dynamic gradients
- Live gradient preview updates automatically

### Shape & Appearance

#### Mask Options (Tabbed Interface)

##### No Mask
- Standard rectangular word cloud
- Full canvas utilization
- Words fill the entire canvas area

##### Image Mask
- Load PNG, JPG, JPEG, BMP, GIF images
- White pixels = areas where words appear
- Black/colored pixels = excluded areas
- Visual preview of loaded mask
- **Contour Options**:
  - Enable/disable contour outline
  - Adjustable contour width (1-10 pixels)
  - Custom contour color picker

##### Text Mask
- Create mask from typed text
- Font selection from system fonts
- Live font preview in actual font
- Adjustable font size (10-500)
- Bold option for thicker text
- Width/Height sliders with lock aspect ratio
- Real-time mask preview

### Word Orientation
- **Prefer Horizontal** slider (0-100%)
- 0% = All words vertical
- 100% = All words horizontal
- Default: 90% horizontal

### Other Settings
- **Maximum Words**: Control word cloud density (1-2000)
- **Scale**: Performance vs quality tradeoff (0.1-5.0)
- **Letter Thickness**: Make words bolder or thinner (0.1-2.0)

---

## Canvas Tab Features

### Canvas Dimensions
- **Width**: 100-3000 pixels
- **Height**: 100-3000 pixels
- **Presets**: 
  - 800×600 (Web)
  - 1024×768 (Standard)
  - 1920×1080 (Full HD)
  - 1000×1000 (Square)

### Color Mode
- **RGB**: Solid background colors
- **RGBA**: Transparent background support (for overlays)

### Background Color
- Color picker for custom backgrounds
- Only active in RGB mode
- Visual preview of selected color

---

## Preview Area

- Real-time canvas preview with dimensions
- **Generate Word Cloud** button
- **Save Image** button (enabled after generation)
- **Clear** button to reset canvas
- Progress indicator during generation
- Automatic scaling for large canvases

---

## File Menu Options

### Configuration Management
- **Load Config**: Load saved settings from JSON file
- **Save Config As...**: Save current settings to a new file
- **Save Config**: Quick save to wordcloud_config.json
- **Reset**: Restore all settings to defaults (with confirmation)

### Configuration Includes:
- All filter settings
- Color mode and selections
- Custom gradient colors
- Canvas dimensions and background
- Mask settings
- Word orientation and density
- Scale and thickness settings
- Working directory
- Theme selection

### Other Options
- **Help**: Show this comprehensive guide in your browser
- **Exit**: Close the application (auto-saves configuration)

---

## Theme Selection

18 available UI themes via dropdown menu:

### Light Themes
- Cosmo, Flatly, Journal, Litera, Lumen, Minty, Pulse, Sandstone, United, Yeti

### Dark Themes
- Darkly, Cyborg, Superhero, Solar, Vapor

---

## Tips & Best Practices

### For Best Results
- Use large, bold fonts for text masks
- High-contrast mask images work best (pure black & white)
- Increase canvas size for print-quality exports
- Use RGBA mode for overlays and transparent backgrounds

### Performance Tips
- Lower scale = faster generation
- Higher scale = better quality
- Reduce max words for faster processing with large texts

### Workflow Tips
- Save configurations for consistent branding
- The app auto-saves/loads config from 'wordcloud_config.json'
- Use the working directory feature to quickly access project files

---

## Troubleshooting

### Common Issues
- **Fonts not appearing**: Restart the app to refresh font list
- **Slow performance**: Reduce max words or scale setting
- **Mask not working**: Ensure image has clear white areas for word placement
- **Text mask slow**: Complex fonts may take longer to generate

### File Format Issues
- **PDF errors**: Some PDFs may have text extraction issues
- **DOCX/PPTX**: Only text content is extracted, not images
- **Large files**: May take time to process, watch the progress bar

---

## Advanced Features

### Command Line Options
```bash
# Run with debug logging
python wordcloud_app.py --debug
# Creates log file: logs/wordcloud_debug_YYYYMMDD_HHMMSS.log
```

### Custom Fonts
The app automatically detects system fonts. For best results with text masks:
- Use TrueType (.ttf) or OpenType (.otf) fonts
- Bold, display fonts work better than thin fonts
- Simple fonts render faster than complex ones

---

## Debug Mode

- Toggle debug mode using the checkbox in the bottom-right corner
- When enabled, detailed logs are saved to the `logs` directory
- Log files include timestamps and are named: `wordcloud_debug_YYYYMMDD_HHMMSS.log`
- Useful for troubleshooting issues

---

## Configuration Files

The application saves settings in two files:
- **configs/default.json**: Main application settings
- **configs/theme.json**: Theme and dark mode preferences

When running as an executable, these files are created in your current working directory.

---

## About

**WordCloud Magic** - A modern, feature-rich word cloud generator

Created by [@ghost-ng](https://github.com/ghost-ng)

Version 0.1.0

For the latest updates and release notes, check the [Releases page](https://github.com/ghost-ng/wordcloudmagic/releases).

---

## Support

For issues, feature requests, or contributions, visit the [GitHub repository](https://github.com/ghost-ng/wordcloudmagic).