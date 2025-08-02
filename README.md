# WordCloud Magic 🪄

![Version](https://img.shields.io/badge/version-0.3.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

Create stunning word clouds from your documents with a beautiful, modern interface. Load PDFs, apply custom masks, and export in multiple formats - all with just a few clicks!

## ✨ Features

**📄 Input** - PDF, DOCX, PPTX, TXT • Multi-file selection • Folder scanning  
**🎨 Style** - 22+ color schemes • Image/text masks • Custom fonts • Transparency  
**🛠️ Filter** - Smart word filtering • 140+ stop words • Length controls  
**💻 Interface** - 18 themes • Live preview • Toast notifications • Responsive design

## 🚀 Quick Start

**Windows Users:** Download from [Releases](https://github.com/ghost-ng/wordcloudmagic/releases) - no installation needed!

**Run from Source:**
```bash
git clone https://github.com/ghost-ng/wordcloudmagic.git
cd wordcloudmagic
pip install -r requirements.txt
python wordcloud_app.py
```

## 📖 Usage

1. **Load** - Select files or paste text in the Input tab
2. **Filter** - Adjust word lengths and forbidden words in the Filters tab  
3. **Style** - Choose colors, masks, and fonts in the Style tab
4. **Generate** - Click "Generate Word Cloud" to create your visualization
5. **Save** - Export as PNG

💡 **Pro tip:** Run with `--debug` flag for detailed logging

## 📁 Supported Formats

**Input:** PDF, DOCX, PPTX, TXT  
**Masks:** PNG, JPG, JPEG, BMP, GIF  
**Export:** PNG

## ⚙️ Configuration

Settings are automatically saved between sessions:
- **Windows:** `%APPDATA%/WordCloudMagic/`
- **Linux/Mac:** `~/.wordcloudmagic/`

**Key Settings:**
- Word filters (length, forbidden words)
- Colors (single, preset, custom gradients)
- Style (orientation, max words, fonts)
- Canvas (size, background, transparency)
- Masks (image/text, outline, effects)

## 💡 Tips & Tricks

• **Masks:** Use high-contrast images - white areas fill with words  
• **Quality:** Increase canvas size for higher resolution exports  
• **Style:** Set horizontal to 100% for title-style clouds  
• **Transparency:** Enable RGBA mode for overlay effects

## 📚 Help & Documentation

Access built-in help via **File → Help** for:
- Interactive documentation
- Settings reference
- Keyboard shortcuts
- Troubleshooting

## 📋 Requirements

- Python 3.8+
- Tkinter (included with Python)
- Dependencies in `requirements.txt`

## 🎨 Themes

**Light:** Cosmo, Flatly, Litera, Minty, Lumen, Sandstone, Yeti, Pulse, United  
**Dark:** Darkly, Cyborg, Vapor, Superhero, Solar, Rose Pine, Gruvbox, Dracula, Monokai

## 🆕 What's New (v0.3.2)

- **Author Attribution** - Added footer and enhanced About dialog with author info
- **Build Improvements** - Fixed GitHub Actions to use bundled UPX
- **Cleaner Releases** - Source archives now exclude all build artifacts

## 🔨 Building

```bash
pyinstaller wordcloud_app.spec
```

## 🤝 Contributing

Contributions welcome! Fork, create a feature branch, and submit a PR.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Credits

- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) - Modern UI
- [word_cloud](https://github.com/amueller/word_cloud) - Core engine

---

⭐ Star this repo if you find it useful!