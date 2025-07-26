# WordCloud Magic - Help & Documentation

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Input Tab](#input-tab)
- [Filters Tab](#filters-tab)
- [Style Tab](#style-tab)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Configuration & Settings](#configuration--settings)
- [Troubleshooting](#troubleshooting)
- [Tips & Best Practices](#tips--best-practices)

## Overview

WordCloud Magic is a modern word cloud generator with a beautiful interface and powerful features. Create stunning visualizations from your text documents with advanced filtering, styling, and export options.

Word clouds are visual representations of text data where the size of each word indicates its frequency or importance. They're perfect for:
- Visualizing key themes in documents
- Creating engaging presentations
- Analyzing text patterns
- Making artistic text displays
- Summarizing large amounts of text at a glance

### Key Features
- **Multiple input formats**: PDF, DOCX, PPTX, TXT
- **Advanced filtering**: Word length and forbidden words
- **16 color schemes** with live preview
- **Custom shape masks** from images or text
- **Transparent backgrounds** (RGBA mode)
- **Auto-save configuration**
- **Debug mode** for troubleshooting

## Getting Started

This section will guide you through the basic workflow of creating your first word cloud. WordCloud Magic is designed to be intuitive, but understanding the basic steps will help you create better visualizations faster.

### Quick Start
1. **Load Text**: Select files or paste text in the Input tab
2. **Apply Filters**: Adjust word length and forbidden words in Filters tab
3. **Choose Style**: Select colors, masks, and canvas settings in Style tab
4. **Generate**: Click "Generate Word Cloud" button
5. **Save**: Export as PNG, JPEG, or SVG

### Interface Overview

The application uses a tabbed interface:

- **Input Tab**: Load and manage text sources
- **Filters Tab**: Control which words appear
- **Style Tab**: Customize appearance and layout

The tabs follow a logical workflow order, but you can switch between them at any time.

## Input Tab

The Input Tab is where you begin your word cloud journey. This is where you'll load the text that will be transformed into a beautiful visualization. WordCloud Magic supports multiple input methods to suit different workflows.

### Working Folder
- Click "Browse" to select a folder containing your documents
- Supported formats: `.txt`, `.pdf`, `.docx`, `.pptx`
- The file list shows all compatible files in the selected folder

### File Selection
- **Select All**: Check all files in the list
- **Select None**: Uncheck all files
- **Individual Selection**: Click checkboxes for specific files
- Click "Load Selected Files" to process chosen files

### Direct Text Input
- Paste or type text directly into the text area
- Click "Use Pasted Text" to use this instead of files
- Useful for quick tests or text from other sources

### Status Messages
- Green ✓ = Success
- Blue ℹ = Information
- Yellow ⚠ = Warning
- Red ✗ = Error

## Filters Tab

The Filters Tab gives you precise control over which words appear in your word cloud. Proper filtering is crucial for creating meaningful visualizations that highlight the most important content while removing noise and common words that don't add value.

### Word Length Filter
Control the length of words that appear in your cloud:

- **Minimum Length** (3-50 characters)
  - Default: 3
  - Filters out very short words like "a", "an", "it"
  
- **Maximum Length** (3-50 characters)
  - Default: 30
  - Filters out extremely long words or URLs

### Forbidden Words
Exclude specific words from your word cloud:

- **Default List**: 140+ common English stop words
- **Add Words**: Type new words on separate lines
- **Reset Button**: Restore the default forbidden words
- **Update Button**: Apply your changes

The forbidden words list includes:
- Articles (a, an, the)
- Pronouns (he, she, it, they)
- Prepositions (in, on, at, to)
- Conjunctions (and, or, but)
- Common verbs (is, are, was, have)

## Style Tab

The Style Tab is where your word cloud comes to life visually. This comprehensive styling system allows you to create word clouds that match your brand, presentation theme, or artistic vision. Every visual aspect can be customized to create the perfect look.

### Color Settings

#### Color Mode
Choose how colors are applied to your word cloud:

1. **Single Color**
   - All words use the same color
   - Click color preview to choose
   
2. **Preset Gradient**
   - Choose from 16 beautiful color schemes:
     - Viridis, Ocean, Fire, Sunset
     - Forest, Royal, Autumn, Winter
     - Plasma, Inferno, Magma, Twilight
     - Rainbow, Pastel, Neon, Earth
   
3. **Custom Gradient**
   - Add up to 10 custom colors
   - Click "+" to add colors
   - Click "×" to remove colors
   - Drag to reorder (if supported)

### Mask Settings

Masks define the shape of your word cloud. Instead of a simple rectangle, you can create word clouds in any shape - from company logos to creative designs. This feature transforms basic word clouds into engaging visual art.

#### Mask Types

1. **No Mask**
   - Standard rectangular word cloud
   - Words fill the entire canvas

2. **Image Mask**
   - Use any image as a shape template
   - Supported formats: PNG, JPG, JPEG, BMP, GIF
   - White areas = words appear
   - Black areas = no words
   - Best results with high contrast images

3. **Text Mask**
   - Create word clouds in the shape of text
   - Customizable font, size, bold, italic
   - Great for logos or titles

#### Contour Settings
When using masks, add an outline:
- **Width**: 0-10 pixels (0 = no outline)
- **Color**: Click to choose outline color

### Word Orientation
- **Prefer Horizontal**: 0-100%
  - 0% = All words vertical
  - 50% = Mixed orientation
  - 100% = All words horizontal
  - Default: 90%

### Other Settings

#### Maximum Words
- Range: 10-500 words
- Default: 200
- More words = denser cloud
- Fewer words = cleaner look

#### Computation Scale

This technical setting balances generation speed with placement quality. Most users can leave this at the default, but it's useful when working with very large texts or when you need quick previews.

- Range: 1-10
- Default: 1
- Higher = faster generation but coarser placement
- Lower = slower generation but better quality
- Use 2-3 for quick previews while designing
- Use 1 for final high-quality exports

### Canvas Settings

Canvas settings control the overall dimensions and background of your word cloud. These settings are important for ensuring your word cloud looks great whether it's displayed on screen, printed, or used in presentations.

#### Canvas Size
- **Width**: 400-4000 pixels
- **Height**: 300-4000 pixels
- **Presets**: Quick buttons for common sizes
  - HD (1920×1080)
  - Square (1080×1080)
  - 4K (3840×2160)
- **Keep Ratio**: Lock aspect ratio when resizing

#### Background
- **RGB Mode**: Solid color background
- **RGBA Mode**: Transparent background
- Click color preview to change background color

## Keyboard Shortcuts

Keyboard shortcuts help you work faster and more efficiently. These shortcuts provide quick access to common functions without navigating through menus.

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open/Import Configuration |
| Ctrl+S | Save/Export Configuration |
| Ctrl+G | Generate Word Cloud |
| Ctrl+E | Export/Save Image |
| Ctrl+R | Reset to Defaults |
| F1 | Show Help |
| Ctrl+Q | Quit Application |

## Configuration & Settings

WordCloud Magic's configuration system ensures your preferred settings are preserved between sessions. This powerful feature allows you to maintain consistency across projects, share settings with team members, and quickly switch between different configuration profiles for various use cases.

WordCloud Magic automatically saves and loads your settings from `configs/wordcloud_config.json`.

### Complete Settings Reference

**INPUT SETTINGS**
- `working_directory` - Folder path containing your documents

**FILTER SETTINGS**
- `min_length` (3-50) - Minimum word length to include
- `max_length` (3-50) - Maximum word length to include  
- `forbidden_words` - List of words to exclude

**COLOR SETTINGS**
- `color_mode` - "single", "preset", or "custom"
- `color_scheme` - Name of selected preset gradient
- `single_color` - Hex color for single color mode
- `custom_colors` - Array of hex colors for custom gradients

**STYLE SETTINGS**
- `prefer_horizontal` (0.0-1.0) - Word orientation preference
- `max_words` (10-500) - Maximum number of words to display
- `scale` (1-10) - Quality vs performance tradeoff

**CANVAS SETTINGS**
- `canvas_width` (400-4000) - Canvas width in pixels
- `canvas_height` (300-4000) - Canvas height in pixels
- `background_color` - Canvas background color (hex)
- `rgba_mode` - Enable transparent background

**MASK SETTINGS**
- `mask_type` - "no_mask", "image_mask", or "text_mask"
- `image_mask_file_path` - Path to mask image
- `text_mask_text` - Text for text mask
- `text_mask_font` - Font family for text mask
- `text_mask_size` (10-2000) - Font size for text mask
- `text_mask_bold` - Bold text mask
- `text_mask_italic` - Italic text mask
- `contour_width` (0-10) - Mask outline thickness
- `contour_color` - Mask outline color (hex)

**UI SETTINGS**
- `theme` - UI theme name

### Import/Export Configuration
- **Export**: File menu → Export Configuration
- **Import**: File menu → Import Configuration
- Configurations are saved as JSON files
- Share configurations with others

### Debug Mode
Run with debug flag for detailed logging:
```bash
python wordcloud_app.py --debug
```

Debug logs are saved to: `logs/wordcloud_debug_YYYYMMDD_HHMMSS.log`

## Troubleshooting

Even the best software can encounter issues. This troubleshooting guide helps you quickly resolve common problems and understand error messages. Most issues have simple solutions, and this section will guide you through them.

### Common Issues

**"No text loaded" error**
- Ensure files are selected or text is pasted
- Check that files contain extractable text
- PDF files must have text layer (not scanned images)

**Words not appearing**
- Check minimum length filter (default: 3)
- Verify word isn't in forbidden list
- Ensure maximum words setting is high enough

**Mask not working**
- Use high contrast images (black and white work best)
- White areas = where words appear
- Ensure image file exists and is readable

**Slow generation**
- Reduce canvas size
- Lower maximum words count
- Increase computation scale
- Close other applications

**Colors look wrong**
- Check color mode setting
- Verify theme isn't affecting preview
- Try different color schemes

### Error Messages

| Error | Solution |
|-------|----------|
| "Please select files or paste text" | Load content in Input tab first |
| "No supported files found" | Check folder contains PDF/DOCX/PPTX/TXT files |
| "Failed to generate word cloud" | Check debug log for details |
| "Failed to save image" | Ensure write permissions for save location |

## Tips & Best Practices

These tips and best practices come from extensive testing and user feedback. Following these guidelines will help you create professional-looking word clouds efficiently and avoid common pitfalls.

### For Best Results
1. **Text Preparation**
   - Remove headers/footers from documents
   - Check for OCR quality in PDFs
   - Combine related documents for better word frequency

2. **Mask Images**
   - Use simple, bold shapes
   - Convert to black and white first
   - Higher resolution = better detail

3. **Color Selection**
   - Dark backgrounds work well with bright colors
   - Use high contrast for readability
   - Match colors to your presentation theme

4. **Performance**
   - Start with smaller canvas for testing
   - Increase size for final export
   - Use computation scale 2-3 for faster previews

### Creative Ideas
- **Logo Masks**: Use company logos as masks
- **Text Masks**: Spell out event names or titles  
- **Themed Colors**: Match brand colors
- **Transparent Backgrounds**: Overlay on presentations
- **Multiple Languages**: Works with Unicode text

### Export Tips
- **PNG**: Best for web and presentations
- **JPEG**: Smaller files, no transparency
- **SVG**: Vector format, infinitely scalable

---

## Need More Help?

If you're still having trouble or need assistance with advanced features, here are additional resources:

- **Report Issues**: [GitHub Issues](https://github.com/anthropics/claude-code/issues)
- **View Logs**: Check `logs/` folder for debug information
- **Reset Settings**: File menu → Reset to Defaults
- **Configuration Files**: Edit `configs/wordcloud_config.json` directly for advanced customization
- **Font Issues**: Restart the application if newly installed fonts don't appear

Remember that WordCloud Magic is designed to be intuitive. If something seems complicated, there's probably an easier way to do it. Don't hesitate to experiment - you can always reset to defaults!

---

*WordCloud Magic - Beautiful word clouds made simple*

Created with ❤️ for data visualization enthusiasts, presenters, and creative professionals.