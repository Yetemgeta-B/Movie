class SeriesAddDialog(ctk.CTkToplevel):
    """Dialog for adding a series with watch date and rating"""
    
    def __init__(self, parent, series, details):
        super().__init__(parent)
        self.title("Add Series")
        self.geometry("600x700")  # Increased size to accommodate series poster
        # Remove the resizable call since CTkToplevel already handles this correctly
        # self.resizable(False, False)  # This was causing the error
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog on the parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Store series data
        self.series = series
        self.details = details
        self.parent = parent
        self.result = None
        self.saved_to_word = False
        
        # Initialize Word handler
        self.word_handler = WordHandler()
        
        # Create UI
        self._create_ui() 