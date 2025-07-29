# Changelog

All notable changes to WordCloud Magic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-29

### Added
- 6 new color schemes: Volcano, Lilac, Cyberpunk, Tron, The Grid, Fiber
- Letter thickness control for text masks (0-5 scale)
- Letter spacing control for text masks (0-5 scale)
- Dark mode toggle in UI
- Mouse wheel scrolling support for font selection listbox
- Automatic text wrapping for toast notifications
- Border display on text mask previews
- Reset button for outline width meter
- GitHub Actions workflows for automated builds

### Changed
- Moved Canvas Settings section above Word Orientation in UI
- All meter descriptions now appear below meters (previously above)
- Improved font selection with LabelFrame border
- All scrollbars now use ttkbootstrap primary-round style
- Theme preferences saved separately in `configs/theme.json`
- Fixed outline width parameter for wordcloud library (contour_width)

### Fixed
- Toast messages no longer truncate long text
- Placeholder text properly removed when generating word cloud
- Contour width meter can now return to 0
- Text mask preview updates when canvas dimensions change
- Dark mode initialization error on startup
- Scrolling behavior in style tab notebook
- Letter thickness meter not updating preview

## [1.0.0] - TBD

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