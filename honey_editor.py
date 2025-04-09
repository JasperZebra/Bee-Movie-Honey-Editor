import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import struct
import logging
import binascii

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL/Pillow library not found. Install with 'pip install pillow' for PNG icon support.")

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('honey_editor.log'), logging.StreamHandler()]
)
logger = logging.getLogger('HoneyEditor')

class HoneyEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bee Movie Honey Editor | Made by: Jasper_Zebra")
        self.root.geometry("800x520")
        self.root.resizable(False, False)
        
        # Save file data
        self.file_path = None
        self.file_data = None
        self.honey_offset = 0xD008  # Fixed offset for honey value
        self.honey_value = 0
        self.has_changes = False
        
        # Load custom font if available
        self.load_custom_font()
        
        # Setup styles and themes before UI
        self.setup_styles()
        
        # Create UI elements
        self.setup_ui()
        
        # Try to set an icon
        self.set_icon()
    
    def load_custom_font(self):
        """Load custom font if available"""
        self.custom_font = None
        try:
            # You can replace this with a custom font file if you have one
            pass
        except:
            pass
    
    def set_icon(self):
        """Set window icon from PNG file"""
        # First try with PIL for PNG support
        if HAS_PIL:
            try:
                # List of possible PNG icon locations to try
                png_icon_paths = [
                    "assets/honey_editor.png",  # Added the new icon path
                    os.path.join(os.path.dirname(__file__), "bee_icon.png")
                ]
                
                # Try each PNG path
                for path in png_icon_paths:
                    if os.path.exists(path):
                        icon_image = Image.open(path)
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        
                        # Keep a reference to prevent garbage collection
                        self.icon_image = icon_photo
                        
                        # Set the icon
                        self.root.iconphoto(True, icon_photo)
                        
                        logger.info(f"Successfully set PNG icon from {path}")
                        return
            except Exception as e:
                logger.error(f"Error setting PNG icon: {str(e)}", exc_info=True)

        try:
            # Try to find an ico file in common locations
            ico_icon_paths = [
                "bee_icon.ico", 
                "icons/bee_icon.ico",
                os.path.join(os.path.dirname(__file__), "bee_icon.ico")
            ]
            
            for path in ico_icon_paths:
                if os.path.exists(path):
                    self.root.iconbitmap(path)
                    logger.info(f"Successfully set ICO icon from {path}")
                    return
        except Exception as e:
            logger.error(f"Error setting ICO icon: {str(e)}")
            pass

    def setup_styles(self):
        """Setup custom styles and themes"""
        style = ttk.Style()
        
        # Use clam theme as base
        style.theme_use('clam')
        
        # Define colors - honey-themed color palette
        colors = {
            'background': '#2D2B27',    # Dark brown
            'darker_bg': '#1E1C19',     # Darker brown for contrast
            'foreground': '#F3E9C4',    # Light honey color
            'highlight': '#F9B947',     # Bright honey color
            'button_bg': '#8C5E1A',     # Medium brown
            'button_hover': '#B37920',  # Lighter brown for hover
            'error': '#D1483F',         # Red for errors
            'success': '#599A44',       # Green for success
            'border': '#8C5E1A',        # Medium brown for borders
            'entry_bg': '#403D39',      # Slightly lighter than background
        }
        
        # Store colors for later use
        self.colors = colors
        
        # Configure global style
        style.configure('.', 
            background=colors['background'],
            foreground=colors['foreground'],
            troughcolor=colors['darker_bg'],
            fieldbackground=colors['entry_bg'],
            borderwidth=1,
            bordercolor=colors['border'],
            font=('Arial', 10, 'bold')
        )
        
        # Frame styling
        style.configure('TFrame', background=colors['background'])
        
        # LabelFrame styling
        style.configure('TLabelframe', 
            background=colors['background'],
            bordercolor=colors['border'],
            font=('Arial', 15, 'bold')
        )
        style.configure('TLabelframe.Label', 
            background=colors['background'],
            foreground=colors['highlight'],
            font=('Arial', 15, 'bold')
        )
        
        # Button styling
        style.configure('TButton', 
            background=colors['button_bg'],
            foreground=colors['foreground'],
            bordercolor=colors['border'],
            lightcolor=colors['button_bg'],
            darkcolor=colors['button_bg'],
            focuscolor=colors['highlight'],
            padding=6
        )
        style.map('TButton',
            background=[
                ('pressed', colors['darker_bg']), 
                ('active', colors['button_hover'])
            ],
            foreground=[
                ('pressed', colors['foreground']), 
                ('active', colors['foreground'])
            ]
        )
        
        # Preset button style - more honey-like
        style.configure('Honey.TButton', 
            background=colors['highlight'],
            foreground=colors['darker_bg'],
            font=('Arial', 10, 'bold')
        )
        style.map('Honey.TButton',
            background=[
                ('pressed', colors['button_bg']), 
                ('active', '#FDCA6E')  # Even brighter on hover
            ],
            foreground=[
                ('pressed', colors['foreground']), 
                ('active', colors['darker_bg'])
            ]
        )
        
        # Label styling
        style.configure('TLabel', 
            background=colors['background'],
            foreground=colors['foreground'],
            font=('Arial', 15, 'bold')
        )
        
        # Title label style
        style.configure('Title.TLabel', 
            background=colors['background'],
            foreground=colors['highlight'],
            font=('Arial', 15, 'bold')
        )
        
        # Value label style
        style.configure('Value.TLabel', 
            background=colors['background'],
            foreground=colors['highlight'],
            font=('Arial', 15, 'bold')
        )
        
        # Entry styling
        style.configure('TEntry', 
            fieldbackground=colors['entry_bg'],
            foreground=colors['foreground'],
            bordercolor=colors['border'],
            font=('Arial', 15, 'bold')
        )
        
        # Medium entry style for reasonably sized input boxes
        style.configure('Medium.TEntry', 
            fieldbackground=colors['entry_bg'],
            foreground=colors['foreground'],
            bordercolor=colors['border'],
            padding=5,  # Reduced padding
            font=('Arial', 15, 'bold')  # Smaller font size
        )

    def setup_ui(self):
        # Create main frame with adjusted padding
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with more spacing
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title font
        title_font = ('Arial', 32, 'bold')
        
        # Use the custom font directly in the label
        title_label = ttk.Label(title_frame, text="BEE MOVIE HONEY EDITOR", 
                            style='Title.TLabel', font=title_font)
        title_label.pack(side=tk.LEFT, pady=5)
        
        # Version label with larger font
        version_font = ('Arial', 16, 'bold')
        version_label = ttk.Label(title_frame, text="v1.2", foreground=self.colors['highlight'], font=version_font)
        version_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # File section with adjusted padding
        file_frame = ttk.LabelFrame(main_frame, text="Save File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.file_label = ttk.Label(file_frame, text="No file loaded", wraplength=500)
        self.file_label.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        load_button = ttk.Button(file_frame, text="Load Save", command=self.load_save, width=15)
        load_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Editor section with adjusted padding
        editor_frame = ttk.LabelFrame(main_frame, text="Honey Editor", padding=10)
        editor_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Current honey display with honey icon and adjusted spacing
        honey_frame = ttk.Frame(editor_frame)
        honey_frame.pack(fill=tk.X, pady=10)
        
        # Honey icon
        honey_icon = ttk.Label(honey_frame, text="🍯", font=("Arial", 24))
        honey_icon.pack(side=tk.LEFT, padx=(10, 15))
        
        # Adjusted font for labels
        honey_label_font = ("Arial", 16)
        ttk.Label(honey_frame, text="Current Honey:", font=honey_label_font).pack(side=tk.LEFT, padx=10)
        
        self.current_value = tk.StringVar(value="0")
        # Adjusted font for value
        honey_value_font = ("Arial", 18, "bold")
        ttk.Label(honey_frame, textvariable=self.current_value, style='Value.TLabel', font=honey_value_font).pack(side=tk.LEFT, padx=10)
        
        # New honey value entry with adjusted spacing
        edit_frame = ttk.Frame(editor_frame)
        edit_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(edit_frame, text="New Honey Value:").pack(side=tk.LEFT, padx=10)
        self.honey_var = tk.StringVar(value="0")
        
        # Create entry with specified font
        entry_font = ('Arial', 12)
        honey_entry = ttk.Entry(
            edit_frame, 
            textvariable=self.honey_var, 
            width=18, 
            justify='center',
            font=entry_font  # Apply custom font
        )
        honey_entry.pack(side=tk.LEFT, padx=10, ipady=3)
        
        # Preset buttons with adjusted spacing
        presets_frame = ttk.Frame(editor_frame)
        presets_frame.pack(fill=tk.X, pady=(10, 15))
        
        preset_label = ttk.Label(presets_frame, text="Quick Presets:")
        preset_label.pack(side=tk.LEFT, padx=(10, 15))
        
        presets = [10000, 50000, 100000, 999999, 9999999]
        for preset in presets:
            formatted_value = format(preset, ",")
            btn = ttk.Button(presets_frame, text=formatted_value, 
                            command=lambda val=preset: self.set_preset(val),
                            style='Honey.TButton', width=10)
            btn.pack(side=tk.LEFT, padx=8)
        
        # Bottom section with save button and status
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        status_font = ('Arial', 12)
        self.status_label = ttk.Label(bottom_frame, text="Ready", font=status_font)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Save button - adjusted size
        self.save_button = ttk.Button(bottom_frame, text="Save Changes", command=self.save_changes, 
                                    state="disabled", width=15)
        self.save_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Bind Enter key to save changes
        self.root.bind('<Return>', lambda e: self.save_changes())

    def show_welcome_message(self, filename, honey_value):
        """Show welcome message when a save file is loaded"""
        messagebox.showinfo(
            "Save File Loaded", 
            f"Successfully loaded save file:\n{filename}\n\nCurrent honey: {honey_value:,}"
        )

    def load_save(self):
        file_path = filedialog.askopenfilename(
            title="Select Bee Movie Save File",
            filetypes=[
                ("Bee Movie Save", "*.BMGSave"),
                ("All Save Files", "*.BMGSave"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self.file_path = Path(file_path)
            self.file_label.config(text=self.file_path.name)
            
            # Read the file
            with open(self.file_path, 'rb') as f:
                self.file_data = f.read()
            
            # Read the honey value at the fixed offset
            honey_bytes = self.file_data[self.honey_offset:self.honey_offset+4]
            self.honey_value = int.from_bytes(honey_bytes, byteorder='big')
            
            # Update UI elements
            self.current_value.set(f"{self.honey_value:,}")
            self.honey_var.set(str(self.honey_value))
            
            # Enable save button
            self.save_button.config(state="normal")
            
            self.status_label.config(text="Save file loaded successfully")
            
            # Show welcome message popup
            self.show_welcome_message(self.file_path.name, self.honey_value)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load save file: {str(e)}")
            logger.error(f"Error loading save file: {str(e)}", exc_info=True)
            self.file_path = None

    def set_preset(self, value):
        """Set a preset honey value"""
        self.honey_var.set(str(value))
        self.has_changes = True
    
    def save_changes(self):
        if not self.file_path:
            messagebox.showinfo("Info", "Please load a save file first.")
            return
        
        try:
            # Get the new honey value
            try:
                new_honey = int(self.honey_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for honey.")
                return
            
            if new_honey < 0:
                messagebox.showwarning("Warning", "Honey value cannot be negative. Setting to 0.")
                new_honey = 0
                self.honey_var.set("0")
            
            # Create backup
            backup_path = self.file_path.with_suffix(self.file_path.suffix + ".backup")
            if not backup_path.exists():
                with open(self.file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                logger.info(f"Created backup at {backup_path}")
            
            # Make a copy of the file data
            updated_data = bytearray(self.file_data)
            
            # Update the 32-bit BE honey value
            new_bytes = new_honey.to_bytes(4, byteorder='big')
            updated_data[self.honey_offset:self.honey_offset+4] = new_bytes
            
            # Write the updated data back to the file
            with open(self.file_path, 'wb') as f:
                f.write(updated_data)
            
            # Update UI
            self.file_data = updated_data  # Update the stored file data
            self.honey_value = new_honey
            self.current_value.set(f"{new_honey:,}")
            self.has_changes = False
            
            self.status_label.config(text="Save file updated successfully", foreground=self.colors['success'])
            
            # Show success message popup
            messagebox.showinfo(
                "Save Successful", 
                f"Honey has been updated!\n\nPrevious value: {self.honey_value:,}\nNew value: {new_honey:,}\n\nA backup of your original save file was created."
            )
            
            logger.info(f"Updated honey value to {new_honey}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
            logger.error(f"Error saving changes: {str(e)}", exc_info=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = HoneyEditor(root)
    root.mainloop()