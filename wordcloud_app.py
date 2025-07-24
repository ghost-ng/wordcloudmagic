import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
import tkinter.font as tkFont
import os
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import platform
import subprocess
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# File handling imports
import PyPDF2
from docx import Document
from pptx import Presentation
import re
from io import BytesIO

class FontListbox(ttk.Frame):
    """Custom font selector that displays fonts in their actual style"""
    def __init__(self, master, font_dict, textvariable=None, width=35, height=6, **kwargs):
        super().__init__(master, **kwargs)
        self.font_dict = font_dict
        self.textvariable = textvariable
        self.fonts_loaded = {}
        self.selected_index = -1
        self.items = []
        
        # Create frame for the selector
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        
        # Create Canvas
        self.canvas = tk.Canvas(self, 
                               width=width * 8,  # Approximate width in pixels
                               height=height * 22,  # Approximate height in pixels
                               bg='white',
                               highlightthickness=1)
        self.canvas.grid(row=0, column=0, sticky=(N, S, E, W))
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        # Bind events
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Populate fonts
        self._populate_fonts()
        
    def _populate_fonts(self):
        """Populate the canvas with fonts in their actual styles"""
        # Clear existing items
        self.canvas.delete("all")
        self.items = []
        self.fonts_loaded = {}
        
        y_position = 5
        item_height = 25
        
        for i, font_name in enumerate(sorted(self.font_dict.keys())):
            # Try to create font
            try:
                font_face = self.font_dict[font_name]
                item_font = tkFont.Font(family=font_face, size=12)
                self.fonts_loaded[font_name] = item_font
            except:
                # If font fails to load, use default
                item_font = tkFont.Font(family='Segoe UI', size=12)
            
            # Create text item
            text_id = self.canvas.create_text(10, y_position + item_height//2,
                                             text=font_name,
                                             font=item_font,
                                             anchor='w',
                                             fill='black',
                                             tags=f"font_{i}")
            
            # Create selection rectangle (initially hidden)
            rect_id = self.canvas.create_rectangle(2, y_position, 
                                                  self.canvas.winfo_width() - 2, 
                                                  y_position + item_height,
                                                  fill='#0078d4',
                                                  outline='',
                                                  state='hidden',
                                                  tags=f"select_{i}")
            
            self.items.append({
                'name': font_name,
                'text_id': text_id,
                'rect_id': rect_id,
                'y_start': y_position,
                'y_end': y_position + item_height
            })
            
            y_position += item_height
        
        # Update scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        # Set initial selection
        if self.textvariable:
            current_value = self.textvariable.get()
            if current_value in self.font_dict:
                index = sorted(self.font_dict.keys()).index(current_value)
                self._select_item(index)
    
    def _on_click(self, event):
        """Handle click events"""
        # Convert canvas coordinates
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find clicked item
        for i, item in enumerate(self.items):
            if item['y_start'] <= canvas_y <= item['y_end']:
                self._select_item(i)
                break
    
    def _select_item(self, index):
        """Select an item by index"""
        # Deselect previous
        if 0 <= self.selected_index < len(self.items):
            prev_item = self.items[self.selected_index]
            self.canvas.itemconfig(prev_item['rect_id'], state='hidden')
            self.canvas.itemconfig(prev_item['text_id'], fill='black')
        
        # Select new item
        if 0 <= index < len(self.items):
            self.selected_index = index
            item = self.items[index]
            self.canvas.itemconfig(item['rect_id'], state='normal')
            self.canvas.itemconfig(item['text_id'], fill='white')
            
            # Update variable
            if self.textvariable:
                self.textvariable.set(item['name'])
                self.event_generate('<<FontSelected>>', when='tail')
            
            # Ensure item is visible
            bbox = self.canvas.bbox(item['text_id'])
            if bbox:
                self.canvas.yview_moveto(bbox[1] / self.canvas.winfo_height())
    
    def _on_canvas_configure(self, event):
        """Update rectangles when canvas is resized"""
        canvas_width = event.width
        for item in self.items:
            self.canvas.coords(item['rect_id'], 
                             2, item['y_start'], 
                             canvas_width - 2, item['y_end'])
    
    def set_fonts(self, font_dict):
        """Update the available fonts"""
        self.font_dict = font_dict
        self._populate_fonts()

class ModernWordCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WordCloud Magic - Modern Word Cloud Generator")
        self.root.geometry("1300x850")
        self.root.state('zoomed')  # Start maximized
        
        # Available themes
        self.themes = [
            "cosmo", "flatly", "litera", "minty", "lumen", 
            "sandstone", "yeti", "pulse", "united", "morph",
            "journal", "darkly", "superhero", "solar", "cyborg",
            "vapor", "simplex", "cerculean"
        ]
        self.current_theme = tk.StringVar(value="cosmo")
        
        # Variables
        self.working_folder = tk.StringVar(value="No folder selected")
        self.text_content = ""
        self.mask_image = None
        self.mask_path = tk.StringVar(value="No mask selected")
        self.min_word_length = tk.IntVar(value=3)
        self.max_word_length = tk.IntVar(value=20)
        self.forbidden_words = set(STOPWORDS)
        self.selected_colormap = "viridis"
        self.toast = ToastNotification(
            title="WordCloud Magic",
            message="",
            duration=3000,
            bootstyle=SUCCESS
        )
        
        # Text mask variables
        self.mask_type = tk.StringVar(value="none")  # "none", "image" or "text"
        self.text_mask_input = tk.StringVar(value="")
        self.text_mask_font_size = tk.IntVar(value=200)
        self.text_mask_bold = tk.BooleanVar(value=True)
        self.text_mask_italic = tk.BooleanVar(value=False)
        self.text_mask_words_per_line = tk.IntVar(value=1)  # Words per line for multi-line text
        self.text_mask_font = tk.StringVar(value="Arial Black")  # Selected font
        
        # Available fonts for text mask
        self.available_fonts = {
            "Arial Black": "Arial Black",
            "Impact": "Impact",
            "Arial": "Arial", 
            "Helvetica": "Helvetica",
            "Times New Roman": "Times New Roman",
            "Georgia": "Georgia",
            "Verdana": "Verdana",
            "Comic Sans MS": "Comic Sans MS",
            "Trebuchet MS": "Trebuchet MS",
            "Courier New": "Courier New",
            "Calibri": "Calibri",
            "Cambria": "Cambria",
            "Tahoma": "Tahoma",
            "Century Gothic": "Century Gothic",
            "Palatino": "Palatino Linotype"
        }
        
        # Canvas settings
        self.canvas_width = tk.IntVar(value=800)
        self.canvas_height = tk.IntVar(value=600)
        self.bg_color = tk.StringVar(value="#FFFFFF")
        self.lock_aspect_ratio = tk.BooleanVar(value=False)
        self.aspect_ratio = 800 / 600  # Initial aspect ratio
        
        # Bind canvas size changes to preview update
        self.canvas_width.trace('w', self.update_preview_size)
        self.canvas_height.trace('w', self.update_preview_size)
        
        # Contour settings
        self.contour_width = tk.IntVar(value=2)
        self.contour_color = tk.StringVar(value="#000000")
        self.contour_widgets = []  # Keep track of contour widgets
        
        # Word orientation and mode
        self.prefer_horizontal = tk.DoubleVar(value=0.9)
        self.rgba_mode = tk.BooleanVar(value=False)
        self.max_words = tk.IntVar(value=200)
        self.scale = tk.IntVar(value=1)
        
        # Color schemes with descriptions
        self.color_schemes = {
            "Viridis": "viridis",
            "Plasma": "plasma",
            "Inferno": "inferno",
            "Magma": "magma",
            "Cool": "cool",
            "Hot": "hot",
            "Spring": "spring",
            "Summer": "summer",
            "Autumn": "autumn",
            "Winter": "winter",
            "Ocean": "ocean",
            "Rainbow": "rainbow",
            "Sunset": "RdYlBu",
            "Pastel": "Pastel1",
            "Dark": "Dark2",
            "Paired": "Paired"
        }
        
        self.create_ui()
        
        # Validate available fonts after UI creation (in a thread to avoid blocking)
        threading.Thread(target=self.validate_fonts, daemon=True).start()
        
    def create_ui(self):
        """Create the main UI"""
        # Create message bar at the very top
        self.create_message_bar()
        
        # Top bar for theme selection
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=X, padx=10, pady=(5, 0))
        
        # Theme selector
        theme_frame = ttk.Frame(top_bar)
        theme_frame.pack(side=RIGHT)
        
        ttk.Label(theme_frame, text="Theme:", font=('Segoe UI', 10)).pack(side=LEFT, padx=(0, 5))
        
        theme_dropdown = ttk.Combobox(theme_frame, 
                                     textvariable=self.current_theme,
                                     values=self.themes,
                                     state="readonly",
                                     width=15)
        theme_dropdown.pack(side=LEFT)
        theme_dropdown.bind('<<ComboboxSelected>>', self.change_theme)
        
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=BOTH, expand=TRUE)
        
        # Create paned window for resizable layout
        paned = ttk.PanedWindow(main_container, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=TRUE)
        
        # Left panel (controls)
        left_panel = ttk.Frame(paned, padding="10")
        paned.add(left_panel, weight=1)
        
        # Right panel (preview) - add padding to create space from left panel
        right_panel = ttk.Frame(paned, padding=(20, 10, 10, 10))  # More padding on left side
        paned.add(right_panel, weight=2)
        
        # Create notebook for organized controls
        self.notebook = ttk.Notebook(left_panel, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=TRUE)
        
        # Set initial sash position (after adding both panels)
        self.root.after(100, lambda: paned.sashpos(0, 520))  # Set left panel to 520px width
        
        # Create tabs
        self.create_input_tab()
        self.create_filter_tab()
        self.create_style_tab()
        
        # Create preview area
        self.create_preview_area(right_panel)
        
    def create_input_tab(self):
        """Create input sources tab"""
        input_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(input_frame, text="📁 Input")
        
        # Working folder selection
        folder_frame = self.create_section(input_frame, "Working Folder")
        
        folder_info = ttk.Frame(folder_frame)
        folder_info.pack(fill=X, pady=(0, 10))
        
        ttk.Label(folder_info, 
                 textvariable=self.working_folder,
                 bootstyle="secondary",
                 font=('Segoe UI', 10)).pack(side=LEFT, padx=(5, 0))
        
        ttk.Button(folder_frame, 
                  text="Select Folder",
                  command=self.select_folder,
                  bootstyle="primary",
                  width=20).pack()
        
        # File selection
        file_frame = self.create_section(input_frame, "Select Files")
        
        # Create frame for listbox with border
        listbox_frame = ttk.Frame(file_frame, bootstyle="secondary", padding=1)
        listbox_frame.pack(fill=BOTH, expand=TRUE, pady=(0, 10))
        
        self.file_listbox = tk.Listbox(listbox_frame,
                                      selectmode=tk.MULTIPLE,
                                      height=6,
                                      font=('Segoe UI', 10),
                                      borderwidth=0,
                                      highlightthickness=1,
                                      highlightbackground="#e0e0e0",
                                      highlightcolor="#0078d4")
        self.file_listbox.pack(fill=BOTH, expand=TRUE, padx=1, pady=1)
        
        # Button frame for file operations
        file_btn_frame = ttk.Frame(file_frame)
        file_btn_frame.pack(fill=X, pady=(5, 0))
        
        ttk.Button(file_btn_frame,
                  text="Select All",
                  command=self.select_all_files,
                  bootstyle="info-outline",
                  width=10).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(file_btn_frame,
                  text="Clear",
                  command=self.clear_file_selection,
                  bootstyle="secondary-outline",
                  width=12).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(file_btn_frame,
                  text="Load Selected Files",
                  command=self.load_files,
                  bootstyle="success",
                  width=18).pack(side=LEFT)
        
        # Text input
        text_frame = self.create_section(input_frame, "Or Paste Text")
        
        # Create frame for text widget with border
        text_border = ttk.Frame(text_frame, bootstyle="secondary", padding=1)
        text_border.pack(fill=BOTH, expand=TRUE, pady=(0, 10))
        
        self.text_input = ScrolledText(text_border,
                                      height=8,
                                      font=('Segoe UI', 10),
                                      borderwidth=0,
                                      highlightthickness=0,
                                      wrap=tk.WORD)
        self.text_input.pack(fill=BOTH, expand=TRUE, padx=1, pady=1)
        
        ttk.Button(text_frame,
                  text="Use Pasted Text",
                  command=self.use_pasted_text,
                  bootstyle="info",
                  width=20).pack()
        
    def create_filter_tab(self):
        """Create filters tab"""
        filter_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(filter_frame, text="⚙️ Filters")
        
        # Word length filters
        length_frame = self.create_section(filter_frame, "Word Length")
        
        # Min length with meter
        min_container = ttk.Frame(length_frame)
        min_container.pack(fill=X, pady=(0, 20))
        
        min_label_frame = ttk.Frame(min_container)
        min_label_frame.pack(fill=X)
        ttk.Label(min_label_frame, text="Minimum Length:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.min_length_label = ttk.Label(min_label_frame, text="3 characters", 
                                         bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.min_length_label.pack(side=RIGHT)
        
        self.min_length_scale = ttk.Scale(min_container,
                                         from_=1,
                                         to=10,
                                         value=3,
                                         command=self.update_min_label,
                                         bootstyle="primary")
        self.min_length_scale.pack(fill=X, pady=(5, 0))
        
        # Max length with meter
        max_container = ttk.Frame(length_frame)
        max_container.pack(fill=X)
        
        max_label_frame = ttk.Frame(max_container)
        max_label_frame.pack(fill=X)
        ttk.Label(max_label_frame, text="Maximum Length:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.max_length_label = ttk.Label(max_label_frame, text="20 characters",
                                         bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.max_length_label.pack(side=RIGHT)
        
        self.max_length_scale = ttk.Scale(max_container,
                                         from_=10,
                                         to=50,
                                         value=20,
                                         command=self.update_max_label,
                                         bootstyle="primary")
        self.max_length_scale.pack(fill=X, pady=(5, 0))
        
        # Forbidden words
        forbidden_frame = self.create_section(filter_frame, "Forbidden Words")
        
        ttk.Label(forbidden_frame,
                 text="Enter words to exclude (one per line):",
                 font=('Segoe UI', 10)).pack(anchor=W, pady=(0, 5))
        
        # Create frame for text widget with border
        text_border = ttk.Frame(forbidden_frame, bootstyle="secondary", padding=1)
        text_border.pack(fill=BOTH, expand=TRUE, pady=(0, 10))
        
        self.forbidden_text = ScrolledText(text_border,
                                          height=10,
                                          font=('Segoe UI', 10),
                                          borderwidth=0,
                                          highlightthickness=0,
                                          wrap=tk.WORD)
        self.forbidden_text.pack(fill=BOTH, expand=TRUE, padx=1, pady=1)
        
        # Pre-populate with common stop words
        default_forbidden = "the\nand\nor\nbut\nin\non\nat\nto\nfor\nof\nwith\nby\nfrom\nas\nis\nwas\nare\nbeen"
        self.forbidden_text.insert('1.0', default_forbidden)
        
        ttk.Button(forbidden_frame,
                  text="Update Forbidden Words",
                  command=self.update_forbidden_words,
                  bootstyle="warning",
                  width=25).pack()
        
    def create_style_tab(self):
        """Create style options tab"""
        style_tab = ttk.Frame(self.notebook)
        self.notebook.add(style_tab, text="🎨 Style")
        
        # Create scrollable frame
        canvas = tk.Canvas(style_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(style_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Add padding to scrollable frame
        style_frame = ttk.Frame(scrollable_frame, padding="20")
        style_frame.pack(fill="both", expand=True)
        
        # Bind mouse wheel to this specific canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind/unbind mousewheel when entering/leaving the canvas
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        
        # Color scheme selection
        color_frame = self.create_section(style_frame, "Color Scheme")
        
        # Create scrollable frame for color buttons
        color_scroll = ttk.Frame(color_frame)
        color_scroll.pack(fill=BOTH, expand=TRUE)
        
        # Create color scheme buttons in a grid
        self.color_var = tk.StringVar(value="Viridis")
        
        colors_grid = ttk.Frame(color_scroll)
        colors_grid.pack(fill=X)
        
        row = 0
        col = 0
        for name, cmap in self.color_schemes.items():
            btn = ttk.Radiobutton(colors_grid,
                                 text=name,
                                 variable=self.color_var,
                                 value=name,
                                 command=self.on_color_select,
                                 bootstyle="primary-outline-toolbutton",
                                 width=12)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=W)
            col += 1
            if col > 3:  # Changed from 1 to 3 for 4 columns
                col = 0
                row += 1
        
        # Color preview
        preview_label = ttk.Label(color_frame, text="Preview:", font=('Segoe UI', 10, 'bold'))
        preview_label.pack(anchor=W, pady=(15, 5))
        
        self.color_preview_frame = ttk.Frame(color_frame, height=40, bootstyle="secondary")
        self.color_preview_frame.pack(fill=X)
        self.color_preview_frame.pack_propagate(False)
        self.update_color_preview()
        
        # Mask and Shape Options
        mask_frame = self.create_section(style_frame, "Shape & Appearance")
        
        # Create notebook for mask options
        self.mask_notebook = ttk.Notebook(mask_frame, bootstyle="secondary")
        self.mask_notebook.pack(fill=BOTH, expand=TRUE)
        
        # Create tabs
        self.create_no_mask_tab()
        self.create_image_mask_tab()
        self.create_text_mask_tab()
        
        # Bind tab change event
        self.mask_notebook.bind("<<NotebookTabChanged>>", self.on_mask_tab_changed)
        
        # Word Orientation
        orientation_frame = ttk.LabelFrame(mask_frame, text="Word Orientation", padding=10)
        orientation_frame.pack(fill=X, pady=(0, 10))
        
        # Prefer horizontal slider
        horizontal_container = ttk.Frame(orientation_frame)
        horizontal_container.pack(fill=X)
        
        horizontal_label_frame = ttk.Frame(horizontal_container)
        horizontal_label_frame.pack(fill=X)
        ttk.Label(horizontal_label_frame, text="Prefer Horizontal:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.horizontal_label = ttk.Label(horizontal_label_frame, text="90%",
                                         bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.horizontal_label.pack(side=RIGHT)
        
        self.horizontal_scale = ttk.Scale(horizontal_container,
                                        from_=0.0,
                                        to=1.0,
                                        value=0.9,
                                        command=self.update_horizontal_label,
                                        bootstyle="primary")
        self.horizontal_scale.pack(fill=X, pady=(5, 0))
        
        ttk.Label(orientation_frame, 
                 text="0% = All vertical, 100% = All horizontal",
                 font=('Segoe UI', 9),
                 bootstyle="secondary").pack(pady=(5, 0))
        
        # Other Settings
        other_frame = ttk.LabelFrame(mask_frame, text="Other Settings", padding=10)
        other_frame.pack(fill=X, pady=(0, 10))
        
        # Max words slider
        max_words_container = ttk.Frame(other_frame)
        max_words_container.pack(fill=X, pady=(0, 10))
        
        max_words_label_frame = ttk.Frame(max_words_container)
        max_words_label_frame.pack(fill=X)
        ttk.Label(max_words_label_frame, text="Maximum Words:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.max_words_label = ttk.Label(max_words_label_frame, text="200",
                                        bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.max_words_label.pack(side=RIGHT)
        
        self.max_words_scale = ttk.Scale(max_words_container,
                                        from_=10,
                                        to=500,
                                        value=200,
                                        command=self.update_max_words,
                                        bootstyle="primary")
        self.max_words_scale.pack(fill=X, pady=(5, 0))
        
        ttk.Label(max_words_container, 
                 text="More words = denser cloud, fewer words = cleaner look",
                 font=('Segoe UI', 9),
                 bootstyle="secondary").pack(pady=(5, 0))
        
        # Scale slider
        scale_container = ttk.Frame(other_frame)
        scale_container.pack(fill=X)
        
        scale_label_frame = ttk.Frame(scale_container)
        scale_label_frame.pack(fill=X)
        ttk.Label(scale_label_frame, text="Quality Scale:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.scale_label = ttk.Label(scale_label_frame, text="1",
                                    bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.scale_label.pack(side=RIGHT)
        
        self.scale_scale = ttk.Scale(scale_container,
                                    from_=1,
                                    to=10,
                                    value=1,
                                    command=self.update_scale,
                                    bootstyle="primary")
        self.scale_scale.pack(fill=X, pady=(5, 0))
        
        ttk.Label(scale_container, 
                 text="Higher values = better quality but slower generation",
                 font=('Segoe UI', 9),
                 bootstyle="secondary").pack(pady=(5, 0))
        
        # Canvas options
        canvas_frame = ttk.LabelFrame(mask_frame, text="Canvas Settings", padding=10)
        canvas_frame.pack(fill=X, pady=(0, 10))
        
        # Lock aspect ratio checkbox
        ratio_frame = ttk.Frame(canvas_frame)
        ratio_frame.pack(fill=X, pady=(0, 10))
        
        self.lock_ratio_check = ttk.Checkbutton(ratio_frame,
                                               text="Lock aspect ratio",
                                               variable=self.lock_aspect_ratio,
                                               command=self.on_lock_ratio_change,
                                               bootstyle="primary")
        self.lock_ratio_check.pack(side=LEFT)
        
        self.ratio_label = ttk.Label(ratio_frame, text="",
                                    font=('Segoe UI', 9, 'italic'),
                                    bootstyle="secondary")
        self.ratio_label.pack(side=LEFT, padx=(10, 0))
        
        # Width slider
        width_container = ttk.Frame(canvas_frame)
        width_container.pack(fill=X, pady=(0, 15))
        
        width_label_frame = ttk.Frame(width_container)
        width_label_frame.pack(fill=X)
        ttk.Label(width_label_frame, text="Width:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.width_label = ttk.Label(width_label_frame, text="800 px",
                                    bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.width_label.pack(side=RIGHT)
        
        self.width_scale = ttk.Scale(width_container,
                                    from_=400,
                                    to=4000,
                                    value=800,
                                    command=self.update_width,
                                    bootstyle="primary")
        self.width_scale.pack(fill=X, pady=(5, 0))
        
        # Height slider
        height_container = ttk.Frame(canvas_frame)
        height_container.pack(fill=X, pady=(0, 10))
        
        height_label_frame = ttk.Frame(height_container)
        height_label_frame.pack(fill=X)
        ttk.Label(height_label_frame, text="Height:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.height_label = ttk.Label(height_label_frame, text="600 px",
                                     bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.height_label.pack(side=RIGHT)
        
        self.height_scale = ttk.Scale(height_container,
                                     from_=300,
                                     to=4000,
                                     value=600,
                                     command=self.update_height,
                                     bootstyle="primary")
        self.height_scale.pack(fill=X, pady=(5, 0))
        
        # Size presets
        preset_frame = ttk.Frame(canvas_frame)
        preset_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Label(preset_frame, text="", font=('Segoe UI', 10)).pack(side=LEFT, padx=(0, 10))
        
        presets = [
            ("Square", 800, 800),
            ("HD", 1920, 1080),
            ("4:3", 800, 600),
            ("16:9", 1280, 720),
            ("A4", 800, 1131)
        ]
        
        for name, width, height in presets:
            ttk.Button(preset_frame,
                      text=name,
                      command=lambda w=width, h=height: self.set_canvas_size(w, h),
                      bootstyle="secondary-outline",
                      width=8).pack(side=LEFT, padx=2)
        
        # Mode selection (RGB/RGBA)
        mode_container = ttk.Frame(canvas_frame)
        mode_container.pack(fill=X, pady=(0, 10))
        
        ttk.Label(mode_container, text="Mode:", font=('Segoe UI', 10)).pack(side=LEFT)
        
        mode_frame = ttk.Frame(mode_container)
        mode_frame.pack(side=LEFT, padx=(20, 0))
        
        ttk.Radiobutton(mode_frame,
                       text="RGB (Solid)",
                       variable=self.rgba_mode,
                       value=False,
                       command=self.update_mode,
                       bootstyle="primary").pack(side=LEFT, padx=(0, 15))
        
        ttk.Radiobutton(mode_frame,
                       text="RGBA (Transparent)",
                       variable=self.rgba_mode,
                       value=True,
                       command=self.update_mode,
                       bootstyle="primary").pack(side=LEFT)
        
        # Background color
        self.bg_container = ttk.Frame(canvas_frame)
        self.bg_container.pack(fill=X)
        
        self.bg_label = ttk.Label(self.bg_container, text="Background Color:", font=('Segoe UI', 10))
        self.bg_label.pack(side=LEFT)
        
        self.bg_color_preview = ttk.Frame(self.bg_container, width=30, height=30)
        self.bg_color_preview.pack(side=RIGHT, padx=(10, 0))
        self.bg_color_preview.configure(bootstyle="light")
        
        self.bg_color_btn = ttk.Button(self.bg_container,
                                      text="Choose Color",
                                      command=self.choose_bg_color,
                                      bootstyle="primary-outline",
                                      width=15)
        self.bg_color_btn.pack(side=RIGHT)
        
    def create_no_mask_tab(self):
        """Create the no mask tab"""
        no_mask_frame = ttk.Frame(self.mask_notebook)
        self.mask_notebook.add(no_mask_frame, text="No Mask")
        
        # Info frame with border
        info_frame = ttk.LabelFrame(no_mask_frame, text="Information", padding=15)
        info_frame.pack(fill=X, padx=20, pady=20)
        
        # Info label
        info_label = ttk.Label(info_frame, 
                              text="Word cloud will be generated in a rectangular shape.\nNo special shape or contours will be applied.",
                              font=('Segoe UI', 10),
                              bootstyle="secondary")
        info_label.pack()
        
        # Add a note about using other tabs
        ttk.Label(info_frame,
                 text="\nTo use a custom shape, select the Image Mask or Text Mask tab.",
                 font=('Segoe UI', 9, 'italic'),
                 bootstyle="info").pack()
    
    def create_image_mask_tab(self):
        """Create the image mask tab"""
        image_mask_frame = ttk.Frame(self.mask_notebook, padding=20)
        self.mask_notebook.add(image_mask_frame, text="Image Mask")
        
        # Create the image mask frame content
        self.create_image_mask_frame(image_mask_frame)
        
        # Add contour options to this tab
        self.create_contour_options(image_mask_frame)
        
        # Add mask preview to this tab
        self.create_mask_preview(image_mask_frame)
    
    def create_text_mask_tab(self):
        """Create the text mask tab"""
        text_mask_frame = ttk.Frame(self.mask_notebook, padding=20)
        self.mask_notebook.add(text_mask_frame, text="Text Mask")
        
        # Create the text mask frame content
        self.create_text_mask_frame(text_mask_frame)
        
        # Add contour options to this tab
        self.create_contour_options(text_mask_frame)
        
        # Add mask preview to this tab
        self.create_mask_preview(text_mask_frame)
    
    def create_contour_options(self, parent):
        """Create contour options frame"""
        contour_frame = ttk.LabelFrame(parent, text="Contour Options", padding=10)
        contour_frame.pack(fill=X, pady=(10, 10))
        
        # Contour width
        width_container = ttk.Frame(contour_frame)
        width_container.pack(fill=X, pady=(0, 10))
        
        width_label_frame = ttk.Frame(width_container)
        width_label_frame.pack(fill=X)
        contour_width_lbl = ttk.Label(width_label_frame, text="Contour Width:", font=('Segoe UI', 10))
        contour_width_lbl.pack(side=LEFT)
        contour_width_label = ttk.Label(width_label_frame, text="2 pixels",
                                       bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        contour_width_label.pack(side=RIGHT)
        
        contour_width_scale = ttk.Scale(width_container,
                                       from_=0,
                                       to=10,
                                       value=2,
                                       command=lambda v: self.update_contour_width(v, contour_width_label),
                                       bootstyle="primary")
        contour_width_scale.pack(fill=X, pady=(5, 0))
        
        # Contour color
        color_container = ttk.Frame(contour_frame)
        color_container.pack(fill=X)
        
        contour_color_lbl = ttk.Label(color_container, text="Contour Color:", font=('Segoe UI', 10))
        contour_color_lbl.pack(side=LEFT)
        
        contour_color_preview = ttk.Frame(color_container, width=30, height=30, bootstyle="dark")
        contour_color_preview.pack(side=RIGHT, padx=(10, 0))
        
        contour_color_btn = ttk.Button(color_container,
                                      text="Choose Color",
                                      command=lambda: self.choose_contour_color(contour_color_preview),
                                      bootstyle="primary-outline",
                                      width=15)
        contour_color_btn.pack(side=RIGHT)
        
        # Store references if this is the first creation
        if not hasattr(self, 'contour_width_label'):
            self.contour_width_label = contour_width_label
            self.contour_width_scale = contour_width_scale
            self.contour_color_preview = contour_color_preview
    
    def create_mask_preview(self, parent):
        """Create mask preview frame"""
        preview_container = ttk.LabelFrame(parent, text="Mask Preview", padding=10)
        preview_container.pack(fill=BOTH, expand=TRUE, pady=(10, 0))
        
        # Create a label for this specific tab
        preview_label = ttk.Label(preview_container,
                                 text="No mask selected",
                                 anchor=CENTER,
                                 font=('Segoe UI', 10))
        preview_label.pack(fill=BOTH, expand=TRUE)
        
        # Store reference based on parent tab
        if "image" in str(parent):
            self.image_mask_preview_label = preview_label
        else:
            self.text_mask_preview_label = preview_label
    
    def create_image_mask_frame(self, parent):
        """Create the image mask options frame"""
        mask_file_frame = ttk.LabelFrame(parent, text="Image File", padding=10)
        mask_file_frame.pack(fill=X)
        
        mask_info = ttk.Frame(mask_file_frame)
        mask_info.pack(fill=X, pady=(0, 10))
        
        self.image_mask_label = ttk.Label(mask_info,
                                         text="No image selected",
                                         bootstyle="secondary",
                                         font=('Segoe UI', 10))
        self.image_mask_label.pack(side=LEFT)
        
        mask_btn_frame = ttk.Frame(mask_file_frame)
        mask_btn_frame.pack(fill=X)
        
        ttk.Button(mask_btn_frame,
                  text="Select Image",
                  command=self.select_mask,
                  bootstyle="primary",
                  width=15).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(mask_btn_frame,
                  text="Clear",
                  command=self.clear_mask,
                  bootstyle="secondary",
                  width=15).pack(side=LEFT)
    
    def create_text_mask_frame(self, parent):
        """Create the text mask options frame"""
        text_input_frame = ttk.LabelFrame(parent, text="Text Input", padding=10)
        text_input_frame.pack(fill=X)
        
        # Text input
        ttk.Label(text_input_frame, text="Enter text for mask:", font=('Segoe UI', 10)).pack(anchor=W, pady=(0, 5))
        
        self.text_mask_entry = ttk.Entry(text_input_frame,
                                        textvariable=self.text_mask_input,
                                        font=('Segoe UI', 12),
                                        bootstyle="primary")
        self.text_mask_entry.pack(fill=X, pady=(0, 10))
        self.text_mask_entry.bind('<KeyRelease>', lambda e: self.update_text_mask())
        
        # Font selection
        font_frame = ttk.Frame(text_input_frame)
        font_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(font_frame, text="Font:", font=('Segoe UI', 10)).pack(anchor=W, pady=(0, 5))
        
        self.font_listbox = FontListbox(font_frame,
                                       self.available_fonts,
                                       textvariable=self.text_mask_font,
                                       width=35,
                                       height=5)
        self.font_listbox.pack(fill=X)
        self.font_listbox.bind('<<FontSelected>>', lambda e: self.update_text_mask())
        
        # Font size
        font_size_container = ttk.Frame(text_input_frame)
        font_size_container.pack(fill=X, pady=(0, 10))
        
        font_size_label_frame = ttk.Frame(font_size_container)
        font_size_label_frame.pack(fill=X)
        ttk.Label(font_size_label_frame, text="Font Size:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.font_size_label = ttk.Label(font_size_label_frame, text="200",
                                        bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.font_size_label.pack(side=RIGHT)
        
        self.font_size_scale = ttk.Scale(font_size_container,
                                        from_=50,
                                        to=2000,
                                        value=200,
                                        command=self.update_font_size,
                                        bootstyle="primary")
        self.font_size_scale.pack(fill=X, pady=(5, 0))
        
        # Font style options
        style_frame = ttk.Frame(text_input_frame)
        style_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Label(style_frame, text="Font Style:", font=('Segoe UI', 10)).pack(side=LEFT, padx=(0, 20))
        
        ttk.Checkbutton(style_frame,
                       text="Bold",
                       variable=self.text_mask_bold,
                       command=self.update_text_mask,
                       bootstyle="primary").pack(side=LEFT, padx=(0, 15))
        
        ttk.Checkbutton(style_frame,
                       text="Italic",
                       variable=self.text_mask_italic,
                       command=self.update_text_mask,
                       bootstyle="primary").pack(side=LEFT)
        
        # Words per line control
        words_frame = ttk.Frame(text_input_frame)
        words_frame.pack(fill=X, pady=(15, 0))
        
        words_label_frame = ttk.Frame(words_frame)
        words_label_frame.pack(fill=X)
        ttk.Label(words_label_frame, text="Words per line:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.words_per_line_label = ttk.Label(words_label_frame, text="1 word",
                                             bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.words_per_line_label.pack(side=RIGHT)
        
        self.words_per_line_scale = ttk.Scale(words_frame,
                                              from_=1,
                                              to=10,
                                              value=1,
                                              command=self.update_words_per_line,
                                              bootstyle="primary")
        self.words_per_line_scale.pack(fill=X, pady=(5, 0))
        
        ttk.Label(words_frame, 
                 text="Tip: Use multiple words per line to create wider text masks",
                 font=('Segoe UI', 9),
                 bootstyle="secondary").pack(pady=(5, 0))
    
    def on_mask_tab_changed(self, event):
        """Handle mask tab change"""
        selected_tab = self.mask_notebook.index(self.mask_notebook.select())
        if selected_tab == 0:  # No Mask
            self.mask_type.set("none")
            self.mask_image = None
            self.mask_path.set("No mask")
        elif selected_tab == 1:  # Image Mask
            self.mask_type.set("image")
            # Keep existing image mask if any
        elif selected_tab == 2:  # Text Mask
            self.mask_type.set("text")
            # Update text mask if text exists
            if self.text_mask_input.get():
                self.update_text_mask()
    
    
    def update_font_size(self, value):
        """Update font size label and regenerate text mask"""
        val = int(float(value))
        self.text_mask_font_size.set(val)
        self.font_size_label.config(text=str(val))
        if self.mask_type.get() == "text" and self.text_mask_input.get():
            self.update_text_mask()
    
    def update_words_per_line(self, value):
        """Update words per line label and regenerate text mask"""
        val = int(float(value))
        self.text_mask_words_per_line.set(val)
        if val == 1:
            self.words_per_line_label.config(text="1 word")
        else:
            self.words_per_line_label.config(text=f"{val} words")
        if self.mask_type.get() == "text" and self.text_mask_input.get():
            self.update_text_mask()
    
    def get_ratio_text(self, width, height):
        """Get a readable aspect ratio text"""
        # Calculate GCD to simplify ratio
        from math import gcd
        g = gcd(width, height)
        w = width // g
        h = height // g
        
        # Check for common ratios
        common_ratios = {
            (16, 9): "16:9",
            (9, 16): "9:16",
            (4, 3): "4:3",
            (3, 4): "3:4",
            (16, 10): "16:10",
            (1, 1): "1:1",
            (3, 2): "3:2",
            (2, 3): "2:3"
        }
        
        if (w, h) in common_ratios:
            return common_ratios[(w, h)]
        
        # Simplify further if numbers are too large
        while w > 20 or h > 20:
            if w % 2 == 0 and h % 2 == 0:
                w //= 2
                h //= 2
            else:
                break
        
        return f"{w}:{h}"
    
    def on_lock_ratio_change(self):
        """Handle lock aspect ratio checkbox change"""
        if self.lock_aspect_ratio.get():
            # Calculate and store current aspect ratio
            width = self.canvas_width.get()
            height = self.canvas_height.get()
            if height > 0:
                self.aspect_ratio = width / height
                # Show ratio in simplified form
                ratio_text = self.get_ratio_text(width, height)
                self.ratio_label.config(text=f"({ratio_text})")
        else:
            self.ratio_label.config(text="")
    
    def update_width(self, value):
        """Update width and maintain aspect ratio if locked"""
        if hasattr(self, '_updating'):  # Prevent recursion
            return
            
        val = int(float(value))
        self.canvas_width.set(val)
        self.width_label.config(text=f"{val} px")
        
        if self.lock_aspect_ratio.get() and self.aspect_ratio > 0:
            self._updating = True
            try:
                # Update height to maintain aspect ratio
                new_height = int(val / self.aspect_ratio)
                new_height = max(300, min(4000, new_height))  # Clamp to valid range
                self.canvas_height.set(new_height)
                self.height_label.config(text=f"{new_height} px")
                self.height_scale.set(new_height)
            finally:
                delattr(self, '_updating')
        
        # Clear canvas when dimensions change
        self.clear_canvas()
    
    def update_height(self, value):
        """Update height and maintain aspect ratio if locked"""
        if hasattr(self, '_updating'):  # Prevent recursion
            return
            
        val = int(float(value))
        self.canvas_height.set(val)
        self.height_label.config(text=f"{val} px")
        
        if self.lock_aspect_ratio.get() and self.aspect_ratio > 0:
            self._updating = True
            try:
                # Update width to maintain aspect ratio
                new_width = int(val * self.aspect_ratio)
                new_width = max(400, min(4000, new_width))  # Clamp to valid range
                self.canvas_width.set(new_width)
                self.width_label.config(text=f"{new_width} px")
                self.width_scale.set(new_width)
            finally:
                delattr(self, '_updating')
        
        # Clear canvas when dimensions change
        self.clear_canvas()
    
    def set_canvas_size(self, width, height):
        """Set canvas size from preset"""
        # Update the aspect ratio if locked
        if self.lock_aspect_ratio.get():
            self.aspect_ratio = width / height
            # Update ratio display
            ratio_text = self.get_ratio_text(width, height)
            self.ratio_label.config(text=f"({ratio_text})")
        
        # Update values and UI
        self.canvas_width.set(width)
        self.canvas_height.set(height)
        self.width_label.config(text=f"{width} px")
        self.height_label.config(text=f"{height} px")
        self.width_scale.set(width)
        self.height_scale.set(height)
        
        # Show toast with preset info
        ratio_text = self.get_ratio_text(width, height)
        self.show_toast(f"Canvas size set to {width}×{height} ({ratio_text})", "info")
        
        # Clear canvas when preset is selected
        self.clear_canvas()
        
        # Clear canvas when preset is selected
        self.clear_canvas()
        
    def calculate_preview_size(self):
        """Calculate preview display size maintaining aspect ratio with max width constraint"""
        actual_width = self.canvas_width.get()
        actual_height = self.canvas_height.get()
        
        # Calculate scale factor based on max width only
        if actual_width > self.preview_max_width:
            scale = self.preview_max_width / actual_width
        else:
            scale = 1.0  # Don't upscale
        
        display_width = int(actual_width * scale)
        display_height = int(actual_height * scale)
        
        return display_width, display_height
    
    def create_preview_area(self, parent):
        """Create the word cloud preview area"""
        preview_container = ttk.LabelFrame(parent, text="Word Cloud Preview", padding=15)
        preview_container.pack(fill=BOTH, expand=TRUE)
        
        # Create a centered frame for the preview with margins
        preview_wrapper = ttk.Frame(preview_container)
        preview_wrapper.pack(fill=BOTH, expand=TRUE, padx=10)  # Reduced horizontal margins
        
        # Scale indicator label (initially hidden)
        self.scale_indicator = ttk.Label(preview_wrapper, 
                                        text="",
                                        font=('Segoe UI', 9, 'italic'),
                                        bootstyle="secondary")
        self.scale_indicator.pack(pady=(0, 5))
        
        # Canvas for word cloud with max width constraint
        canvas_container = ttk.Frame(preview_wrapper)
        canvas_container.pack(expand=TRUE)  # Center it
        
        canvas_frame = ttk.Frame(canvas_container, bootstyle="secondary", padding=2)
        canvas_frame.pack(pady=(0, 15))
        
        # Fixed preview max width (will scale height proportionally)
        self.preview_max_width = 600
        
        # Calculate initial display size
        display_width, display_height = self.calculate_preview_size()
        
        self.figure = plt.Figure(figsize=(display_width/100, display_height/100), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()  # Don't expand, keep fixed size
        
        # Initial empty plot with message
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Generate a word cloud to see it here', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.axis('off')
        self.canvas.draw()
        
        # Store reference to preview canvas frame for theme updates
        self.preview_canvas_frame = canvas_frame
        
        # Button frame (centered below preview)
        button_frame = ttk.Frame(preview_wrapper)
        button_frame.pack()
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(button_frame, 
                                       mode='indeterminate',
                                       bootstyle="success-striped",
                                       length=300)
        
        # Generate and save buttons
        btn_container = ttk.Frame(button_frame)
        btn_container.pack()
        
        self.generate_btn = ttk.Button(btn_container,
                                      text="🚀 Generate Word Cloud",
                                      command=self.generate_wordcloud,
                                      bootstyle="success",
                                      width=25)
        self.generate_btn.pack(side=LEFT, padx=(0, 10))
        
        self.save_btn = ttk.Button(btn_container,
                                  text="💾 Save Image",
                                  command=self.save_wordcloud,
                                  bootstyle="primary",
                                  width=20,
                                  state=DISABLED)
        self.save_btn.pack(side=LEFT)
        
        # Clear button
        self.clear_btn = ttk.Button(btn_container,
                                  text="🗑️ Clear",
                                  command=self.clear_canvas,
                                  bootstyle="secondary",
                                  width=15)
        self.clear_btn.pack(side=LEFT, padx=(10, 0))
    
    def create_message_bar(self):
        """Create the message bar at the top of the interface"""
        # Message bar frame
        self.message_frame = ttk.Frame(self.root)
        self.message_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        # Message styles
        self.message_styles = {
            "good": {"icon": "✓", "bootstyle": "success", "bg": "#d4edda", "fg": "#155724", "border": "#c3e6cb"},
            "info": {"icon": "ℹ", "bootstyle": "info", "bg": "#d1ecf1", "fg": "#0c5460", "border": "#bee5eb"},
            "warning": {"icon": "⚠", "bootstyle": "warning", "bg": "#fff3cd", "fg": "#856404", "border": "#ffeaa7"},
            "fail": {"icon": "✗", "bootstyle": "danger", "bg": "#f8d7da", "fg": "#721c24", "border": "#f5c6cb"}
        }
        
        # Create message label (initially hidden)
        self.message_container = ttk.Frame(self.message_frame)
        
        self.message_icon_label = ttk.Label(self.message_container, font=('Segoe UI', 12, 'bold'))
        self.message_icon_label.pack(side=LEFT, padx=(10, 5))
        
        self.message_label = ttk.Label(self.message_container, font=('Segoe UI', 10))
        self.message_label.pack(side=LEFT, padx=(0, 10))
        
        # Close button
        self.message_close_btn = ttk.Button(self.message_container, 
                                           text="×",
                                           width=3,
                                           command=self.hide_message)
        self.message_close_btn.pack(side=RIGHT, padx=(0, 5))
        
        # Initially hide the message
        self.hide_message()
    
    def show_message(self, message, status="info"):
        """Show a message in the message bar"""
        if status not in self.message_styles:
            status = "info"
        
        style = self.message_styles[status]
        
        # Update message content
        self.message_icon_label.config(text=style["icon"])
        self.message_label.config(text=message)
        
        # Apply styling based on theme
        if self.current_theme.get() in ["darkly", "superhero", "solar", "cyborg", "vapor"]:
            # Dark theme adjustments
            self.message_container.configure(style=f"{style['bootstyle']}.TFrame")
        else:
            # Light theme - use custom colors
            self.message_container.configure(style="TFrame")
            # We'll use the bootstyle colors which work well
        
        # Show the message
        self.message_container.pack(fill=X, pady=5)
        
        # Auto-hide after 5 seconds for non-error messages
        if status != "fail":
            self.root.after(5000, self.hide_message)
    
    def hide_message(self):
        """Hide the message bar"""
        self.message_container.pack_forget()
        
    def create_section(self, parent, title):
        """Create a styled section with title"""
        frame = ttk.LabelFrame(parent, text=title, padding=15)
        frame.pack(fill=BOTH, expand=TRUE, pady=(0, 15))
        return frame
    
    def select_folder(self):
        """Select working folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.working_folder.set(folder)
            self.populate_file_list()
    
    def populate_file_list(self):
        """Populate file listbox with supported files"""
        self.file_listbox.delete(0, tk.END)
        
        folder = self.working_folder.get()
        if folder and os.path.exists(folder):
            files_found = 0
            for file in os.listdir(folder):
                if file.lower().endswith(('.txt', '.pdf', '.docx', '.pptx')):
                    self.file_listbox.insert(tk.END, f"📄 {file}")
                    files_found += 1
            
            if files_found == 0:
                self.file_listbox.insert(tk.END, "No supported files found")
                self.show_message("No supported files found in the selected folder", "info")
            else:
                self.show_message(f"Found {files_found} supported file(s) in the selected folder", "info")
    
    def select_all_files(self):
        """Select all files in the listbox"""
        # First check if there are any files
        if self.file_listbox.size() == 0:
            self.show_message("No files to select", "warning")
            return
        
        # Check if the first item is "No supported files found"
        first_item = self.file_listbox.get(0)
        if first_item == "No supported files found":
            self.show_message("No files to select", "warning")
            return
        
        # Select all items
        self.file_listbox.selection_set(0, tk.END)
        
        # Show message
        file_count = self.file_listbox.size()
        self.show_message(f"Selected all {file_count} file(s)", "info")
    
    def clear_file_selection(self):
        """Clear all file selections"""
        self.file_listbox.selection_clear(0, tk.END)
        self.show_message("File selection cleared", "info")
    
    def load_files(self):
        """Load selected files"""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            self.show_message("Please select at least one file to load", "warning")
            return
        
        self.text_content = ""
        folder = self.working_folder.get()
        
        for idx in selected_indices:
            filename = self.file_listbox.get(idx).replace("📄 ", "")
            filepath = os.path.join(folder, filename)
            
            try:
                if filename.lower().endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.text_content += f.read() + "\n"
                
                elif filename.lower().endswith('.pdf'):
                    with open(filepath, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            self.text_content += page.extract_text() + "\n"
                
                elif filename.lower().endswith('.docx'):
                    doc = Document(filepath)
                    for paragraph in doc.paragraphs:
                        self.text_content += paragraph.text + "\n"
                
                elif filename.lower().endswith('.pptx'):
                    prs = Presentation(filepath)
                    for slide in prs.slides:
                        for shape in slide.shapes:
                            if hasattr(shape, "text"):
                                self.text_content += shape.text + "\n"
                
            except Exception as e:
                self.show_message(f"Error reading {filename}: {str(e)}", "fail")
                self.show_toast(f"Error reading {filename}", "danger")
        
        # Show success message in the message bar
        total_words = len(self.text_content.split())
        self.show_message(f"Successfully loaded {len(selected_indices)} file(s) with approximately {total_words:,} words", "good")
        self.show_toast(f"Files loaded successfully!", "success")
    
    def use_pasted_text(self):
        """Use text from text input widget"""
        self.text_content = self.text_input.get('1.0', tk.END).strip()
        if self.text_content:
            word_count = len(self.text_content.split())
            self.show_message(f"Text loaded successfully with approximately {word_count:,} words", "good")
            self.show_toast("Text loaded successfully", "success")
        else:
            self.show_message("Please paste some text into the text area first", "warning")
            self.show_toast("Please paste some text first", "warning")
    
    def update_min_label(self, value):
        """Update minimum length label"""
        val = int(float(value))
        self.min_word_length.set(val)
        self.min_length_label.config(text=f"{val} characters")
    
    def update_max_label(self, value):
        """Update maximum length label"""
        val = int(float(value))
        self.max_word_length.set(val)
        self.max_length_label.config(text=f"{val} characters")
    
    def update_forbidden_words(self):
        """Update forbidden words set"""
        text = self.forbidden_text.get('1.0', tk.END).strip()
        self.forbidden_words = set(STOPWORDS)
        if text:
            custom_forbidden = set(word.strip().lower() for word in text.split('\n') if word.strip())
            self.forbidden_words.update(custom_forbidden)
        self.show_toast(f"Updated forbidden words ({len(self.forbidden_words)} total)", "info")
    
    def on_color_select(self):
        """Handle color scheme selection"""
        color_name = self.color_var.get()
        self.selected_colormap = self.color_schemes[color_name]
        self.update_color_preview()
    
    def update_color_preview(self):
        """Update color scheme preview"""
        # Clear previous preview
        for widget in self.color_preview_frame.winfo_children():
            widget.destroy()
        
        # Create color gradient preview
        try:
            cmap = matplotlib.colormaps[self.selected_colormap]
            
            # Create a gradient image
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            gradient = np.vstack((gradient, gradient))
            
            fig, ax = plt.subplots(figsize=(6, 0.5), facecolor='white')
            fig.subplots_adjust(top=1, bottom=0, left=0, right=1)
            ax.imshow(gradient, aspect='auto', cmap=cmap)
            ax.set_axis_off()
            
            # Convert to PhotoImage
            buf = BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            img = Image.open(buf)
            photo = ImageTk.PhotoImage(img)
            
            # Display in label
            preview_label = ttk.Label(self.color_preview_frame, image=photo)
            preview_label.image = photo  # Keep reference
            preview_label.pack(fill=BOTH, expand=TRUE)
            
            plt.close(fig)
        except:
            pass
    
    def select_mask(self):
        """Select mask image file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                self.mask_image = np.array(Image.open(file_path))
                self.mask_path.set(os.path.basename(file_path))
                
                # Update the image mask label
                self.image_mask_label.config(text=os.path.basename(file_path))
                
                # Update mask preview
                img = Image.open(file_path)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                if hasattr(self, 'image_mask_preview_label'):
                    self.image_mask_preview_label.config(image=photo, text="")
                    self.image_mask_preview_label.image = photo  # Keep a reference
                
                # Enable contour options when mask is selected
                self.update_contour_state(True)
            except Exception as e:
                self.show_toast(f"Error loading mask: {str(e)}", "danger")
    
    def clear_mask(self):
        """Clear selected mask"""
        self.mask_image = None
        self.mask_path.set("No mask selected")
        
        # Clear appropriate preview label
        if self.mask_type.get() == "image" and hasattr(self, 'image_mask_preview_label'):
            self.image_mask_preview_label.config(image="", text="No mask selected")
            self.image_mask_label.config(text="No image selected")
        elif self.mask_type.get() == "text" and hasattr(self, 'text_mask_preview_label'):
            self.text_mask_preview_label.config(image="", text="No mask selected")
            self.text_mask_input.set("")
        
        # Disable contour options when mask is cleared
        self.update_contour_state(False)
    
    def create_text_mask(self, text, width=None, height=None, font_size=None):
        """Create a mask image from text"""
        if not text:
            return None
        
        # Use canvas dimensions if not specified
        if width is None:
            width = self.canvas_width.get()
        if height is None:
            height = self.canvas_height.get()
        if font_size is None:
            font_size = self.text_mask_font_size.get()
        
        # Create white image
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Get selected font
        selected_font = self.text_mask_font.get()
        font_name = self.available_fonts.get(selected_font, "Arial")
        
        # Build font style
        font_style = []
        if self.text_mask_bold.get():
            font_style.append("Bold")
        if self.text_mask_italic.get():
            font_style.append("Italic")
        
        # Try to load the font with style
        font = None
        font_attempts = []
        
        # First try with full style
        if font_style:
            font_attempts.append(f"{font_name} {' '.join(font_style)}")
        
        # Then try just the font name
        font_attempts.append(font_name)
        
        # Then try with .ttf extension
        font_attempts.append(f"{font_name.lower().replace(' ', '')}.ttf")
        
        # Try each font attempt
        for attempt in font_attempts:
            try:
                font = ImageFont.truetype(attempt, font_size)
                break
            except:
                continue
        
        # Fallback fonts
        if font is None:
            fallback_fonts = ["arial.ttf", "Arial", "helvetica", "verdana"]
            for fallback in fallback_fonts:
                try:
                    font = ImageFont.truetype(fallback, font_size)
                    break
                except:
                    continue
        
        # Final fallback to default
        if font is None:
            font = ImageFont.load_default()
        
        # Handle multi-line text
        words_per_line = self.text_mask_words_per_line.get()
        if words_per_line > 1:
            # Split text into words and group them
            words = text.split()
            lines = []
            for i in range(0, len(words), words_per_line):
                lines.append(' '.join(words[i:i+words_per_line]))
            text_to_draw = '\n'.join(lines)
        else:
            text_to_draw = text
        
        # Get text boundaries for multi-line text
        bbox = draw.textbbox((0, 0), text_to_draw, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text in black (multiline will be handled automatically)
        draw.text((x, y), text_to_draw, fill='black', font=font, align='center')
        
        # Convert to numpy array
        return np.array(img)
    
    def update_text_mask(self):
        """Update the text mask when text or settings change"""
        if self.mask_type.get() == "text" and self.text_mask_input.get():
            # Generate text mask
            self.mask_image = self.create_text_mask(self.text_mask_input.get())
            self.mask_path.set(f"Text: {self.text_mask_input.get()}")
            
            # Update preview
            self.update_mask_preview()
            
            # Enable contour options
            self.update_contour_state(True)
    
    def update_mask_preview(self):
        """Update the mask preview display"""
        if self.mask_image is not None:
            # Convert numpy array to PIL Image for preview
            if len(self.mask_image.shape) == 3:
                preview_img = Image.fromarray(self.mask_image.astype('uint8'), 'RGB')
            else:
                preview_img = Image.fromarray(self.mask_image.astype('uint8'), 'L')
            
            # Thumbnail for preview
            preview_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)
            
            # Update appropriate preview label
            if self.mask_type.get() == "text" and hasattr(self, 'text_mask_preview_label'):
                self.text_mask_preview_label.config(image=photo, text="")
                self.text_mask_preview_label.image = photo
            elif self.mask_type.get() == "image" and hasattr(self, 'image_mask_preview_label'):
                self.image_mask_preview_label.config(image=photo, text="")
                self.image_mask_preview_label.image = photo
    
    def update_contour_width(self, value, label=None):
        """Update contour width label"""
        val = int(float(value))
        self.contour_width.set(val)
        if label:
            label.config(text=f"{val} pixels")
        elif hasattr(self, 'contour_width_label'):
            self.contour_width_label.config(text=f"{val} pixels")
    
    def choose_contour_color(self, preview_frame=None):
        """Open color chooser for contour color"""
        dialog = ColorChooserDialog()
        dialog.show()
        color = dialog.result
        if color:
            hex_color = color.hex
            self.contour_color.set(hex_color)
            # Update preview - ttk frames don't support background, use style instead
            style = ttk.Style()
            style_name = f"ContourPreview.TFrame"
            style.configure(style_name, background=hex_color)
            if preview_frame:
                preview_frame.configure(style=style_name)
            elif hasattr(self, 'contour_color_preview'):
                self.contour_color_preview.configure(style=style_name)
    
    def choose_bg_color(self):
        """Open color chooser for background color"""
        dialog = ColorChooserDialog()
        dialog.show()
        color = dialog.result
        if color:
            hex_color = color.hex
            self.bg_color.set(hex_color)
            # Update preview - ttk frames don't support background, use style instead
            style = ttk.Style()
            style_name = f"BgPreview.TFrame"
            style.configure(style_name, background=hex_color)
            self.bg_color_preview.configure(style=style_name)
    
    def clear_canvas(self):
        """Clear the canvas completely"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')
        ax.axis('off')
        self.figure.patch.set_facecolor('white')
        self.canvas.draw()
        
        # Disable save button since there's nothing to save
        if hasattr(self, 'save_btn'):
            self.save_btn.config(state=DISABLED)
        
        # Clear any stored wordcloud
        if hasattr(self, 'current_wordcloud'):
            self.current_wordcloud = None
    
    def update_preview_size(self, *args):
        """Update preview canvas size when dimensions change"""
        try:
            # Calculate new display size
            display_width, display_height = self.calculate_preview_size()
            
            # Update figure size for display
            self.figure.set_size_inches(display_width/100, display_height/100)
            
            # Update scale indicator
            actual_width = self.canvas_width.get()
            actual_height = self.canvas_height.get()
            if display_width < actual_width or display_height < actual_height:
                reduction = 100 - int((display_width / actual_width) * 100)
                self.scale_indicator.config(text=f"Preview reduced by {reduction}% to fit screen")
            else:
                self.scale_indicator.config(text="")
            
            # Clear canvas when size changes
            self.clear_canvas()
        except:
            pass  # Ignore errors during initialization
    
    def update_contour_state(self, has_mask=None):
        """Enable/disable contour options based on mask selection"""
        if has_mask is None:
            has_mask = self.mask_image is not None
        
        state = NORMAL if has_mask else DISABLED
        
        for widget in self.contour_widgets:
            try:
                widget.configure(state=state)
            except:
                pass  # Some widgets might not support state
        
        # Update frame title
        if has_mask:
            self.contour_frame.configure(text="Contour Options")
        else:
            self.contour_frame.configure(text="Contour Options (requires mask)")
    
    def update_horizontal_label(self, value):
        """Update prefer horizontal label"""
        val = float(value)
        self.prefer_horizontal.set(val)
        self.horizontal_label.config(text=f"{int(val * 100)}%")
    
    def update_max_words(self, value):
        """Update max words label and clear canvas"""
        val = int(float(value))
        self.max_words.set(val)
        self.max_words_label.config(text=str(val))
        self.clear_canvas()
    
    def update_scale(self, value):
        """Update scale label and clear canvas"""
        val = int(float(value))
        self.scale.set(val)
        self.scale_label.config(text=str(val))
        self.clear_canvas()
    
    def update_mode(self):
        """Update mode between RGB and RGBA"""
        if self.rgba_mode.get():
            # RGBA mode - disable background color
            self.bg_label.configure(state=DISABLED)
            self.bg_color_btn.configure(state=DISABLED)
            self.show_toast("RGBA mode enabled - background will be transparent", "info")
        else:
            # RGB mode - enable background color
            self.bg_label.configure(state=NORMAL)
            self.bg_color_btn.configure(state=NORMAL)
            self.show_toast("RGB mode enabled - solid background", "info")
    
    def filter_words(self, text):
        """Filter words based on length and forbidden words"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Update forbidden words
        self.update_forbidden_words()
        
        # Filter words
        filtered_words = []
        min_len = self.min_word_length.get()
        max_len = self.max_word_length.get()
        
        for word in words:
            if (min_len <= len(word) <= max_len and 
                word not in self.forbidden_words):
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def generate_wordcloud(self):
        """Generate word cloud in a separate thread"""
        if not self.text_content:
            self.show_message("No text content available. Please load files or paste text first.", "warning")
            self.show_toast("Please load text from files or paste text first", "warning")
            return
        
        # Show progress and disable button
        self.generate_btn.config(state=DISABLED)
        self.progress.pack(fill=X, pady=(0, 10))
        self.progress.start(10)
        
        # Run generation in separate thread
        thread = threading.Thread(target=self._generate_wordcloud_thread)
        thread.start()
    
    def _generate_wordcloud_thread(self):
        """Generate word cloud (thread function)"""
        try:
            # Filter words
            filtered_text = self.filter_words(self.text_content)
            
            if not filtered_text:
                self.root.after(0, lambda: self.show_toast("No words found after filtering", "warning"))
                return
            
            # Create word cloud
            wc_params = {
                'width': self.canvas_width.get(),
                'height': self.canvas_height.get(),
                'colormap': self.selected_colormap,
                'max_words': int(self.max_words.get()),
                'scale': self.scale.get(),
                'relative_scaling': 0.5,
                'min_font_size': 10,
                'prefer_horizontal': self.prefer_horizontal.get()
            }
            
            # Set background and mode
            if self.rgba_mode.get():
                wc_params['mode'] = 'RGBA'
                wc_params['background_color'] = None
            else:
                wc_params['mode'] = 'RGB'
                wc_params['background_color'] = self.bg_color.get()
            
            if self.mask_image is not None:
                wc_params['mask'] = self.mask_image
                if self.contour_width.get() > 0:
                    wc_params['contour_width'] = self.contour_width.get()
                    wc_params['contour_color'] = self.contour_color.get()
            
            self.wordcloud = WordCloud(**wc_params).generate(filtered_text)
            
            # Update UI in main thread
            self.root.after(0, self._update_preview)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_toast(f"Error generating word cloud: {str(e)}", "danger"))
        finally:
            self.root.after(0, self._generation_complete)
    
    def _update_preview(self):
        """Update the preview canvas with generated word cloud"""
        # Ensure preview size is updated
        display_width, display_height = self.calculate_preview_size()
        self.figure.set_size_inches(display_width/100, display_height/100)
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get the word cloud as an image (full resolution)
        wc_image = self.wordcloud.to_image()
        
        if self.rgba_mode.get():
            # For RGBA mode, create a checkered background to show transparency
            import numpy as np
            
            # Create checkered pattern at display resolution
            checker_size = 20
            checkerboard = np.zeros((display_height, display_width, 3))
            for i in range(0, display_height, checker_size * 2):
                for j in range(0, display_width, checker_size * 2):
                    checkerboard[i:i+checker_size, j:j+checker_size] = 0.9
                    checkerboard[i+checker_size:i+2*checker_size, j+checker_size:j+2*checker_size] = 0.9
            for i in range(checker_size, display_height, checker_size * 2):
                for j in range(0, display_width, checker_size * 2):
                    checkerboard[i:i+checker_size, j:j+checker_size] = 0.95
            for i in range(0, display_height, checker_size * 2):
                for j in range(checker_size, display_width, checker_size * 2):
                    checkerboard[i:i+checker_size, j:j+checker_size] = 0.95
            
            # Show checkerboard first
            ax.imshow(checkerboard)
            
            # Overlay the word cloud (will be automatically scaled to fit)
            ax.imshow(wc_image, interpolation='bilinear', alpha=1.0)
        else:
            # For RGB mode, just show the image
            ax.imshow(wc_image, interpolation='bilinear')
        
        ax.axis('off')
        
        # Add size indicator if preview is scaled down
        actual_width = self.canvas_width.get()
        actual_height = self.canvas_height.get()
        if display_width < actual_width or display_height < actual_height:
            scale_percent = int((display_width / actual_width) * 100)
            reduction = 100 - scale_percent
            ax.text(0.02, 0.98, f"Preview reduced by {reduction}% to fit\nActual size: {actual_width}×{actual_height}px\nPreview size: {display_width}×{display_height}px", 
                   transform=ax.transAxes, 
                   fontsize=9, 
                   verticalalignment='top',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9, edgecolor='gray'))
        
        self.canvas.draw()
        
        # Enable save button and show success
        self.save_btn.config(state=NORMAL)
        mode_text = "with transparency" if self.rgba_mode.get() else "with solid background"
        self.show_toast(f"Word cloud generated successfully {mode_text}!", "success")
    
    def _generation_complete(self):
        """Called when generation is complete"""
        self.progress.stop()
        self.progress.pack_forget()
        self.generate_btn.config(state=NORMAL)
    
    def save_wordcloud(self):
        """Save generated word cloud"""
        if not hasattr(self, 'wordcloud'):
            self.show_toast("Please generate a word cloud first", "warning")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Handle different file formats
                if file_path.lower().endswith('.svg'):
                    # For SVG, we need to use a different method
                    import io
                    svg_text = self.wordcloud.to_svg()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(svg_text)
                else:
                    # For PNG/JPEG
                    if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                        if self.rgba_mode.get():
                            self.show_message("JPEG format doesn't support transparency. Image will have white background.", "warning")
                    
                    self.wordcloud.to_file(file_path)
                    
                self.show_message(f"Word cloud saved successfully to: {os.path.basename(file_path)}", "good")
                self.show_toast(f"Word cloud saved successfully!", "success")
            except Exception as e:
                self.show_toast(f"Error saving word cloud: {str(e)}", "danger")

    def get_system_fonts(self):
        """Discover fonts available on the system"""
        fonts = set()
        system = platform.system()
        
        if system == "Windows":
            # Windows font directories
            font_dirs = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
            ]
            
            for font_dir in font_dirs:
                if os.path.exists(font_dir):
                    try:
                        for font_file in os.listdir(font_dir):
                            if font_file.lower().endswith(('.ttf', '.otf')):
                                # Try to extract font name from file
                                font_path = os.path.join(font_dir, font_file)
                                try:
                                    # Try to load and get font name
                                    font = ImageFont.truetype(font_path, 12)
                                    # Use filename without extension as fallback
                                    font_name = os.path.splitext(font_file)[0]
                                    fonts.add(font_name)
                                except:
                                    pass
                    except:
                        pass
            
            # Also try to get fonts from registry (more reliable for font names)
            try:
                import winreg
                reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            # Extract font name from registry entry
                            font_name = name.split(' (')[0]  # Remove style info
                            fonts.add(font_name)
                            i += 1
                        except WindowsError:
                            break
            except:
                pass
                
        elif system == "Darwin":  # macOS
            font_dirs = [
                "/System/Library/Fonts",
                "/Library/Fonts",
                os.path.expanduser("~/Library/Fonts")
            ]
            
            for font_dir in font_dirs:
                if os.path.exists(font_dir):
                    try:
                        for font_file in os.listdir(font_dir):
                            if font_file.lower().endswith(('.ttf', '.otf', '.ttc')):
                                font_name = os.path.splitext(font_file)[0]
                                fonts.add(font_name)
                    except:
                        pass
                        
        else:  # Linux
            # Try fc-list command
            try:
                result = subprocess.run(['fc-list', ':family'], 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            # Extract font family name
                            font_name = line.split(':')[0].strip()
                            fonts.add(font_name)
            except:
                # Fallback to common font directories
                font_dirs = [
                    "/usr/share/fonts",
                    "/usr/local/share/fonts",
                    os.path.expanduser("~/.fonts")
                ]
                
                for font_dir in font_dirs:
                    if os.path.exists(font_dir):
                        for root, dirs, files in os.walk(font_dir):
                            for font_file in files:
                                if font_file.lower().endswith(('.ttf', '.otf')):
                                    font_name = os.path.splitext(font_file)[0]
                                    fonts.add(font_name)
        
        return sorted(list(fonts))
    
    def validate_fonts(self):
        """Check which fonts are actually available on the system"""
        # Show loading message
        self.root.after(0, lambda: self.show_message("Discovering available fonts...", "info"))
        
        # Get system fonts
        system_fonts = self.get_system_fonts()
        
        # Create a dict of validated fonts
        available = {}
        
        # First, add some guaranteed fallback fonts
        fallback_fonts = {
            "Arial": "Arial",
            "Times New Roman": "Times New Roman",
            "Courier New": "Courier New",
            "Verdana": "Verdana"
        }
        
        # Test common fonts that should work
        common_fonts = {
            "Arial": ["Arial", "arial", "arial.ttf"],
            "Arial Black": ["Arial Black", "ariblk", "ariblk.ttf"],
            "Impact": ["Impact", "impact", "impact.ttf"],
            "Times New Roman": ["Times New Roman", "times", "times.ttf"],
            "Georgia": ["Georgia", "georgia", "georgia.ttf"],
            "Verdana": ["Verdana", "verdana", "verdana.ttf"],
            "Comic Sans MS": ["Comic Sans MS", "comic", "comic.ttf"],
            "Trebuchet MS": ["Trebuchet MS", "trebuc", "trebuc.ttf"],
            "Courier New": ["Courier New", "cour", "cour.ttf"],
            "Calibri": ["Calibri", "calibri", "calibri.ttf"],
            "Cambria": ["Cambria", "cambria", "cambria.ttc"],
            "Tahoma": ["Tahoma", "tahoma", "tahoma.ttf"],
            "Century Gothic": ["Century Gothic", "GOTHIC", "GOTHIC.TTF"],
            "Palatino Linotype": ["Palatino Linotype", "pala", "pala.ttf"],
            "Consolas": ["Consolas", "consola", "consola.ttf"],
            "Segoe UI": ["Segoe UI", "segoeui", "segoeui.ttf"]
        }
        
        # Test each common font
        for display_name, attempts in common_fonts.items():
            for attempt in attempts:
                try:
                    ImageFont.truetype(attempt, 12)
                    available[display_name] = attempt
                    break
                except:
                    continue
        
        # Also check system fonts that match our patterns
        for font in system_fonts:
            # Clean up font name for display
            display_name = font.replace('-', ' ').replace('_', ' ')
            
            # Skip if we already have this font
            if display_name in available:
                continue
                
            # Try to load it
            attempts = [
                font,
                f"{font}.ttf",
                f"{font}.otf",
                font.lower(),
                font.replace(' ', ''),
                font.replace(' ', '-')
            ]
            
            for attempt in attempts:
                try:
                    ImageFont.truetype(attempt, 12)
                    available[display_name] = attempt
                    break
                except:
                    continue
        
        # Update available fonts
        if available:
            self.available_fonts = available
            sorted_fonts = sorted(list(available.keys()))
            self.text_mask_font.set(sorted_fonts[0])
            
            # Update font listbox if it exists (in main thread)
            def update_ui():
                if hasattr(self, 'font_listbox'):
                    self.font_listbox.set_fonts(available)
                self.show_message(f"Found {len(available)} fonts available on your system", "good")
            
            self.root.after(0, update_ui)
    
    def show_toast(self, message, style="info"):
        """Show toast notification"""
        toast = ToastNotification(
            title="WordCloud Magic",
            message=message,
            duration=3000,
            bootstyle=style
        )
        toast.show_toast()

    def change_theme(self, event=None):
        """Change the application theme"""
        new_theme = self.current_theme.get()
        self.root.style.theme_use(new_theme)
        
        # Update any theme-specific elements
        self.show_toast(f"Theme changed to {new_theme}", "info")
        
        # Update canvas background if needed
        if new_theme in ["darkly", "superhero", "solar", "cyborg", "vapor"]:
            # Dark themes - adjust canvas
            self.figure.patch.set_facecolor('#2b2b2b')
        else:
            # Light themes
            self.figure.patch.set_facecolor('white')
        self.canvas.draw()

def main():
    # Create the app with a modern theme
    root = ttk.Window(themename="cosmo")
    app = ModernWordCloudApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()