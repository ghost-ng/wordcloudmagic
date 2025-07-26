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
import json
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
matplotlib.use('TkAgg')
import sys
import argparse
import traceback
import logging
from datetime import datetime

# File handling imports
import PyPDF2
from docx import Document
from pptx import Presentation
import re
from io import BytesIO
import webbrowser
import tempfile

# Import tutorial wizard
from tutorial_wizard import TutorialWizard

# Global debug flag and logger
DEBUG = False
debug_logger = None

def setup_debug_logging():
    """Setup debug logging to both console and file"""
    global debug_logger
    
    # Create logger
    debug_logger = logging.getLogger('wordcloud_debug')
    debug_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    debug_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # File handler - create debug log in logs directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, f"wordcloud_debug_{timestamp}.log")
    file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    debug_logger.addHandler(console_handler)
    debug_logger.addHandler(file_handler)
    
    # Log initial info
    debug_logger.info(f"Debug logging started - Log file: {log_filename}")
    
    return log_filename

def debug_print(*args, **kwargs):
    """Print debug messages when DEBUG mode is enabled"""
    if DEBUG and debug_logger:
        message = " ".join(str(arg) for arg in args)
        debug_logger.debug(message)

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
                                                  fill='#e1f0ff',
                                                  outline='#0078d4',
                                                  width=2,
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
            self.canvas.itemconfig(item['text_id'], fill='#0078d4', font=tkFont.Font(family=self.fonts_loaded.get(item['name'], 'Segoe UI'), size=12, weight='bold'))
            
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
    def create_custom_gradients(self):
        """Create and register custom color gradients"""
        gradients = {}
        
        # Sunset Sky - Orange → Pink → Purple
        sunset_colors = ['#FF8C00', '#FF69B4', '#8B008B']
        gradients['sunset_sky'] = LinearSegmentedColormap.from_list('sunset_sky', sunset_colors)
        
        # Deep Ocean - Deep Blue → Teal → Light Blue
        ocean_colors = ['#000080', '#008B8B', '#87CEEB']
        gradients['deep_ocean'] = LinearSegmentedColormap.from_list('deep_ocean', ocean_colors)
        
        # Forest - Dark Green → Green → Light Green
        forest_colors = ['#006400', '#228B22', '#90EE90']
        gradients['forest'] = LinearSegmentedColormap.from_list('forest', forest_colors)
        
        # Fire - Red → Orange → Yellow
        fire_colors = ['#DC143C', '#FF8C00', '#FFD700']
        gradients['fire'] = LinearSegmentedColormap.from_list('fire', fire_colors)
        
        # Cotton Candy - Pink → Light Blue → Lavender
        cotton_colors = ['#FFB6C1', '#87CEFA', '#E6E6FA']
        gradients['cotton_candy'] = LinearSegmentedColormap.from_list('cotton_candy', cotton_colors)
        
        # Fall Leaves - Brown → Orange → Gold
        fall_colors = ['#8B4513', '#FF8C00', '#FFD700']
        gradients['fall_leaves'] = LinearSegmentedColormap.from_list('fall_leaves', fall_colors)
        
        # Berry - Deep Purple → Magenta → Pink
        berry_colors = ['#4B0082', '#FF00FF', '#FFC0CB']
        gradients['berry'] = LinearSegmentedColormap.from_list('berry', berry_colors)
        
        # Mint - Dark Teal → Mint → White
        mint_colors = ['#008080', '#98FB98', '#FFFFFF']
        gradients['mint'] = LinearSegmentedColormap.from_list('mint', mint_colors)
        
        # Volcano - Black → Red → Orange → Yellow
        volcano_colors = ['#000000', '#8B0000', '#FF4500', '#FFFF00']
        gradients['volcano'] = LinearSegmentedColormap.from_list('volcano', volcano_colors)
        
        # Aurora (Northern Lights) - Dark Blue → Green → Purple → Pink
        aurora_colors = ['#191970', '#00FF00', '#9370DB', '#FF1493']
        gradients['aurora'] = LinearSegmentedColormap.from_list('aurora', aurora_colors)
        
        # Hacker - Lime Green → Black
        hacker_colors = ['#00FF00', '#00AA00', '#005500', '#000000']
        gradients['hacker'] = LinearSegmentedColormap.from_list('hacker', hacker_colors)
        
        # Solarized Dark
        solarized_dark_colors = ['#002b36', '#073642', '#586e75', '#657b83', '#839496', '#93a1a1']
        gradients['solarized_dark'] = LinearSegmentedColormap.from_list('solarized_dark', solarized_dark_colors)
        
        # Solarized Light
        solarized_light_colors = ['#fdf6e3', '#eee8d5', '#93a1a1', '#839496', '#657b83', '#586e75']
        gradients['solarized_light'] = LinearSegmentedColormap.from_list('solarized_light', solarized_light_colors)
        
        # Rose Pine
        rose_pine_colors = ['#191724', '#1f1d2e', '#403d52', '#e0def4', '#eb6f92', '#f6c177']
        gradients['rose_pine'] = LinearSegmentedColormap.from_list('rose_pine', rose_pine_colors)
        
        # Grape - Deep Purple → Light Purple
        grape_colors = ['#2D1B69', '#512DA8', '#7E57C2', '#AB47BC', '#CE93D8']
        gradients['grape'] = LinearSegmentedColormap.from_list('grape', grape_colors)
        
        # Dracula
        dracula_colors = ['#282a36', '#44475a', '#6272a4', '#bd93f9', '#ff79c6', '#f8f8f2']
        gradients['dracula'] = LinearSegmentedColormap.from_list('dracula', dracula_colors)
        
        # Gruvbox
        gruvbox_colors = ['#282828', '#3c3836', '#504945', '#928374', '#d5c4a1', '#fbf1c7']
        gradients['gruvbox'] = LinearSegmentedColormap.from_list('gruvbox', gruvbox_colors)
        
        # Monokai
        monokai_colors = ['#272822', '#49483e', '#75715e', '#a6e22e', '#f92672', '#66d9ef']
        gradients['monokai'] = LinearSegmentedColormap.from_list('monokai', monokai_colors)
        
        # Army - Military Greens
        army_colors = ['#4B5320', '#556B2F', '#6B8E23', '#8FBC8F', '#90EE90']
        gradients['army'] = LinearSegmentedColormap.from_list('army', army_colors)
        
        # Air Force - Sky Blues
        airforce_colors = ['#00308F', '#0047AB', '#4169E1', '#6495ED', '#87CEEB']
        gradients['airforce'] = LinearSegmentedColormap.from_list('airforce', airforce_colors)
        
        # Cyber - Neon Cyan → Dark
        cyber_colors = ['#000000', '#0D0D0D', "#A6FF00", "#00D10A", '#1E90FF']
        gradients['cyber'] = LinearSegmentedColormap.from_list('cyber', cyber_colors)
        
        # Navy - Deep Ocean Blues
        navy_colors = ['#000080', '#002FA7', '#003F87', '#1560BD', '#4682B4']
        gradients['navy'] = LinearSegmentedColormap.from_list('navy', navy_colors)
        
        # Register all custom colormaps with matplotlib
        for name, cmap in gradients.items():
            matplotlib.colormaps.register(cmap, name=name)
        
        return gradients
    
    def __init__(self, root):
        debug_print("Initializing ModernWordCloudApp")
        self.root = root
        self.root.title("WordCloud Magic - Modern Word Cloud Generator")
        self.root.geometry("1300x850")
        self.root.state('zoomed')  # Start maximized
        
        # Flag to track UI readiness
        self.ui_ready = False
        
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
        self.image_mask_file_path = None  # Store full path of image mask
        self.min_word_length = tk.IntVar(value=3)
        self.max_word_length = tk.IntVar(value=20)
        self.forbidden_words = set(STOPWORDS)
        self.selected_colormap = "viridis"
        self.color_mode = tk.StringVar(value="preset")  # "single", "preset", or "custom"
        self.single_color = tk.StringVar(value="#0078D4")
        self.custom_gradient_colors = ["#FF0000", "#00FF00", "#0000FF"]  # Default RGB
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
        debug_print(f"Initialized contour_width with default value: 2")
        # Add trace to monitor changes
        self.contour_width.trace('w', lambda *args: debug_print(f"contour_width changed to: {self.contour_width.get()}"))
        self.contour_color = tk.StringVar(value="#000000")
        self.contour_widgets = []  # Keep track of contour widgets
        
        # Word orientation and mode
        self.prefer_horizontal = tk.DoubleVar(value=0.9)
        self.rgba_mode = tk.BooleanVar(value=False)
        self.max_words = tk.IntVar(value=200)
        self.scale = tk.IntVar(value=1)
        
        # Create custom gradients
        self.custom_gradients = self.create_custom_gradients()
        
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
            "Paired": "Paired",
            # New custom gradients
            "Sunset Sky": "sunset_sky",
            "Deep Ocean": "deep_ocean",
            "Forest": "forest",
            "Fire": "fire",
            "Cotton Candy": "cotton_candy",
            "Fall Leaves": "fall_leaves",
            "Berry": "berry",
            "Mint": "mint",
            "Volcano": "volcano",
            "Aurora": "aurora",
            "Hacker": "hacker",
            "SolarizedDk": "solarized_dark",
            "SolarizedLt": "solarized_light",
            "Rose Pine": "rose_pine",
            "Grape": "grape",
            "Dracula": "dracula",
            "Gruvbox": "gruvbox",
            "Monokai": "monokai",
            "Army": "army",
            "Air Force": "airforce",
            "Cyber": "cyber",
            "Navy": "navy"
        }
        
        self.create_ui()
        
        # Mark UI as ready
        self.ui_ready = True
        
        # Initialize tutorial wizard after UI is ready
        self.tutorial_wizard = TutorialWizard(self, self.root)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Auto-load configuration if exists (after UI is created)
        self.root.after(100, self.auto_load_config)
        
        # Validate available fonts after UI creation (in a thread to avoid blocking)
        threading.Thread(target=self.validate_fonts, daemon=True).start()
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Load Config", command=self.import_config)
        file_menu.add_command(label="Save Config As...", command=self.export_config)
        file_menu.add_command(label="Save Config", command=self.save_config_locally)
        file_menu.add_separator()
        file_menu.add_command(label="Reset", command=self.reset_app)
        file_menu.add_separator()
        file_menu.add_command(label="Start Tutorial", command=self.start_tutorial_wizard)
        file_menu.add_command(label="Help", command=self.show_help)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
    def create_ui(self):
        """Create the main UI"""
        # Create menu bar
        self.create_menu()
        
        # Top bar for theme selection and messages
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=X, padx=10, pady=(10, 5))
        
        # Create message bar on the left side of top bar
        self.create_message_bar(top_bar)
        
        # Theme selector on the right
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
        self.file_list_frame = file_frame  # Store reference for tutorial
        
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
        self.length_frame = length_frame  # Store reference for tutorial
        
        # Min length with meter
        min_container = ttk.Frame(length_frame)
        min_container.pack(fill=X, pady=(0, 20))
        
        min_label_frame = ttk.Frame(min_container)
        min_label_frame.pack(fill=X)
        ttk.Label(min_label_frame, text="Minimum Length:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.min_length_label = ttk.Label(min_label_frame, text=f"{self.min_word_length.get()} characters", 
                                         bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.min_length_label.pack(side=RIGHT)
        
        self.min_length_scale = ttk.Scale(min_container,
                                         from_=1,
                                         to=10,
                                         variable=self.min_word_length,
                                         command=self.update_min_label,
                                         bootstyle="primary")
        self.min_length_scale.pack(fill=X, pady=(5, 0))
        
        # Max length with meter
        max_container = ttk.Frame(length_frame)
        max_container.pack(fill=X)
        
        max_label_frame = ttk.Frame(max_container)
        max_label_frame.pack(fill=X)
        ttk.Label(max_label_frame, text="Maximum Length:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.max_length_label = ttk.Label(max_label_frame, text=f"{self.max_word_length.get()} characters",
                                         bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.max_length_label.pack(side=RIGHT)
        
        self.max_length_scale = ttk.Scale(max_container,
                                         from_=10,
                                         to=50,
                                         variable=self.max_word_length,
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
        
        # Pre-populate with common stop words - expanded list
        self.default_forbidden = """the
and
or
but
in
on
at
to
for
of
with
by
from
as
is
was
are
been
be
have
has
had
do
does
did
will
would
should
could
may
might
must
can
shall
a
an
these
those
this
that
their
there
they
them
he
she
it
we
you
i
me
my
our
your
his
her
its
their
what
which
who
when
where
why
how
all
each
every
some
any
few
more
most
other
such
no
not
only
own
same
so
than
too
very
just
also
now
then
here
there
up
down
out
off
over
under
about
into
through
during
before
after
above
below
between
under
since
without
within
along
among
around
however
therefore
moreover
furthermore
otherwise
nevertheless
nonetheless
still
yet
already
always
never
often
sometimes
usually
generally
specifically
particularly
especially
mainly
mostly
simply
actually
really
indeed
certainly
definitely
probably
possibly
perhaps
maybe"""
        self.forbidden_text.insert('1.0', self.default_forbidden)
        
        # Button frame
        button_frame = ttk.Frame(forbidden_frame)
        button_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(button_frame,
                  text="Update",
                  command=self.update_forbidden_words,
                  bootstyle="warning",
                  width=20).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(button_frame,
                  text="Reset to Default",
                  command=self.reset_forbidden_words,
                  bootstyle="secondary",
                  width=15).pack(side=LEFT)
        
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
        
        # Create the window and store its ID
        self.style_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Function to update canvas window width
        def update_style_canvas_width(event=None):
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Ensure canvas has been drawn
                canvas.itemconfig(self.style_window_id, width=canvas_width)
        
        # Bind canvas resize to update window width
        canvas.bind("<Configure>", update_style_canvas_width)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Update width after canvas is displayed
        canvas.after(100, update_style_canvas_width)
        
        # Add padding to scrollable frame
        style_frame = ttk.Frame(scrollable_frame, padding="20")
        style_frame.pack(fill="both", expand=True)
        
        # Bind mouse wheel to this specific canvas
        def _on_style_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Store the current binding
        self._style_wheel_bound = False
        
        def _bind_style_mousewheel(event):
            if not self._style_wheel_bound:
                canvas.bind("<MouseWheel>", _on_style_mousewheel)
                self._style_wheel_bound = True
        
        def _unbind_style_mousewheel(event):
            if self._style_wheel_bound:
                canvas.unbind("<MouseWheel>")
                self._style_wheel_bound = False
        
        # Bind/unbind mousewheel when entering/leaving the canvas
        canvas.bind('<Enter>', _bind_style_mousewheel)
        canvas.bind('<Leave>', _unbind_style_mousewheel)
        
        # Color scheme selection
        color_frame = self.create_section(style_frame, "Color Scheme")
        self.color_scheme_frame = color_frame  # Store reference for tutorial
        
        # Color mode selection
        mode_frame = ttk.Frame(color_frame)
        mode_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Single Color", variable=self.color_mode, 
                       value="single", command=self.on_color_mode_change,
                       bootstyle="primary").pack(side=LEFT, padx=(0, 15))
        
        ttk.Radiobutton(mode_frame, text="Preset Gradients", variable=self.color_mode,
                       value="preset", command=self.on_color_mode_change,
                       bootstyle="primary").pack(side=LEFT, padx=(0, 15))
        
        ttk.Radiobutton(mode_frame, text="Custom Gradient", variable=self.color_mode,
                       value="custom", command=self.on_color_mode_change,
                       bootstyle="primary").pack(side=LEFT)
        
        ttk.Separator(color_frame, orient='horizontal').pack(fill=X, pady=(5, 10))
        
        # Create notebook for different color modes
        self.color_notebook = ttk.Notebook(color_frame)
        self.color_notebook.pack(fill=BOTH, expand=TRUE)
        
        # Single color tab
        single_tab = ttk.Frame(self.color_notebook)
        self.color_notebook.add(single_tab, text="Single Color")
        
        single_color_frame = ttk.Frame(single_tab, padding=20)
        single_color_frame.pack(fill=X)
        
        ttk.Label(single_color_frame, text="Color:", font=('Segoe UI', 10)).pack(side=LEFT)
        
        self.single_color_preview = ttk.Frame(single_color_frame, width=30, height=30)
        self.single_color_preview.pack(side=LEFT, padx=(10, 10))
        
        # Set initial color preview
        style = ttk.Style()
        style_name = "SingleColorPreview.TFrame"
        style.configure(style_name, background=self.single_color.get())
        self.single_color_preview.configure(style=style_name)
        
        self.single_color_btn = ttk.Button(single_color_frame,
                                         text="Choose Color",
                                         command=self.choose_single_color,
                                         bootstyle="primary-outline")
        self.single_color_btn.pack(side=LEFT)
        
        # Preset gradients tab
        preset_tab = ttk.Frame(self.color_notebook)
        self.color_notebook.add(preset_tab, text="Preset Gradients")
        
        # Create scrollable frame for preset color buttons
        preset_canvas = tk.Canvas(preset_tab, height=300)
        preset_scrollbar = ttk.Scrollbar(preset_tab, orient="vertical", command=preset_canvas.yview)
        preset_scrollable = ttk.Frame(preset_canvas)
        
        preset_scrollable.bind(
            "<Configure>",
            lambda e: preset_canvas.configure(scrollregion=preset_canvas.bbox("all"))
        )
        
        # Create the window and store its ID
        self.preset_window_id = preset_canvas.create_window((0, 0), window=preset_scrollable, anchor="nw")
        preset_canvas.configure(yscrollcommand=preset_scrollbar.set)
        
        # Function to update canvas window width
        def update_preset_canvas_width(event=None):
            canvas_width = preset_canvas.winfo_width()
            if canvas_width > 1:  # Ensure canvas has been drawn
                preset_canvas.itemconfig(self.preset_window_id, width=canvas_width)
        
        # Bind canvas resize to update window width
        preset_canvas.bind("<Configure>", update_preset_canvas_width)
        
        preset_canvas.pack(side="left", fill="both", expand=True)
        preset_scrollbar.pack(side="right", fill="y")
        
        # Update width after canvas is displayed
        preset_canvas.after(100, update_preset_canvas_width)
        
        # Bind mouse wheel to preset canvas only
        def _on_preset_mousewheel(event):
            preset_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # Stop propagation
            return "break"
        
        # Direct binding to the preset canvas
        preset_canvas.bind("<MouseWheel>", _on_preset_mousewheel)
        
        # Also bind to the scrollable frame inside
        preset_scrollable.bind("<MouseWheel>", _on_preset_mousewheel)
        
        # Custom gradient tab
        custom_tab = ttk.Frame(self.color_notebook)
        self.color_notebook.add(custom_tab, text="Custom Gradient")
        
        custom_frame = ttk.Frame(custom_tab, padding=20)
        custom_frame.pack(fill=BOTH, expand=TRUE)
        
        ttk.Label(custom_frame, text="Create your own gradient:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=W, pady=(0, 10))
        
        # Custom gradient colors
        self.custom_color_frames = []
        self.custom_color_previews = []
        
        for i in range(3):
            color_row = ttk.Frame(custom_frame)
            color_row.pack(fill=X, pady=5)
            
            ttk.Label(color_row, text=f"Color {i+1}:", width=10).pack(side=LEFT)
            
            preview = ttk.Frame(color_row, width=30, height=30)
            preview.pack(side=LEFT, padx=(5, 10))
            self.custom_color_previews.append(preview)
            
            btn = ttk.Button(color_row, text="Choose", 
                           command=lambda idx=i: self.choose_custom_color(idx),
                           bootstyle="secondary-outline")
            btn.pack(side=LEFT)
            
            self.custom_color_frames.append(color_row)
        
        # Update custom color previews
        self.update_custom_gradient_preview()
        
        # Add/Remove color buttons
        btn_frame = ttk.Frame(custom_frame)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Add Color", command=self.add_gradient_color,
                  bootstyle="success-outline").pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="Remove Color", command=self.remove_gradient_color,
                  bootstyle="danger-outline").pack(side=LEFT)
        
        # Set initial tab based on color mode
        self.color_notebook.select(1)  # Select preset tab by default
        self.update_custom_gradient_preview()
        
        # Combined color preview frame (after the notebook)
        ttk.Separator(color_frame, orient='horizontal').pack(fill=X, pady=(10, 5))
        
        combined_preview_frame = ttk.Frame(color_frame)
        combined_preview_frame.pack(fill=X, pady=(5, 10))
        
        ttk.Label(combined_preview_frame, text="Selected Color Scheme Preview:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=W, pady=(0, 5))
        
        self.combined_color_preview = ttk.Frame(combined_preview_frame, height=50)
        self.combined_color_preview.pack(fill=X)
        self.combined_color_preview.pack_propagate(False)
        # Create scrollable frame for color buttons
        color_scroll = preset_scrollable
        
        # Create color scheme buttons in a grid
        self.color_var = tk.StringVar(value="Viridis")
        
        colors_grid = ttk.Frame(color_scroll)
        colors_grid.pack(fill=X, padx=10, pady=(10, 0))
        
        # Bind mouse wheel to grid
        colors_grid.bind("<MouseWheel>", _on_preset_mousewheel)
        
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
            # Bind mouse wheel to button
            btn.bind("<MouseWheel>", _on_preset_mousewheel)
            col += 1
            if col > 3:  # Changed from 1 to 3 for 4 columns
                col = 0
                row += 1
        
        # Update combined preview after all color vars are initialized
        self.update_combined_color_preview()
        
        # Mask and Shape Options
        mask_frame = self.create_section(style_frame, "Shape & Appearance")
        self.mask_frame = mask_frame  # Store reference for tutorial
        
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
        self.horizontal_label = ttk.Label(horizontal_label_frame, text=f"{int(self.prefer_horizontal.get() * 100)}%",
                                         bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.horizontal_label.pack(side=RIGHT)
        
        self.horizontal_scale = ttk.Scale(horizontal_container,
                                        from_=0.0,
                                        to=1.0,
                                        variable=self.prefer_horizontal,
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
        self.max_words_label = ttk.Label(max_words_label_frame, text=str(self.max_words.get()),
                                        bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.max_words_label.pack(side=RIGHT)
        
        self.max_words_scale = ttk.Scale(max_words_container,
                                        from_=10,
                                        to=500,
                                        variable=self.max_words,
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
        ttk.Label(scale_label_frame, text="Computation Scale:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.scale_label = ttk.Label(scale_label_frame, text=str(self.scale.get()),
                                    bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.scale_label.pack(side=RIGHT)
        
        self.scale_scale = ttk.Scale(scale_container,
                                    from_=1,
                                    to=10,
                                    variable=self.scale,
                                    command=self.update_scale,
                                    bootstyle="primary")
        self.scale_scale.pack(fill=X, pady=(5, 0))
        
        ttk.Label(scale_container, 
                 text="Higher = faster generation but coarser word placement",
                 font=('Segoe UI', 9),
                 bootstyle="secondary").pack(pady=(5, 0))
        
        # Canvas options
        canvas_frame = ttk.LabelFrame(mask_frame, text="Canvas Settings", padding=10)
        canvas_frame.pack(fill=X, pady=(0, 10))
        self.canvas_size_frame = canvas_frame  # Store reference for tutorial
        
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
        self.width_label = ttk.Label(width_label_frame, text=f"{self.canvas_width.get()} px",
                                    bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.width_label.pack(side=RIGHT)
        
        self.width_scale = ttk.Scale(width_container,
                                    from_=400,
                                    to=4000,
                                    variable=self.canvas_width,
                                    command=self.update_width,
                                    bootstyle="primary")
        self.width_scale.pack(fill=X, pady=(5, 0))
        
        # Height slider
        height_container = ttk.Frame(canvas_frame)
        height_container.pack(fill=X, pady=(0, 10))
        
        height_label_frame = ttk.Frame(height_container)
        height_label_frame.pack(fill=X)
        ttk.Label(height_label_frame, text="Height:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.height_label = ttk.Label(height_label_frame, text=f"{self.canvas_height.get()} px",
                                     bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.height_label.pack(side=RIGHT)
        
        self.height_scale = ttk.Scale(height_container,
                                     from_=300,
                                     to=4000,
                                     variable=self.canvas_height,
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
        self.contour_frame = ttk.LabelFrame(parent, text="Contour Options", padding=10)
        self.contour_frame.pack(fill=X, pady=(10, 10))
        
        # Contour width
        width_container = ttk.Frame(self.contour_frame)
        width_container.pack(fill=X, pady=(0, 10))
        
        width_label_frame = ttk.Frame(width_container)
        width_label_frame.pack(fill=X)
        contour_width_lbl = ttk.Label(width_label_frame, text="Contour Width:", font=('Segoe UI', 10))
        contour_width_lbl.pack(side=LEFT)
        contour_width_label = ttk.Label(width_label_frame, text=f"{self.contour_width.get()} pixels",
                                       bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        contour_width_label.pack(side=RIGHT)
        
        contour_width_scale = ttk.Scale(width_container,
                                       from_=0,
                                       to=10,
                                       variable=self.contour_width,
                                       command=lambda v: self.update_contour_width(v, contour_width_label),
                                       bootstyle="primary")
        contour_width_scale.pack(fill=X, pady=(5, 0))
        
        # Contour color
        color_container = ttk.Frame(self.contour_frame)
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
        
        # Store references - keep a list of all labels to update them all
        if not hasattr(self, 'contour_width_labels'):
            self.contour_width_labels = []
            self.contour_width_scales = []
            self.contour_color_previews = []
        
        self.contour_width_labels.append(contour_width_label)
        self.contour_width_scales.append(contour_width_scale)
        self.contour_color_previews.append(contour_color_preview)
        
        # Keep single reference for backward compatibility
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

        # bind a change color to font selection
        
        # Font size
        font_size_container = ttk.Frame(text_input_frame)
        font_size_container.pack(fill=X, pady=(0, 10))
        
        font_size_label_frame = ttk.Frame(font_size_container)
        font_size_label_frame.pack(fill=X)
        ttk.Label(font_size_label_frame, text="Font Size:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.font_size_label = ttk.Label(font_size_label_frame, text=str(self.text_mask_font_size.get()),
                                        bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.font_size_label.pack(side=RIGHT)
        
        self.font_size_scale = ttk.Scale(font_size_container,
                                        from_=50,
                                        to=2000,
                                        variable=self.text_mask_font_size,
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
        self.preview_frame = preview_container  # Store reference for tutorial
        
        # Create a centered frame for the preview with margins
        preview_wrapper = ttk.Frame(preview_container)
        preview_wrapper.pack(fill=BOTH, expand=TRUE, padx=10)  # Reduced horizontal margins
        
        # Removed scale indicator to clean up UI
        
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
        
        # Initial empty plot with placeholder
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Generate a word cloud to see it here', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='gray')
        
        # Add a decorative border
        rect = plt.Rectangle((0.1, 0.1), 0.8, 0.8, 
                           fill=False, 
                           edgecolor='lightgray', 
                           linewidth=2, 
                           linestyle='--',
                           transform=ax.transAxes)
        ax.add_patch(rect)
        
        # Add corner icons/text
        ax.text(0.15, 0.85, '☁', fontsize=20, color='lightgray', transform=ax.transAxes)
        ax.text(0.85, 0.85, '☁', fontsize=20, color='lightgray', transform=ax.transAxes)
        ax.text(0.15, 0.15, '☁', fontsize=20, color='lightgray', transform=ax.transAxes)
        ax.text(0.85, 0.15, '☁', fontsize=20, color='lightgray', transform=ax.transAxes)
        
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
    
    def create_message_bar(self, parent):
        """Create the message bar in the specified parent"""
        # Message bar frame
        self.message_frame = ttk.Frame(parent)
        self.message_frame.pack(side=LEFT, fill=X, expand=TRUE)
        
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
        
        # Log to console and file in debug mode
        if DEBUG and debug_logger:
            log_method = {
                "good": debug_logger.info,
                "info": debug_logger.info,
                "warning": debug_logger.warning,
                "fail": debug_logger.error
            }.get(status, debug_logger.info)
            log_method(message)
        
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
    
    def reset_forbidden_words(self):
        """Reset forbidden words to default list"""
        self.forbidden_text.delete('1.0', tk.END)
        self.forbidden_text.insert('1.0', self.default_forbidden)
        self.update_forbidden_words()
        self.show_toast("Reset to default forbidden words", "info")
    
    def on_color_select(self):
        """Handle color scheme selection"""
        color_name = self.color_var.get()
        self.selected_colormap = self.color_schemes[color_name]
        # Update combined preview if in preset mode
        if self.color_mode.get() == "preset":
            self.update_combined_color_preview()
        
    def on_color_mode_change(self):
        """Handle color mode radio button change"""
        mode = self.color_mode.get()
        if mode == "single":
            self.color_notebook.select(0)
        elif mode == "preset":
            self.color_notebook.select(1)
        elif mode == "custom":
            self.color_notebook.select(2)
            self.update_custom_gradient_preview()
        
        # Update the combined preview
        self.update_combined_color_preview()
    
    def choose_custom_color(self, index):
        """Choose a color for custom gradient"""
        current_color = self.custom_gradient_colors[index]
        dialog = ColorChooserDialog(title=f"Choose Color {index+1}", 
                                   initialcolor=current_color)
        dialog.show()
        
        if dialog.result:
            color = dialog.result
            hex_color = color.hex
            self.custom_gradient_colors[index] = hex_color
            self.update_custom_gradient_preview()
    
    def add_gradient_color(self):
        """Add a new color to the gradient"""
        if len(self.custom_gradient_colors) < 10:  # Limit to 10 colors
            self.custom_gradient_colors.append("#FFFFFF")
            self.recreate_custom_gradient_ui()
    
    def remove_gradient_color(self):
        """Remove the last color from gradient"""
        if len(self.custom_gradient_colors) > 2:  # Minimum 2 colors
            self.custom_gradient_colors.pop()
            self.recreate_custom_gradient_ui()
    
    def recreate_custom_gradient_ui(self):
        """Recreate the custom gradient UI after adding/removing colors"""
        # Find the custom frame
        custom_tab = self.color_notebook.winfo_children()[2]
        custom_frame = custom_tab.winfo_children()[0]
        
        # Clear existing color frames
        for frame in self.custom_color_frames:
            frame.destroy()
        self.custom_color_frames.clear()
        self.custom_color_previews.clear()
        
        # Recreate color rows
        for i in range(len(self.custom_gradient_colors)):
            color_row = ttk.Frame(custom_frame)
            color_row.pack(fill=X, pady=5, before=custom_frame.winfo_children()[1])
            
            ttk.Label(color_row, text=f"Color {i+1}:", width=10).pack(side=LEFT)
            
            preview = ttk.Frame(color_row, width=30, height=30)
            preview.pack(side=LEFT, padx=(5, 10))
            self.custom_color_previews.append(preview)
            
            btn = ttk.Button(color_row, text="Choose", 
                           command=lambda idx=i: self.choose_custom_color(idx),
                           bootstyle="secondary-outline")
            btn.pack(side=LEFT)
            
            self.custom_color_frames.append(color_row)
        
        self.update_custom_gradient_preview()
    
    def update_custom_gradient_preview(self):
        """Update the custom gradient preview"""
        # Update individual color previews
        for i, (preview, color) in enumerate(zip(self.custom_color_previews, self.custom_gradient_colors)):
            style = ttk.Style()
            style_name = f"CustomColor{i}.TFrame"
            style.configure(style_name, background=color)
            preview.configure(style=style_name)
        
        # Update combined preview if in custom mode
        if self.color_mode.get() == "custom":
            self.update_combined_color_preview()
            
    def choose_single_color(self):
        """Open color picker for single color"""
        dialog = ColorChooserDialog(title="Choose Single Color", 
                                   initialcolor=self.single_color.get())
        dialog.show()
        
        if dialog.result:
            color = dialog.result
            hex_color = color.hex
            self.single_color.set(hex_color)
            
            # Update preview
            style = ttk.Style()
            style_name = "SingleColorPreview.TFrame"
            style.configure(style_name, background=hex_color)
            self.single_color_preview.configure(style=style_name)
            
            # Update combined preview if in single color mode
            if self.color_mode.get() == "single":
                self.update_combined_color_preview()
    
    
    def update_combined_color_preview(self):
        """Update the combined color preview based on selected mode"""
        if not hasattr(self, 'combined_color_preview'):
            return
            
        # Clear existing preview
        for widget in self.combined_color_preview.winfo_children():
            widget.destroy()
            
        mode = self.color_mode.get()
        
        if mode == "single":
            # Show single color
            preview_canvas = tk.Canvas(self.combined_color_preview, 
                                     height=50, 
                                     highlightthickness=0)
            preview_canvas.pack(fill=X)
            preview_canvas.configure(bg=self.single_color.get())
            
        elif mode == "preset":
            # Show selected preset gradient
            color_name = self.color_var.get()
            cmap_name = self.color_schemes.get(color_name)
            
            if cmap_name:
                preview_canvas = tk.Canvas(self.combined_color_preview, 
                                         height=50, 
                                         highlightthickness=0)
                preview_canvas.pack(fill=X)
                
                # Draw gradient when canvas is configured
                def draw_gradient(event=None):
                    width = preview_canvas.winfo_width()
                    if width > 1:
                        try:
                            # Get the actual colormap
                            cmap = matplotlib.colormaps[cmap_name]
                            for i in range(width):
                                color = cmap(i / width)
                                rgb = tuple(int(c * 255) for c in color[:3])
                                hex_color = '#%02x%02x%02x' % rgb
                                preview_canvas.create_line(i, 0, i, 50, fill=hex_color)
                        except:
                            pass
                
                preview_canvas.bind('<Configure>', draw_gradient)
                
        elif mode == "custom":
            # Show custom gradient
            if len(self.custom_gradient_colors) >= 2:
                preview_canvas = tk.Canvas(self.combined_color_preview, 
                                         height=50, 
                                         highlightthickness=0)
                preview_canvas.pack(fill=X)
                
                # Draw custom gradient when canvas is configured
                def draw_custom_gradient(event=None):
                    width = preview_canvas.winfo_width()
                    if width > 1:
                        try:
                            # Create custom colormap
                            custom_cmap = LinearSegmentedColormap.from_list(
                                'custom_gradient', 
                                self.custom_gradient_colors
                            )
                            
                            for i in range(width):
                                color = custom_cmap(i / width)
                                rgb = tuple(int(c * 255) for c in color[:3])
                                hex_color = '#%02x%02x%02x' % rgb
                                preview_canvas.create_line(i, 0, i, 50, fill=hex_color)
                        except:
                            pass
                
                preview_canvas.bind('<Configure>', draw_custom_gradient)
    
    def select_mask(self):
        """Select mask image file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                self.mask_image = np.array(Image.open(file_path))
                self.mask_path.set(os.path.basename(file_path))
                self.image_mask_file_path = file_path  # Store full path
                
                # Update the image mask label
                self.image_mask_label.config(text=os.path.basename(file_path))
                
                # Update mask preview with scaling
                img = Image.open(file_path)
                
                # Scale preview relative to canvas dimensions (25% of canvas size)
                canvas_w = self.canvas_width.get()
                canvas_h = self.canvas_height.get()
                preview_w = int(canvas_w * 0.25)
                preview_h = int(canvas_h * 0.25)
                
                # Maintain aspect ratio
                img_w, img_h = img.size
                aspect = img_w / img_h
                
                if aspect > preview_w / preview_h:
                    # Image is wider
                    new_w = preview_w
                    new_h = int(preview_w / aspect)
                else:
                    # Image is taller
                    new_h = preview_h
                    new_w = int(preview_h * aspect)
                
                # Ensure minimum size
                new_w = max(new_w, 100)
                new_h = max(new_h, 100)
                
                img.thumbnail((new_w, new_h), Image.Resampling.LANCZOS)
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
        self.image_mask_file_path = None
        
        # Clear appropriate preview label and update UI based on mask type
        if self.mask_type.get() == "image":
            if hasattr(self, 'image_mask_preview_label'):
                self.image_mask_preview_label.config(image="", text="No mask selected")
            if hasattr(self, 'image_mask_label'):
                self.image_mask_label.config(text="No image selected")
        elif self.mask_type.get() == "text":
            if hasattr(self, 'text_mask_preview_label'):
                self.text_mask_preview_label.config(image="", text="No mask selected")
            if hasattr(self, 'text_mask_input'):
                debug_print("Clearing text_mask_input in clear_mask()")
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

            # change the font selection color
            self.canvas.itemconfig(self.text_mask_preview_label, fill='white')

    def update_mask_preview(self):
        """Update the mask preview display"""
        if self.mask_image is not None:
            # Convert numpy array to PIL Image for preview
            if len(self.mask_image.shape) == 3:
                preview_img = Image.fromarray(self.mask_image.astype('uint8'), 'RGB')
            else:
                preview_img = Image.fromarray(self.mask_image.astype('uint8'), 'L')
            
            # Scale preview relative to canvas dimensions (25% of canvas size)
            canvas_w = self.canvas_width.get()
            canvas_h = self.canvas_height.get()
            preview_w = int(canvas_w * 0.25)
            preview_h = int(canvas_h * 0.25)
            
            # Maintain aspect ratio
            img_w, img_h = preview_img.size
            aspect = img_w / img_h
            
            if aspect > preview_w / preview_h:
                # Image is wider
                new_w = preview_w
                new_h = int(preview_w / aspect)
            else:
                # Image is taller
                new_h = preview_h
                new_w = int(preview_h * aspect)
            
            # Ensure minimum size
            new_w = max(new_w, 100)
            new_h = max(new_h, 100)
            
            # Thumbnail for preview
            preview_img.thumbnail((new_w, new_h), Image.Resampling.LANCZOS)
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
        else:
            # Update all contour width labels
            if hasattr(self, 'contour_width_labels'):
                for lbl in self.contour_width_labels:
                    lbl.config(text=f"{val} pixels")
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
            
            # Scale calculation removed - no longer showing indicator
            
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
        if hasattr(self, 'contour_frame'):
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
            debug_print("Starting word cloud generation thread")
            
            # Filter words
            debug_print(f"Text content type: {type(self.text_content)}, content length: {len(self.text_content) if self.text_content else 0}")
            filtered_text = self.filter_words(self.text_content)
            
            if not filtered_text:
                self.root.after(0, lambda: self.show_toast("No words found after filtering", "warning"))
                return
            
            debug_print(f"Filtered text length: {len(filtered_text)}")
            
            # Create word cloud
            debug_print("Building word cloud parameters...")
            wc_params = {
                'width': self.canvas_width.get(),
                'height': self.canvas_height.get(),
                'max_words': int(self.max_words.get()),
                'scale': self.scale.get(),
                'relative_scaling': 0.5,
                'min_font_size': 10,
                'prefer_horizontal': self.prefer_horizontal.get()
            }
            debug_print(f"Word cloud params: {wc_params}")
            
            # Set color mode
            debug_print(f"Color mode: {self.color_mode.get()}")
            if self.color_mode.get() == "single":
                # Use single color function
                debug_print(f"Single color type: {type(self.single_color)}")
                color_value = self.single_color.get()
                debug_print(f"Single color value: {color_value}")
                wc_params['color_func'] = lambda *args, **kwargs: color_value
            elif self.color_mode.get() == "custom":
                # Use custom gradient
                debug_print("Using custom gradient colors")
                custom_cmap = LinearSegmentedColormap.from_list('custom', self.custom_gradient_colors)
                wc_params['colormap'] = custom_cmap
            else:
                # Use preset colormap
                debug_print(f"Using preset colormap: {self.selected_colormap}")
                wc_params['colormap'] = self.selected_colormap
            
            # Set background and mode
            debug_print(f"RGBA mode type: {type(self.rgba_mode)}, value: {self.rgba_mode if hasattr(self, 'rgba_mode') else 'No rgba_mode attr'}")
            if hasattr(self, 'rgba_mode') and callable(getattr(self.rgba_mode, 'get', None)):
                if self.rgba_mode.get():
                    wc_params['mode'] = 'RGBA'
                    wc_params['background_color'] = None
                else:
                    wc_params['mode'] = 'RGB'
                    wc_params['background_color'] = self.bg_color.get()
            else:
                # Default to RGB mode if rgba_mode is not properly initialized
                debug_print("Warning: rgba_mode not properly initialized, defaulting to RGB")
                wc_params['mode'] = 'RGB'
                wc_params['background_color'] = self.bg_color.get() if hasattr(self, 'bg_color') else '#FFFFFF'
            
            if self.mask_image is not None:
                debug_print("Using mask image")
                wc_params['mask'] = self.mask_image
                if hasattr(self, 'contour_width') and callable(getattr(self.contour_width, 'get', None)):
                    contour_width_value = self.contour_width.get()
                    debug_print(f"Contour width value: {contour_width_value}")
                    if contour_width_value > 0:
                        wc_params['contour_width'] = contour_width_value
                        wc_params['contour_color'] = self.contour_color.get()
                        debug_print(f"Applied contour: width={contour_width_value}, color={self.contour_color.get()}")
            
            debug_print("Creating WordCloud object...")
            self.wordcloud = WordCloud(**wc_params).generate(filtered_text)
            debug_print("WordCloud generated successfully")
            
            # Update UI in main thread
            self.root.after(0, self._update_preview)
            
        except Exception as e:
            error_msg = str(e)
            if DEBUG and debug_logger:
                debug_logger.error(f"Error generating word cloud: {error_msg}")
                debug_logger.error(f"Exception type: {type(e).__name__}")
                debug_logger.error("Full traceback:", exc_info=True)
            self.root.after(0, lambda: self.show_toast(f"Error generating word cloud: {error_msg}", "danger"))
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
        
        # Size indicator removed for cleaner UI
        
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
        # Log to console and file in debug mode
        if DEBUG and debug_logger:
            log_method = {
                "success": debug_logger.info,
                "info": debug_logger.info, 
                "warning": debug_logger.warning,
                "danger": debug_logger.error
            }.get(style, debug_logger.info)
            log_method(f"[TOAST] {message}")
            
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
    
    def apply_config(self, config, show_message=True):
        """Apply configuration from dictionary"""
        debug_print(f"=== APPLY CONFIG START ===")
        debug_print(f"Applying config with {len(config)} settings")
        debug_print(f"Config keys: {list(config.keys())}")
        debug_print(f"show_message: {show_message}")
        try:
            # Apply basic settings
            if 'min_length' in config:
                debug_print(f"Setting min_length to: {config['min_length']}")
                if hasattr(self, 'min_word_length'):
                    self.min_word_length.set(config['min_length'])
                    # Update UI after delay
                    min_value = config['min_length']
                    def update_min_ui():
                        if hasattr(self, 'min_length_label'):
                            self.min_length_label.config(text=f"{min_value} characters")
                            debug_print(f"Updated min_length_label to: {min_value}")
                    self.root.after(100, update_min_ui)
            if 'max_length' in config:
                debug_print(f"Setting max_length to: {config['max_length']}")
                if hasattr(self, 'max_word_length'):
                    self.max_word_length.set(config['max_length'])
                    # Update UI after delay
                    max_value = config['max_length']
                    def update_max_ui():
                        if hasattr(self, 'max_length_label'):
                            self.max_length_label.config(text=f"{max_value} characters")
                            debug_print(f"Updated max_length_label to: {max_value}")
                    self.root.after(100, update_max_ui)
            if 'forbidden_words' in config:
                # Filter out empty strings
                forbidden_list = [word for word in config['forbidden_words'] if word.strip()]
                debug_print(f"Setting forbidden_words, count: {len(forbidden_list)}")
                self.forbidden_text.delete(1.0, tk.END)
                if forbidden_list:  # Only insert if there are words
                    self.forbidden_text.insert(1.0, '\n'.join(forbidden_list))
                self.update_forbidden_words()
            
            # Apply color settings
            if 'color_mode' in config:
                debug_print(f"Setting color_mode to: {config['color_mode']}")
                self.color_mode.set(config['color_mode'])
                self.on_color_mode_change()
            if 'color_scheme' in config:
                debug_print(f"Setting color_scheme to: {config['color_scheme']}")
                self.color_var.set(config['color_scheme'])
                self.on_color_select()
            if 'single_color' in config:
                debug_print(f"Setting single_color to: {config['single_color']}")
                self.single_color.set(config['single_color'])
                # Update single color preview
                style = ttk.Style()
                style.configure("SingleColorPreview.TFrame", background=config['single_color'])
                if hasattr(self, 'single_color_preview'):
                    self.single_color_preview.configure(style="SingleColorPreview.TFrame")
            if 'custom_colors' in config:
                debug_print(f"Setting custom_colors: {config['custom_colors']}")
                self.custom_gradient_colors = config['custom_colors']
                self.update_custom_gradient_preview()
            # Note: selected_colormap is derived from color_scheme, not loaded separately
            
            # Apply other settings
            if 'prefer_horizontal' in config:
                debug_print(f"Setting prefer_horizontal to: {config['prefer_horizontal']}")
                if hasattr(self, 'prefer_horizontal'):
                    self.prefer_horizontal.set(config['prefer_horizontal'])
                    # Update UI elements after a delay
                    horizontal_value = config['prefer_horizontal']
                    def update_horizontal_ui():
                        if hasattr(self, 'horizontal_scale'):
                            self.horizontal_scale.set(horizontal_value)
                            debug_print(f"Updated horizontal_scale to: {horizontal_value}")
                        if hasattr(self, 'horizontal_label'):
                            self.horizontal_label.config(text=f"{int(horizontal_value * 100)}%")
                            debug_print(f"Updated horizontal_label to: {int(horizontal_value * 100)}%")
                    self.root.after(100, update_horizontal_ui)
            if 'canvas_width' in config:
                debug_print(f"Setting canvas_width to: {config['canvas_width']}")
                if hasattr(self, 'canvas_width'):
                    self.canvas_width.set(config['canvas_width'])
                    # Update scale and label after UI is ready
                    width_value = config['canvas_width']
                    def update_width_ui():
                        if hasattr(self, 'width_scale'):
                            self.width_scale.set(width_value)
                        if hasattr(self, 'width_label'):
                            self.width_label.config(text=f"{width_value} px")
                        debug_print(f"Updated width UI to: {width_value}")
                    self.root.after(100, update_width_ui)
            if 'canvas_height' in config:
                debug_print(f"Setting canvas_height to: {config['canvas_height']}")
                if hasattr(self, 'canvas_height'):
                    self.canvas_height.set(config['canvas_height'])
                    # Update scale and label after UI is ready
                    height_value = config['canvas_height']
                    def update_height_ui():
                        if hasattr(self, 'height_scale'):
                            self.height_scale.set(height_value)
                        if hasattr(self, 'height_label'):
                            self.height_label.config(text=f"{height_value} px")
                        debug_print(f"Updated height UI to: {height_value}")
                    self.root.after(100, update_height_ui)
            if 'background_color' in config:
                debug_print(f"Setting background_color to: {config['background_color']}")
                self.bg_color.set(config['background_color'])
                # Update preview after UI is ready
                bg_color_value = config['background_color']
                def update_bg_color_ui():
                    if hasattr(self, 'bg_color_preview'):
                        style = ttk.Style()
                        style_name = f"BgPreview.TFrame"
                        style.configure(style_name, background=bg_color_value)
                        self.bg_color_preview.configure(style=style_name)
                        debug_print(f"Updated bg_color_preview to: {bg_color_value}")
                self.root.after(100, update_bg_color_ui)
            if 'rgba_mode' in config and hasattr(self, 'rgba_mode'):
                debug_print(f"Setting rgba_mode to: {config['rgba_mode']}")
                self.rgba_mode.set(config['rgba_mode'])
            if 'color_mode_setting' in config:
                self.color_mode_var.set(config['color_mode_setting'])
                # TODO: on_color_mode_change_canvas() method needs to be implemented
            if 'max_words' in config:
                debug_print(f"Setting max_words to: {config['max_words']}")
                if hasattr(self, 'max_words'):
                    self.max_words.set(config['max_words'])
                    # Update UI elements after a delay
                    max_words_value = config['max_words']
                    def update_max_words_ui():
                        if hasattr(self, 'max_words_scale'):
                            self.max_words_scale.set(max_words_value)
                            debug_print(f"Updated max_words_scale to: {max_words_value}")
                        if hasattr(self, 'max_words_label'):
                            self.max_words_label.config(text=str(max_words_value))
                            debug_print(f"Updated max_words_label to: {max_words_value}")
                    self.root.after(100, update_max_words_ui)
            if 'scale' in config:
                debug_print(f"Setting scale to: {config['scale']}")
                if hasattr(self, 'scale'):
                    self.scale.set(config['scale'])
                    # Update UI elements after a delay
                    scale_value = config['scale']
                    def update_scale_ui():
                        if hasattr(self, 'scale_scale'):
                            self.scale_scale.set(scale_value)
                            debug_print(f"Updated scale_scale to: {scale_value}")
                        if hasattr(self, 'scale_label'):
                            self.scale_label.config(text=str(scale_value))
                            debug_print(f"Updated scale_label to: {scale_value}")
                    self.root.after(100, update_scale_ui)
            
            # Apply theme
            if 'theme' in config and config['theme'] in self.themes:
                self.current_theme.set(config['theme'])
                self.root.style.theme_use(config['theme'].lower().replace(" ", ""))
            
            # Apply mask settings
            if 'mask_type' in config:
                debug_print(f"Setting mask_type to: {config['mask_type']}")
                mask_types = {'no_mask': 0, 'image_mask': 1, 'text_mask': 2}
                if config['mask_type'] in mask_types:
                    self.mask_notebook.select(mask_types[config['mask_type']])
            
            # Apply contour settings
            if 'contour_enabled' in config and hasattr(self, 'contour_var'):
                self.contour_var.set(config['contour_enabled'])
            if 'contour_width' in config:
                debug_print(f"Setting contour_width to: {config['contour_width']}")
                if hasattr(self, 'contour_width'):
                    self.contour_width.set(config['contour_width'])
                    # Schedule label update after UI is ready
                    contour_value = config['contour_width']
                    def update_contour_labels():
                        # Update all contour width labels
                        if hasattr(self, 'contour_width_labels'):
                            for label in self.contour_width_labels:
                                label.config(text=f"{contour_value} pixels")
                            debug_print(f"Updated all contour_width_labels to: {contour_value} pixels")
                        elif hasattr(self, 'contour_width_label'):
                            self.contour_width_label.config(text=f"{contour_value} pixels")
                            debug_print(f"Updated contour_width_label to: {contour_value} pixels")
                    self.root.after(100, update_contour_labels)
            if 'contour_color' in config:
                debug_print(f"Setting contour_color to: {config['contour_color']}")
                if hasattr(self, 'contour_color'):
                    self.contour_color.set(config['contour_color'])
                    # TODO: update_contour_color_preview() method needs to be implemented
            
            # Apply text mask settings
            if hasattr(self, 'text_mask_input'):
                if 'text_mask_text' in config:
                    text_value = config['text_mask_text']
                    debug_print(f"Loading text_mask_text: '{text_value}'")
                    if text_value:  # Only set if not empty
                        self.text_mask_input.set(text_value)
                        debug_print(f"Set text_mask_input to: '{self.text_mask_input.get()}'")
                        # Update text mask if text is present and mask type is text
                        if config.get('mask_type') == 'text_mask':
                            debug_print("Scheduling text mask update")
                            # Schedule text mask update after UI is ready
                            self.root.after(200, self.update_text_mask)
                if 'text_mask_font' in config:
                    debug_print(f"Setting text_mask_font to: {config['text_mask_font']}")
                    if hasattr(self, 'text_mask_font'):
                        self.text_mask_font.set(config['text_mask_font'])
                if 'text_mask_size' in config:
                    debug_print(f"Setting text_mask_font_size to: {config['text_mask_size']}")
                    if hasattr(self, 'text_mask_font_size'):
                        self.text_mask_font_size.set(config['text_mask_size'])
                        # Update UI elements after a delay
                        font_size_value = config['text_mask_size']
                        def update_font_size_ui():
                            if hasattr(self, 'font_size_scale'):
                                self.font_size_scale.set(font_size_value)
                                debug_print(f"Updated font_size_scale to: {font_size_value}")
                            if hasattr(self, 'font_size_label'):
                                self.font_size_label.config(text=str(font_size_value))
                                debug_print(f"Updated font_size_label to: {font_size_value}")
                        self.root.after(100, update_font_size_ui)
                if 'text_mask_bold' in config:
                    debug_print(f"Setting text_mask_bold to: {config['text_mask_bold']}")
                    if hasattr(self, 'text_mask_bold'):
                        self.text_mask_bold.set(config['text_mask_bold'])
                if 'text_mask_italic' in config:
                    debug_print(f"Setting text_mask_italic to: {config['text_mask_italic']}")
                    if hasattr(self, 'text_mask_italic'):
                        self.text_mask_italic.set(config['text_mask_italic'])
                # Note: text mask uses canvas width/height, not separate dimensions
            
            # Note: mask_path is derived from mask_type and specific mask data, not loaded separately
                
            # Load image mask from file path if available and mask_type is image
            if 'image_mask_file_path' in config and config.get('mask_type') == 'image_mask' and os.path.exists(config['image_mask_file_path']):
                try:
                    file_path = config['image_mask_file_path']
                    self.mask_image = np.array(Image.open(file_path))
                    self.image_mask_file_path = file_path
                    
                    # Update UI elements after a short delay to ensure UI is ready
                    def update_mask_ui():
                        if hasattr(self, 'image_mask_label'):
                            self.image_mask_label.config(text=os.path.basename(file_path))
                        
                        # Update mask preview with scaling
                        img = Image.open(file_path)
                        
                        # Scale preview relative to canvas dimensions (25% of canvas size)
                        canvas_w = self.canvas_width.get()
                        canvas_h = self.canvas_height.get()
                        preview_w = int(canvas_w * 0.25)
                        preview_h = int(canvas_h * 0.25)
                        
                        # Maintain aspect ratio
                        img_w, img_h = img.size
                        aspect = img_w / img_h
                        
                        if aspect > preview_w / preview_h:
                            # Image is wider
                            new_w = preview_w
                            new_h = int(preview_w / aspect)
                        else:
                            # Image is taller
                            new_h = preview_h
                            new_w = int(preview_h * aspect)
                        
                        # Ensure minimum size
                        new_w = max(new_w, 100)
                        new_h = max(new_h, 100)
                        
                        img.thumbnail((new_w, new_h), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        if hasattr(self, 'image_mask_preview_label'):
                            self.image_mask_preview_label.config(image=photo, text="")
                            self.image_mask_preview_label.image = photo  # Keep a reference
                        
                        # Enable contour options
                        self.update_contour_state(True)
                    
                    # Schedule UI update
                    self.root.after(100, update_mask_ui)
                    
                except Exception as e:
                    debug_print(f"Failed to load image mask: {e}")
            
            # Apply input settings
            if 'working_directory' in config and hasattr(self, 'working_folder'):
                self.working_folder.set(config['working_directory'])
                if os.path.exists(config['working_directory']):
                    self.populate_file_list()
            
            if show_message:
                self.show_message("Configuration loaded successfully", "good")
            
            debug_print("=== APPLY CONFIG END ===")
            return True
            
        except Exception as e:
            if DEBUG and debug_logger:
                debug_logger.error(f"Failed to apply config: {str(e)}")
                debug_logger.error("Full traceback:", exc_info=True)
            if show_message:
                self.show_message(f"Failed to apply config: {str(e)}", "fail")
            return False
    
    def import_config(self):
        """Import configuration from JSON file"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        configs_dir = os.path.join(script_dir, 'configs')
        os.makedirs(configs_dir, exist_ok=True)
        
        file_path = filedialog.askopenfilename(
            title="Import Configuration",
            initialdir=configs_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                debug_print(f"=== CONFIG LOAD START ===")
                debug_print(f"Loading config from: {file_path}")
                debug_print(f"Total settings in config: {len(config)}")
                debug_print(f"Config keys: {list(config.keys())}")
                if 'text_mask_text' in config:
                    debug_print(f"text_mask_text value: '{config['text_mask_text']}'")
                if 'mask_type' in config:
                    debug_print(f"mask_type value: '{config['mask_type']}'")
                self.apply_config(config)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON format: {str(e)}"
                if DEBUG and debug_logger:
                    debug_logger.error(error_msg)
                    debug_logger.error(f"File: {file_path}")
                self.show_message(error_msg, "fail")
            except Exception as e:
                if DEBUG and debug_logger:
                    debug_logger.error(f"Failed to import config: {str(e)}")
                    debug_logger.error("Full traceback:", exc_info=True)
                self.show_message(f"Failed to import config: {str(e)}", "fail")
    
    def auto_load_config(self):
        """Auto-load configuration from configs folder if it exists"""
        # Create configs folder if it doesn't exist
        script_dir = os.path.dirname(os.path.abspath(__file__))
        configs_dir = os.path.join(script_dir, 'configs')
        os.makedirs(configs_dir, exist_ok=True)
        
        config_file = os.path.join(configs_dir, 'wordcloud_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    content = f.read().strip()
                    if content:  # Only parse if file has content
                        config = json.loads(content)
                        debug_print(f"Loaded config: {config}")
                        self.apply_config(config, show_message=False)
                        debug_print(f"Successfully auto-loaded configuration from configs/wordcloud_config.json")
                    else:
                        print("Config file is empty, skipping auto-load")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in config file: {e}")
                print("Consider deleting configs/wordcloud_config.json or fixing the JSON syntax")
            except Exception as e:
                print(f"Failed to auto-load config: {e}")
    
    def get_current_config(self):
        """Get current configuration as dictionary"""
        debug_print("Getting current configuration...")
        config = {}
        
        # Basic settings
        if hasattr(self, 'min_length_var'):
            config['min_length'] = self.min_length_var.get()
        elif hasattr(self, 'min_length_scale'):
            config['min_length'] = int(self.min_length_scale.get())
        else:
            debug_print("Warning: min_length not found")
            
        if hasattr(self, 'max_length_var'):
            config['max_length'] = self.max_length_var.get()
        elif hasattr(self, 'max_length_scale'):
            config['max_length'] = int(self.max_length_scale.get())
        else:
            debug_print("Warning: max_length not found")
        if hasattr(self, 'forbidden_text'):
            config['forbidden_words'] = self.forbidden_text.get(1.0, tk.END).strip().split('\n')
        
        # Color settings
        if hasattr(self, 'color_mode'):
            config['color_mode'] = self.color_mode.get()
        if hasattr(self, 'color_var'):
            config['color_scheme'] = self.color_var.get()
        # Note: selected_colormap is derived from color_scheme, not saved separately
        if hasattr(self, 'single_color'):
            config['single_color'] = self.single_color.get()
        if hasattr(self, 'custom_gradient_colors'):
            config['custom_colors'] = self.custom_gradient_colors
        
        # Canvas settings
        if hasattr(self, 'horizontal_scale'):
            config['prefer_horizontal'] = self.horizontal_scale.get()
        elif hasattr(self, 'prefer_horizontal'):
            config['prefer_horizontal'] = self.prefer_horizontal.get()
            
        if hasattr(self, 'width_var'):
            config['canvas_width'] = self.width_var.get()
        elif hasattr(self, 'canvas_width'):
            config['canvas_width'] = self.canvas_width.get()
        else:
            debug_print("Warning: canvas_width not found")
            
        if hasattr(self, 'height_var'):
            config['canvas_height'] = self.height_var.get()
        elif hasattr(self, 'canvas_height'):
            config['canvas_height'] = self.canvas_height.get()
        else:
            debug_print("Warning: canvas_height not found")
        if hasattr(self, 'bg_color'):
            config['background_color'] = self.bg_color.get()
        if hasattr(self, 'rgba_mode'):
            config['rgba_mode'] = self.rgba_mode.get()
        if hasattr(self, 'color_mode_var'):
            config['color_mode_setting'] = self.color_mode_var.get()
        
        # Other settings
        if hasattr(self, 'max_words_var'):
            config['max_words'] = self.max_words_var.get()
        elif hasattr(self, 'max_words'):
            config['max_words'] = self.max_words.get()
            
        if hasattr(self, 'scale_var'):
            config['scale'] = self.scale_var.get()
        elif hasattr(self, 'scale'):
            config['scale'] = self.scale.get()
        if hasattr(self, 'current_theme'):
            config['theme'] = self.current_theme.get()
        
        # Mask settings
        if hasattr(self, 'mask_notebook'):
            config['mask_type'] = self.get_current_mask_type()
        
        # Image mask settings
        # Note: mask_path is derived from mask_type and specific mask data, not saved separately
        if hasattr(self, 'image_mask_file_path') and self.image_mask_file_path:
            config['image_mask_file_path'] = self.image_mask_file_path
        if hasattr(self, 'contour_var'):
            config['contour_enabled'] = self.contour_var.get()
        if hasattr(self, 'contour_width'):
            config['contour_width'] = self.contour_width.get()
            debug_print(f"Saving contour_width: {self.contour_width.get()}")
        if hasattr(self, 'contour_color'):
            config['contour_color'] = self.contour_color.get() if hasattr(self.contour_color, 'get') else self.contour_color
        
        # Text mask settings
        if hasattr(self, 'text_mask_input'):
            text_value = self.text_mask_input.get()
            config['text_mask_text'] = text_value
            debug_print(f"Saving text_mask_text: '{text_value}'")
        if hasattr(self, 'text_mask_font'):
            font_value = self.text_mask_font.get()
            config['text_mask_font'] = font_value
            debug_print(f"Saving text_mask_font: '{font_value}'")
        if hasattr(self, 'text_mask_font_size'):
            config['text_mask_size'] = self.text_mask_font_size.get()
            debug_print(f"Saving text_mask_size: {self.text_mask_font_size.get()}")
        if hasattr(self, 'text_mask_bold'):
            config['text_mask_bold'] = self.text_mask_bold.get()
            debug_print(f"Saving text_mask_bold: {self.text_mask_bold.get()}")
        if hasattr(self, 'text_mask_italic'):
            config['text_mask_italic'] = self.text_mask_italic.get()
            debug_print(f"Saving text_mask_italic: {self.text_mask_italic.get()}")
        
        # Input settings
        if hasattr(self, 'working_folder'):
            config['working_directory'] = self.working_folder.get()
        
        # Default forbidden words
        if hasattr(self, 'default_forbidden'):
            config['default_forbidden'] = self.default_forbidden
        
        debug_print(f"Final config with {len(config)} settings")
        return config
    
    def get_current_mask_type(self):
        """Get the currently selected mask type"""
        try:
            current_tab = self.mask_notebook.index(self.mask_notebook.select())
            return ['no_mask', 'image_mask', 'text_mask'][current_tab]
        except:
            return 'no_mask'
    
    def save_config_to_file(self, file_path):
        """Save configuration to specified file"""
        try:
            config = self.get_current_config()
            debug_print(f"Config to save: {config}")
            debug_print(f"Number of settings: {len(config)}")
            
            # Ensure all values are JSON serializable
            serializable_config = {}
            for key, value in config.items():
                if hasattr(value, 'get'):  # If it's a Tkinter variable
                    serializable_config[key] = value.get()
                else:
                    serializable_config[key] = value
            
            with open(file_path, 'w') as f:
                json.dump(serializable_config, f, indent=2)
            return True
        except Exception as e:
            if DEBUG and debug_logger:
                debug_logger.error(f"Error saving config: {e}")
                debug_logger.error("Full traceback:", exc_info=True)
            else:
                print(f"Error saving config: {e}")
            return False
    
    def export_config(self):
        """Export current configuration to JSON file"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        configs_dir = os.path.join(script_dir, 'configs')
        os.makedirs(configs_dir, exist_ok=True)
        
        file_path = filedialog.asksaveasfilename(
            title="Export Configuration",
            initialdir=configs_dir,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.save_config_to_file(file_path):
                self.show_message("Configuration exported successfully", "good")
            else:
                self.show_message("Failed to export configuration", "fail")
    
    def auto_save_config(self):
        """Auto-save configuration to configs folder"""
        # Only save if UI has been created and is ready
        if hasattr(self, 'ui_ready') and self.ui_ready:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            configs_dir = os.path.join(script_dir, 'configs')
            os.makedirs(configs_dir, exist_ok=True)
            
            config_file = os.path.join(configs_dir, 'wordcloud_config.json')
            self.save_config_to_file(config_file)
    
    def save_config_locally(self):
        """Save configuration to configs folder with user feedback"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        configs_dir = os.path.join(script_dir, 'configs')
        os.makedirs(configs_dir, exist_ok=True)
        
        config_file = os.path.join(configs_dir, 'wordcloud_config.json')
        if self.save_config_to_file(config_file):
            self.show_message(f"Configuration saved to configs/{os.path.basename(config_file)}", "good")
        else:
            self.show_message("Failed to save configuration locally", "fail")
    
    def on_closing(self):
        """Handle application closing - prompt to save config and exit"""
        from tkinter import messagebox
        
        # Create a custom dialog with three options
        result = messagebox.askyesnocancel(
            "Save Configuration?", 
            "Do you want to save your current configuration before exiting?\n\n" +
            "Yes - Save and Exit\n" +
            "No - Exit without saving\n" +
            "Cancel - Don't exit"
        )
        
        if result is True:  # Yes - Save and exit
            try:
                self.auto_save_config()
                debug_print("Configuration saved before exit")
            except Exception as e:
                print(f"Could not save config on exit: {e}")
                messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
                return  # Don't exit if save failed
            self.root.quit()
        elif result is False:  # No - Exit without saving
            debug_print("Exiting without saving configuration")
            self.root.quit()
        # else: result is None (Cancel) - do nothing, stay in app
    
    def reset_app(self):
        """Reset application to default settings"""
        from tkinter import messagebox
        
        # Confirm reset
        if messagebox.askyesno("Reset Application", "Are you sure you want to reset all settings to defaults?"):
            try:
                # Reset filter settings
                if hasattr(self, 'min_length_scale'):
                    self.min_length_scale.set(3)
                    self.update_min_label(3)
                if hasattr(self, 'max_length_scale'):
                    self.max_length_scale.set(30)
                    self.update_max_label(30)
                self.forbidden_text.delete(1.0, tk.END)
                self.forbidden_text.insert(1.0, self.default_forbidden)
                self.update_forbidden_words()
                
                # Reset color settings
                self.color_mode.set("preset")
                self.color_var.set("Viridis")
                self.single_color.set("#0078D4")
                self.custom_gradient_colors = ["#FF0000", "#00FF00", "#0000FF"]
                self.update_custom_gradient_preview()
                self.on_color_mode_change()  # Update UI to reflect preset mode
                
                # Reset canvas settings
                if hasattr(self, 'horizontal_scale'):
                    self.horizontal_scale.set(0.9)
                elif hasattr(self, 'prefer_horizontal'):
                    self.prefer_horizontal.set(0.9)
                    
                if hasattr(self, 'canvas_width'):
                    self.canvas_width.set(800)
                if hasattr(self, 'canvas_height'):
                    self.canvas_height.set(600)
                if hasattr(self, 'bg_color'):
                    self.bg_color.set("#FFFFFF")
                if hasattr(self, 'rgba_mode'):
                    self.rgba_mode.set(False)
                
                # Reset other settings
                if hasattr(self, 'max_words'):
                    self.max_words.set(200)
                if hasattr(self, 'scale'):
                    self.scale.set(1)
                
                # Reset mask settings
                if hasattr(self, 'mask_notebook'):
                    self.mask_notebook.select(0)  # Select "No Mask" tab
                if hasattr(self, 'mask_path'):
                    self.mask_path.set("No mask selected")
                self.mask_image = None
                if hasattr(self, 'mask_label'):
                    self.mask_label.config(text="No mask selected")
                
                # Reset contour settings
                if hasattr(self, 'contour_var'):
                    self.contour_var.set(False)
                if hasattr(self, 'contour_width'):
                    self.contour_width.set(3)
                if hasattr(self, 'contour_color'):
                    self.contour_color.set('#000000')
            
                # Reset text mask settings
                if hasattr(self, 'text_mask_input'):
                    debug_print("Clearing text_mask_input in reset_app()")
                    self.text_mask_input.set("")
                if hasattr(self, 'text_mask_font'):
                    self.text_mask_font.set("Arial")
                if hasattr(self, 'text_mask_font_size'):
                    self.text_mask_font_size.set(200)  # Reset to default
                if hasattr(self, 'text_mask_bold'):
                    self.text_mask_bold.set(True)  # Default was True
                if hasattr(self, 'text_mask_italic'):
                    self.text_mask_italic.set(False)
                # Clear text mask preview
                if hasattr(self, 'text_mask_preview_label'):
                    self.text_mask_preview_label.config(image='', text="Preview will appear here")
            
                # Reset working directory
                self.working_folder.set("No folder selected")
                if hasattr(self, 'file_listbox'):
                    self.file_listbox.delete(0, tk.END)
                
                # Clear loaded text
                self.text_content = ""
                if hasattr(self, 'loaded_files_label'):
                    self.loaded_files_label.config(text="No files loaded")
                
                # Clear text input area
                if hasattr(self, 'text_area'):
                    self.text_area.delete(1.0, tk.END)
                
                # Clear canvas
                self.clear_canvas()
                
                # Reset theme to default
                self.current_theme.set("cosmo")
                self.root.style.theme_use("cosmo")
                
                # Note: We don't auto-save after reset to preserve the user's saved configuration
                # Users can manually save if they want to keep the reset state
                self.show_message("Application reset to defaults (not saved)", "good")
                
            except Exception as e:
                if DEBUG and debug_logger:
                    debug_logger.error(f"Failed to reset application: {str(e)}")
                    debug_logger.error("Full traceback:", exc_info=True)
                self.show_message(f"Failed to reset application: {str(e)}", "fail")
    
    def start_tutorial_wizard(self):
        """Start the interactive tutorial wizard"""
        if hasattr(self, 'tutorial_wizard'):
            self.tutorial_wizard.start_tutorial()
        else:
            self.show_message("Tutorial wizard not available", "error")
    
    def show_help(self):
        """Show help in browser as HTML"""
        try:
            # Check if markdown2 is available
            try:
                import markdown2
            except ImportError:
                self.show_message("Please install markdown2: pip install markdown2", "error")
                return
            
            # Read help.md file
            help_md_path = os.path.join(os.path.dirname(__file__), 'help.md')
            if not os.path.exists(help_md_path):
                self.show_message("Help file not found", "error")
                return
            
            with open(help_md_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Convert markdown to HTML with extras for better formatting
            md = markdown2.Markdown(extras=[
                'fenced-code-blocks',
                'tables',
                'strike',
                'task_list',
                'header-ids',
                'code-friendly',
                'break-on-newline'
            ])
            html_content = md.convert(markdown_content)
            
            # Read HTML template
            template_path = os.path.join(os.path.dirname(__file__), 'help_template.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
            
            # Insert content into template
            final_html = html_template.replace('{content}', html_content)
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(final_html)
                temp_path = f.name
            
            # Open in default browser
            webbrowser.open(f'file://{temp_path}')
            
            # Clean up temp file after a delay (give browser time to load)
            def cleanup():
                import time
                time.sleep(5)
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            cleanup_thread = threading.Thread(target=cleanup, daemon=True)
            cleanup_thread.start()
            
        except Exception as e:
            debug_print(f"Error showing help: {str(e)}")
            self.show_message(f"Failed to open help: {str(e)}", "error")

def main():
    global DEBUG
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='WordCloud Magic - Modern Word Cloud Generator')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to print errors and debug info to console and log file')
    args = parser.parse_args()
    
    DEBUG = args.debug
    
    if DEBUG:
        # Setup debug logging
        log_file = setup_debug_logging()
        debug_print("Starting WordCloud Magic in debug mode...")
        debug_print(f"Python version: {sys.version}")
        debug_print(f"Platform: {platform.system()} {platform.release()}")
        debug_print(f"Debug log file: {log_file}")
    
    # Create the app with a modern theme
    root = ttk.Window(themename="cosmo")
    app = ModernWordCloudApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()