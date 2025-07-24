import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
import os
import threading
from PIL import Image, ImageTk
import numpy as np
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

class ModernWordCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WordCloud Magic - Modern Word Cloud Generator")
        self.root.geometry("1300x850")
        
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
        
        # Canvas settings
        self.canvas_width = tk.IntVar(value=800)
        self.canvas_height = tk.IntVar(value=600)
        self.bg_color = tk.StringVar(value="#FFFFFF")
        
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
        left_panel.pack_propagate(False)
        paned.add(left_panel, weight=1)
        
        # Right panel (preview)
        right_panel = ttk.Frame(paned, padding="10")
        paned.add(right_panel, weight=2)
        
        # Create notebook for organized controls
        self.notebook = ttk.Notebook(left_panel, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=TRUE)
        
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
            if col > 1:
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
        
        # Mask file selection
        mask_file_frame = ttk.LabelFrame(mask_frame, text="Mask Image", padding=10)
        mask_file_frame.pack(fill=X, pady=(0, 10))
        
        mask_info = ttk.Frame(mask_file_frame)
        mask_info.pack(fill=X, pady=(0, 10))
        
        ttk.Label(mask_info,
                 textvariable=self.mask_path,
                 bootstyle="secondary",
                 font=('Segoe UI', 10)).pack(side=LEFT)
        
        mask_btn_frame = ttk.Frame(mask_file_frame)
        mask_btn_frame.pack(fill=X)
        
        ttk.Button(mask_btn_frame,
                  text="Select Mask",
                  command=self.select_mask,
                  bootstyle="primary",
                  width=15).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(mask_btn_frame,
                  text="Clear Mask",
                  command=self.clear_mask,
                  bootstyle="secondary",
                  width=15).pack(side=LEFT)
        
        # Contour options
        self.contour_frame = ttk.LabelFrame(mask_frame, text="Contour Options (requires mask)", padding=10)
        self.contour_frame.pack(fill=X, pady=(0, 10))
        
        # Contour width
        width_container = ttk.Frame(self.contour_frame)
        width_container.pack(fill=X, pady=(0, 10))
        
        width_label_frame = ttk.Frame(width_container)
        width_label_frame.pack(fill=X)
        self.contour_width_lbl = ttk.Label(width_label_frame, text="Contour Width:", font=('Segoe UI', 10))
        self.contour_width_lbl.pack(side=LEFT)
        self.contour_width_label = ttk.Label(width_label_frame, text="2 pixels",
                                           bootstyle="primary", font=('Segoe UI', 10, 'bold'))
        self.contour_width_label.pack(side=RIGHT)
        
        self.contour_width_scale = ttk.Scale(width_container,
                                           from_=0,
                                           to=10,
                                           value=2,
                                           command=self.update_contour_width,
                                           bootstyle="primary")
        self.contour_width_scale.pack(fill=X, pady=(5, 0))
        
        # Contour color
        color_container = ttk.Frame(self.contour_frame)
        color_container.pack(fill=X)
        
        self.contour_color_lbl = ttk.Label(color_container, text="Contour Color:", font=('Segoe UI', 10))
        self.contour_color_lbl.pack(side=LEFT)
        
        self.contour_color_preview = ttk.Frame(color_container, width=30, height=30, bootstyle="dark")
        self.contour_color_preview.pack(side=RIGHT, padx=(10, 0))
        
        self.contour_color_btn = ttk.Button(color_container,
                                          text="Choose Color",
                                          command=self.choose_contour_color,
                                          bootstyle="primary-outline",
                                          width=15)
        self.contour_color_btn.pack(side=RIGHT)
        
        # Store contour widgets for enabling/disabling
        self.contour_widgets = [self.contour_width_scale, self.contour_color_btn,
                               self.contour_width_lbl, self.contour_color_lbl]
        
        # Initially disable contour options
        self.update_contour_state()
        
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
        
        # Canvas options
        canvas_frame = ttk.LabelFrame(mask_frame, text="Canvas Settings", padding=10)
        canvas_frame.pack(fill=X, pady=(0, 10))
        
        # Canvas size
        size_container = ttk.Frame(canvas_frame)
        size_container.pack(fill=X, pady=(0, 10))
        
        # Width
        width_frame = ttk.Frame(size_container)
        width_frame.pack(side=LEFT, padx=(0, 20))
        ttk.Label(width_frame, text="Width:", font=('Segoe UI', 10)).pack(side=LEFT)
        ttk.Spinbox(width_frame,
                   from_=400,
                   to=2000,
                   textvariable=self.canvas_width,
                   width=10,
                   bootstyle="primary").pack(side=LEFT, padx=(5, 0))
        ttk.Label(width_frame, text="px", font=('Segoe UI', 10)).pack(side=LEFT)
        
        # Height
        height_frame = ttk.Frame(size_container)
        height_frame.pack(side=LEFT)
        ttk.Label(height_frame, text="Height:", font=('Segoe UI', 10)).pack(side=LEFT)
        ttk.Spinbox(height_frame,
                   from_=300,
                   to=2000,
                   textvariable=self.canvas_height,
                   width=10,
                   bootstyle="primary").pack(side=LEFT, padx=(5, 0))
        ttk.Label(height_frame, text="px", font=('Segoe UI', 10)).pack(side=LEFT)
        
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
        
        # Mask preview (smaller now)
        preview_container = ttk.LabelFrame(mask_frame, text="Mask Preview", padding=10)
        preview_container.pack(fill=BOTH, expand=TRUE)
        
        self.mask_preview_label = ttk.Label(preview_container,
                                           text="No mask selected",
                                           anchor=CENTER,
                                           font=('Segoe UI', 10))
        self.mask_preview_label.pack(fill=BOTH, expand=TRUE)
        
    def create_preview_area(self, parent):
        """Create the word cloud preview area"""
        preview_container = ttk.LabelFrame(parent, text="Word Cloud Preview", padding=15)
        preview_container.pack(fill=BOTH, expand=TRUE)
        
        # Canvas for word cloud
        canvas_frame = ttk.Frame(preview_container, bootstyle="secondary", padding=2)
        canvas_frame.pack(fill=BOTH, expand=TRUE, pady=(0, 15))
        
        # Calculate initial figure size based on canvas settings
        fig_width = self.canvas_width.get() / 100  # Convert to inches (100 DPI)
        fig_height = self.canvas_height.get() / 100
        
        self.figure = plt.Figure(figsize=(fig_width, fig_height), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=BOTH, expand=TRUE)
        
        # Initial empty plot with message
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Generate a word cloud to see it here', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, color='gray')
        ax.axis('off')
        self.canvas.draw()
        
        # Store reference to preview canvas frame for theme updates
        self.preview_canvas_frame = canvas_frame
        
        # Button frame
        button_frame = ttk.Frame(preview_container)
        button_frame.pack(fill=X)
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(button_frame, 
                                       mode='indeterminate',
                                       bootstyle="success-striped")
        
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
                
                # Update mask preview
                img = Image.open(file_path)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.mask_preview_label.config(image=photo, text="")
                self.mask_preview_label.image = photo  # Keep a reference
                
                # Enable contour options when mask is selected
                self.update_contour_state(True)
            except Exception as e:
                self.show_toast(f"Error loading mask: {str(e)}", "danger")
    
    def clear_mask(self):
        """Clear selected mask"""
        self.mask_image = None
        self.mask_path.set("No mask selected")
        self.mask_preview_label.config(image="", text="No mask selected")
        
        # Disable contour options when mask is cleared
        self.update_contour_state(False)
    
    def update_contour_width(self, value):
        """Update contour width label"""
        val = int(float(value))
        self.contour_width.set(val)
        self.contour_width_label.config(text=f"{val} pixels")
    
    def choose_contour_color(self):
        """Open color chooser for contour color"""
        dialog = ColorChooserDialog()
        dialog.show()
        color = dialog.result
        if color:
            hex_color = color.hex
            self.contour_color.set(hex_color)
            # Update preview - create a colored frame
            self.contour_color_preview.configure(style="")
            self.contour_color_preview.configure(background=hex_color)
    
    def choose_bg_color(self):
        """Open color chooser for background color"""
        dialog = ColorChooserDialog()
        dialog.show()
        color = dialog.result
        if color:
            hex_color = color.hex
            self.bg_color.set(hex_color)
            # Update preview
            self.bg_color_preview.configure(style="")
            self.bg_color_preview.configure(background=hex_color)
    
    def update_preview_size(self, *args):
        """Update preview canvas size when dimensions change"""
        try:
            # Calculate new figure size
            fig_width = self.canvas_width.get() / 100  # Convert to inches
            fig_height = self.canvas_height.get() / 100
            
            # Update figure size
            self.figure.set_size_inches(fig_width, fig_height)
            
            # Redraw canvas
            self.canvas.draw()
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
                'max_words': 200,
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
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get the word cloud as an image
        wc_image = self.wordcloud.to_image()
        
        if self.rgba_mode.get():
            # For RGBA mode, create a checkered background to show transparency
            import numpy as np
            height, width = wc_image.size[1], wc_image.size[0]
            
            # Create checkered pattern
            checker_size = 20
            checkerboard = np.zeros((height, width, 3))
            for i in range(0, height, checker_size * 2):
                for j in range(0, width, checker_size * 2):
                    checkerboard[i:i+checker_size, j:j+checker_size] = 0.9
                    checkerboard[i+checker_size:i+2*checker_size, j+checker_size:j+2*checker_size] = 0.9
            for i in range(checker_size, height, checker_size * 2):
                for j in range(0, width, checker_size * 2):
                    checkerboard[i:i+checker_size, j:j+checker_size] = 0.95
            for i in range(0, height, checker_size * 2):
                for j in range(checker_size, width, checker_size * 2):
                    checkerboard[i:i+checker_size, j:j+checker_size] = 0.95
            
            # Show checkerboard first
            ax.imshow(checkerboard, extent=[0, width, height, 0])
            
            # Overlay the word cloud with alpha
            ax.imshow(wc_image, interpolation='bilinear', extent=[0, width, height, 0])
        else:
            # For RGB mode, just show the image
            ax.imshow(wc_image, interpolation='bilinear')
        
        ax.axis('off')
        ax.set_xlim(0, wc_image.size[0])
        ax.set_ylim(wc_image.size[1], 0)
        
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