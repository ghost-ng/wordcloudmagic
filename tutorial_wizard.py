"""
Tutorial Wizard for WordCloud Magic
Interactive guided tour for new users
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import json
import os
from typing import List, Dict, Tuple, Optional, Callable
import logging
import platform

class TutorialStep:
    """Represents a single step in the tutorial"""
    def __init__(self, 
                 title: str,
                 content: str,
                 target_widget: Optional[str] = None,
                 highlight_offset: Tuple[int, int, int, int] = (0, 0, 0, 0),
                 position: str = "center",
                 action: Optional[Callable] = None):
        self.title = title
        self.content = content
        self.target_widget = target_widget  # Widget path to highlight
        self.highlight_offset = highlight_offset  # (left, top, right, bottom) padding
        self.position = position  # Where to show the tooltip: center, right, left, top, bottom
        self.action = action  # Optional action to perform when step is shown

class TutorialWizard:
    """Interactive tutorial wizard with overlay and spotlight effects"""
    
    def __init__(self, app, root):
        self.app = app  # Reference to main WordCloud app
        self.root = root
        self.current_step = 0
        self.steps: List[TutorialStep] = []
        self.overlay_pieces = []
        self.spotlight = None
        self.tooltip = None
        self.is_running = False
        
        # Create tutorial steps
        self._create_tutorial_steps()
        
    def _create_tutorial_steps(self):
        """Define all tutorial steps"""
        self.steps = [
            TutorialStep(
                title="Welcome to WordCloud Magic! 🎨",
                content="Let's take a quick tour to help you create amazing word clouds.\n\n"
                       "This tutorial will guide you through all the key features.\n\n"
                       "You can skip at any time or navigate with the buttons below.",
                position="center"
            ),
            
            TutorialStep(
                title="Input Tab - Loading Your Text",
                content="This is where you load the text for your word cloud.\n\n"
                       "• Click 'Browse' to select a folder with documents\n"
                       "• Choose files from the list (PDF, DOCX, TXT, PPTX)\n"
                       "• Or paste text directly in the text area\n\n"
                       "Try selecting a folder now!",
                target_widget="input_tab",
                highlight_offset=(10, 10, 10, 10),
                position="right",
                action=lambda: self.app.notebook.select(0)  # Switch to Input tab
            ),
            
            TutorialStep(
                title="Working with Files",
                content="Once you've selected a folder:\n\n"
                       "• Use 'Select All' to choose all files\n"
                       "• Or check individual files\n"
                       "• Click 'Load Selected Files' to process them\n\n"
                       "The status area shows loading progress.",
                target_widget="file_list_frame",
                highlight_offset=(5, 5, 5, 5),
                position="right"
            ),
            
            TutorialStep(
                title="Filters Tab - Refining Your Words",
                content="Control which words appear in your cloud:\n\n"
                       "• Set minimum/maximum word length\n"
                       "• Add forbidden words to exclude\n"
                       "• Common words are pre-filtered\n\n"
                       "This helps create cleaner, more meaningful clouds.",
                target_widget="filters_tab",
                highlight_offset=(10, 10, 10, 10),
                position="right",
                action=lambda: self.app.notebook.select(1)  # Switch to Filters tab
            ),
            
            TutorialStep(
                title="Word Length Controls",
                content="Use these sliders to filter words by length:\n\n"
                       "• Minimum length removes short words (a, an, it)\n"
                       "• Maximum length filters very long words or URLs\n\n"
                       "The default settings work well for most cases.",
                target_widget="length_controls",
                highlight_offset=(5, 5, 5, 5),
                position="bottom"
            ),
            
            TutorialStep(
                title="Style Tab - Making It Beautiful",
                content="This is where your creativity shines!\n\n"
                       "• Choose from 16 color schemes\n"
                       "• Add custom shape masks\n"
                       "• Control word orientation\n"
                       "• Adjust canvas size\n\n"
                       "Let's explore the styling options.",
                target_widget="style_tab",
                highlight_offset=(10, 10, 10, 10),
                position="left",
                action=lambda: self.app.notebook.select(2)  # Switch to Style tab
            ),
            
            TutorialStep(
                title="Color Schemes",
                content="Pick a color scheme that matches your style:\n\n"
                       "• Viridis - Scientific and professional\n"
                       "• Ocean - Cool blues and greens\n"
                       "• Fire - Warm reds and oranges\n"
                       "• Rainbow - Full spectrum\n\n"
                       "Click any scheme to see a preview!",
                target_widget="color_scheme_frame",
                highlight_offset=(5, 5, 5, 5),
                position="left"
            ),
            
            TutorialStep(
                title="Shape Masks - Advanced Feature",
                content="Create word clouds in custom shapes!\n\n"
                       "• Use 'Image Mask' for logos or shapes\n"
                       "• Try 'Text Mask' to form words\n"
                       "• Add contours for extra style\n\n"
                       "White areas = where words appear",
                target_widget="mask_frame",
                highlight_offset=(5, 5, 5, 5),
                position="left"
            ),
            
            TutorialStep(
                title="Canvas Settings",
                content="Control the output size and background:\n\n"
                       "• Use presets for common sizes (HD, Square, 4K)\n"
                       "• Enable RGBA for transparent backgrounds\n"
                       "• Perfect for presentations and overlays",
                target_widget="canvas_frame",
                highlight_offset=(5, 5, 5, 5),
                position="top"
            ),
            
            TutorialStep(
                title="Generate Your Word Cloud",
                content="Ready to create? Click this button!\n\n"
                       "• Generation takes a few seconds\n"
                       "• Larger sizes take longer\n"
                       "• Progress bar shows status\n\n"
                       "Your word cloud will appear on the right.",
                target_widget="generate_button",
                highlight_offset=(10, 10, 10, 10),
                position="top"
            ),
            
            TutorialStep(
                title="Preview Canvas",
                content="Your word cloud appears here:\n\n"
                       "• Automatically resizes to fit\n"
                       "• Shows placeholder when empty\n"
                       "• Full resolution is preserved\n\n"
                       "Save your creation with the button below.",
                target_widget="preview_canvas",
                highlight_offset=(10, 10, 10, 10),
                position="left"
            ),
            
            TutorialStep(
                title="Saving Your Work",
                content="Export your word cloud:\n\n"
                       "• PNG - Best for web and presentations\n"
                       "• JPEG - Smaller files, no transparency\n"
                       "• SVG - Vector format, scalable\n\n"
                       "Your settings auto-save for next time!",
                target_widget="save_button",
                highlight_offset=(10, 10, 10, 10),
                position="top"
            ),
            
            TutorialStep(
                title="Configuration & Themes",
                content="Personalize your experience:\n\n"
                       "• Change themes with the dropdown (top-right)\n"
                       "• Import/Export configurations (File menu)\n"
                       "• Press F1 for detailed help\n\n"
                       "All settings save automatically!",
                target_widget="theme_selector",
                highlight_offset=(5, 5, 5, 5),
                position="left"
            ),
            
            TutorialStep(
                title="Tutorial Complete! 🎉",
                content="You're ready to create amazing word clouds!\n\n"
                       "Remember:\n"
                       "• F1 opens the help documentation\n"
                       "• File → Help for detailed guides\n"
                       "• Your settings save automatically\n\n"
                       "Have fun creating!",
                position="center"
            )
        ]
        
        
    def start_tutorial(self):
        """Start the tutorial from the beginning"""
        if self.is_running:
            return
            
        self.is_running = True
        self.current_step = 0
        
        # Create overlay
        self._create_overlay()
        
        # Show first step
        self._show_current_step()
        
    def _create_overlay(self):
        """Create multiple overlay windows to allow interaction with highlighted areas"""
        # Instead of one big overlay, we'll create 4 separate overlays around the spotlight
        # This allows the highlighted area to be clickable
        
        # We'll create these when we have a spotlight
        self.overlay_pieces = []
        
        # Bind to main window movements
        self.root.bind('<Configure>', self._on_main_window_configure)
        
    def _create_center_overlay(self):
        """Create a simple dark overlay for center dialogs"""
        # Clear any existing overlay pieces
        for piece in self.overlay_pieces:
            piece.destroy()
        self.overlay_pieces = []
        
        # Create a single full overlay
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.configure(bg='black')
        overlay.attributes('-alpha', 0.7)
        overlay.attributes('-topmost', True)
        
        # Make it non-interactive on Windows
        if platform.system() == 'Windows':
            overlay.attributes('-disabled', True)
        
        # Position it over the main window
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        self.overlay_pieces.append(overlay)
    
    def _create_overlay_pieces(self, spotlight_x, spotlight_y, spotlight_width, spotlight_height):
        """Create overlay pieces around the spotlight area"""
        # Clear existing overlays
        for piece in self.overlay_pieces:
            piece.destroy()
        self.overlay_pieces = []
        
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        # Create 4 overlay pieces: top, bottom, left, right
        pieces_config = [
            # Top piece (full width, from top to spotlight top)
            (0, 0, root_width, spotlight_y),
            # Bottom piece (full width, from spotlight bottom to window bottom)
            (0, spotlight_y + spotlight_height, root_width, root_height - (spotlight_y + spotlight_height)),
            # Left piece (from left to spotlight left, spotlight height)
            (0, spotlight_y, spotlight_x, spotlight_height),
            # Right piece (from spotlight right to window right, spotlight height)
            (spotlight_x + spotlight_width, spotlight_y, root_width - (spotlight_x + spotlight_width), spotlight_height)
        ]
        
        for x, y, width, height in pieces_config:
            if width > 0 and height > 0:  # Only create if has positive dimensions
                piece = tk.Toplevel(self.root)
                piece.overrideredirect(True)
                piece.configure(bg='black')
                piece.attributes('-alpha', 0.7)
                piece.attributes('-topmost', True)
                piece.geometry(f"{width}x{height}+{root_x + x}+{root_y + y}")
                # Make overlay non-interactive
                piece.attributes('-disabled', True) if platform.system() == 'Windows' else None
                self.overlay_pieces.append(piece)
        
    def _on_main_window_configure(self, event):
        """Handle main window resize/move"""
        if self.is_running:
            self._update_spotlight()
            self._update_tooltip_position()
            
    def _create_spotlight(self, x, y, width, height):
        """Create a spotlight window to highlight a specific area"""
        if self.spotlight:
            self.spotlight.destroy()
            
        # Create overlay pieces around the spotlight
        self._create_overlay_pieces(x, y, width, height)
            
        self.spotlight = tk.Toplevel(self.root)
        self.spotlight.overrideredirect(True)
        self.spotlight.configure(bg='white')
        self.spotlight.attributes('-alpha', 0.1)
        self.spotlight.attributes('-topmost', True)
        
        # Position the spotlight
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        self.spotlight.geometry(f"{width}x{height}+{root_x + x}+{root_y + y}")
        
        # Create a border effect
        border = tk.Frame(self.spotlight, bg='#0078D4', bd=3)
        border.place(x=0, y=0, relwidth=1, relheight=1)
        
    def _create_tooltip(self, step: TutorialStep):
        """Create the tooltip window for the current step"""
        if self.tooltip:
            self.tooltip.destroy()
            
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes('-topmost', True)
        
        # Force tooltip to be on top by lifting it
        self.tooltip.lift()
        self.tooltip.focus_force()
        
        # Main frame with padding
        main_frame = ttk.Frame(self.tooltip, style='light', padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=step.title,
            font=('Segoe UI', 16, 'bold'),
            foreground='#0078D4'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Content
        content_label = ttk.Label(
            main_frame,
            text=step.content,
            font=('Segoe UI', 10),
            wraplength=400,
            justify='left'
        )
        content_label.pack(anchor='w', pady=(0, 20))
        
        # Progress indicator
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=(0, 10))
        
        progress_label = ttk.Label(
            progress_frame,
            text=f"Step {self.current_step + 1} of {len(self.steps)}",
            font=('Segoe UI', 9),
            foreground='gray'
        )
        progress_label.pack(side='left')
        
        # Progress bar
        progress = ttk.Progressbar(
            progress_frame,
            length=200,
            mode='determinate',
            value=(self.current_step + 1) / len(self.steps) * 100
        )
        progress.pack(side='right', padx=(10, 0))
        
        # Navigation buttons
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill='x')
        
        # Skip button
        skip_btn = ttk.Button(
            nav_frame,
            text="Skip Tutorial",
            command=self.end_tutorial,
            style='secondary.TButton'
        )
        skip_btn.pack(side='left')
        
        # Previous button
        if self.current_step > 0:
            prev_btn = ttk.Button(
                nav_frame,
                text="← Previous",
                command=self.previous_step,
                style='info.TButton'
            )
            prev_btn.pack(side='left', padx=(10, 0))
        
        # Next/Finish button
        if self.current_step < len(self.steps) - 1:
            next_btn = ttk.Button(
                nav_frame,
                text="Next →",
                command=self.next_step,
                style='primary.TButton'
            )
            next_btn.pack(side='right')
        else:
            finish_btn = ttk.Button(
                nav_frame,
                text="Finish ✓",
                command=self.end_tutorial,
                style='success.TButton'
            )
            finish_btn.pack(side='right')
        
        # Don't show again checkbox (only on last step)
        if self.current_step == len(self.steps) - 1:
            self.dont_show_var = tk.BooleanVar(value=True)
            dont_show = ttk.Checkbutton(
                main_frame,
                text="Don't show this tutorial on startup",
                variable=self.dont_show_var
            )
            dont_show.pack(pady=(10, 0))
        
    def _show_current_step(self):
        """Display the current tutorial step"""
        if not self.is_running or self.current_step >= len(self.steps):
            return
            
        step = self.steps[self.current_step]
        
        # Perform any step action
        if step.action:
            step.action()
            
        # Create tooltip
        self._create_tooltip(step)
        
        # Create spotlight if target widget specified
        if step.target_widget:
            self.root.after(100, lambda: self._highlight_widget(step))
        else:
            # For steps without targets (like welcome), create a center overlay
            self._create_center_overlay()
            # Center the tooltip
            self._position_tooltip_center()
            
        # Ensure tooltip stays on top
        if self.tooltip:
            self.root.after(200, lambda: self.tooltip.lift() if self.tooltip else None)
            
    def _highlight_widget(self, step: TutorialStep):
        """Highlight a specific widget with spotlight"""
        try:
            # Find the target widget
            widget = self._find_widget(step.target_widget)
            if not widget:
                logging.warning(f"Tutorial: Widget not found: {step.target_widget}")
                self._position_tooltip_center()
                return
                
            # Get widget position relative to root window
            x = widget.winfo_x()
            y = widget.winfo_y()
            
            # Walk up the widget hierarchy to get absolute position
            parent = widget.winfo_parent()
            while parent and parent != '.':
                parent_widget = self.root.nametowidget(parent)
                x += parent_widget.winfo_x()
                y += parent_widget.winfo_y()
                parent = parent_widget.winfo_parent()
                
            width = widget.winfo_width()
            height = widget.winfo_height()
            
            # Apply offset padding
            left, top, right, bottom = step.highlight_offset
            x -= left
            y -= top
            width += left + right
            height += top + bottom
            
            # Create spotlight
            self._create_spotlight(x, y, width, height)
            
            # Position tooltip
            self._position_tooltip(x, y, width, height, step.position)
            
        except Exception as e:
            logging.error(f"Tutorial: Error highlighting widget: {e}")
            self._position_tooltip_center()
            
    def _find_widget(self, widget_name: str) -> Optional[tk.Widget]:
        """Find a widget by its attribute name in the app"""
        # Map of tutorial widget names to actual app attributes
        widget_map = {
            "input_tab": lambda: self.app.notebook.winfo_children()[0],
            "filters_tab": lambda: self.app.notebook.winfo_children()[1],
            "style_tab": lambda: self.app.notebook.winfo_children()[2],
            "file_list_frame": lambda: getattr(self.app, 'file_list_frame', None),
            "length_controls": lambda: getattr(self.app, 'length_frame', None),
            "color_scheme_frame": lambda: getattr(self.app, 'color_scheme_frame', None),
            "mask_frame": lambda: getattr(self.app, 'mask_frame', None),
            "canvas_frame": lambda: getattr(self.app, 'canvas_size_frame', None),
            "generate_button": lambda: getattr(self.app, 'generate_btn', None),
            "preview_canvas": lambda: getattr(self.app, 'preview_frame', None),
            "save_button": lambda: getattr(self.app, 'save_btn', None),
            "theme_selector": lambda: getattr(self.app, 'theme_var', None)
        }
        
        if widget_name in widget_map:
            widget = widget_map[widget_name]()
            return widget
            
        # Try direct attribute access
        return getattr(self.app, widget_name, None)
        
    def _position_tooltip(self, target_x, target_y, target_width, target_height, position):
        """Position the tooltip relative to the target widget"""
        if not self.tooltip:
            return
            
        # Update tooltip to get its size
        self.tooltip.update()
        tooltip_width = self.tooltip.winfo_width()
        tooltip_height = self.tooltip.winfo_height()
        
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        
        # Calculate position based on preference
        if position == "right":
            x = root_x + target_x + target_width + 20
            y = root_y + target_y + (target_height - tooltip_height) // 2
        elif position == "left":
            x = root_x + target_x - tooltip_width - 20
            y = root_y + target_y + (target_height - tooltip_height) // 2
        elif position == "top":
            x = root_x + target_x + (target_width - tooltip_width) // 2
            y = root_y + target_y - tooltip_height - 20
        elif position == "bottom":
            x = root_x + target_x + (target_width - tooltip_width) // 2
            y = root_y + target_y + target_height + 20
        else:  # center
            self._position_tooltip_center()
            return
            
        # Ensure tooltip stays on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = max(10, min(x, screen_width - tooltip_width - 10))
        y = max(10, min(y, screen_height - tooltip_height - 10))
        
        self.tooltip.geometry(f"+{x}+{y}")
        self.tooltip.lift()  # Ensure tooltip stays on top
        
    def _position_tooltip_center(self):
        """Position the tooltip in the center of the main window"""
        if not self.tooltip:
            return
            
        self.tooltip.update()
        tooltip_width = self.tooltip.winfo_width()
        tooltip_height = self.tooltip.winfo_height()
        
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        x = root_x + (root_width - tooltip_width) // 2
        y = root_y + (root_height - tooltip_height) // 2
        
        self.tooltip.geometry(f"+{x}+{y}")
        self.tooltip.lift()  # Ensure tooltip stays on top
        
    def _update_spotlight(self):
        """Update spotlight position if it exists"""
        if self.spotlight and self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            if step.target_widget:
                self._highlight_widget(step)
            else:
                # Update center overlay position
                self._create_center_overlay()
                
    def _update_tooltip_position(self):
        """Update tooltip position if it exists"""
        if self.tooltip and self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            if step.target_widget and self.spotlight:
                # Get spotlight position
                x = self.spotlight.winfo_x() - self.root.winfo_x()
                y = self.spotlight.winfo_y() - self.root.winfo_y()
                width = self.spotlight.winfo_width()
                height = self.spotlight.winfo_height()
                self._position_tooltip(x, y, width, height, step.position)
            else:
                self._position_tooltip_center()
                
    def next_step(self):
        """Go to the next tutorial step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._show_current_step()
            
    def previous_step(self):
        """Go to the previous tutorial step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_current_step()
            
    def end_tutorial(self):
        """End the tutorial and clean up"""
        self.is_running = False
        
        # Save completion state if checkbox was checked
        if hasattr(self, 'dont_show_var') and self.dont_show_var.get():
            self._save_completion_state()
            
        # Clean up overlay pieces
        for piece in self.overlay_pieces:
            piece.destroy()
        self.overlay_pieces = []
            
        if self.spotlight:
            self.spotlight.destroy()
            self.spotlight = None
            
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            
        # Unbind events
        self.root.unbind('<Configure>')
        
        # Show completion message
        if hasattr(self.app, 'show_message'):
            self.app.show_message(
                "Tutorial complete! Press F1 anytime for help.",
                "success"
            )
            
    def _save_completion_state(self):
        """Save tutorial completion to config"""
        config_path = os.path.join("configs", "wordcloud_config.json")
        config = {}
        
        # Load existing config
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except:
                pass
                
        # Update tutorial completion
        config['tutorial_completed'] = True
        
        # Save config
        os.makedirs("configs", exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)