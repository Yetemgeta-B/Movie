import customtkinter as ctk
from typing import List, Dict, Callable, Optional
import os
import json
from pathlib import Path
import threading
import pandas as pd
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from config import WORD_DOC_PATH, MOVIE_TABLE_INDEX, SERIES_TABLE_INDEX
from redesigned_ui.word_handler import WordHandler

class DocumentViewScreen(ctk.CTkFrame):
    """
    Document View screen for the application.
    Displays tables from the Word document with options to edit and update.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Initialize variables
        self.word_handler = WordHandler()
        self.movie_data = []
        self.series_data = []
        self.current_view = "movies"  # Default view
        
        # Create UI
        self._create_ui()
        
        # Load data initially
        self.after(100, self._load_document_data)
    
    def _create_ui(self):
        """Create the UI elements for the document view screen"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=15)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Header title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📄 Document View",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(side="left", padx=10, pady=10)
        
        # View selection tabs
        self.tabs_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.tabs_frame.pack(side="right", padx=10, pady=10)
        
        # Movies tab
        self.movies_tab = ctk.CTkButton(
            self.tabs_frame,
            text="🎬 Movies",
            command=lambda: self._switch_view("movies"),
            width=120,
            corner_radius=10,
            fg_color=("#4a86e8", "#2d5bb9"),  # Active initially
            hover_color=("#3a76d8", "#1d4ba9")
        )
        self.movies_tab.pack(side="left", padx=5)
        
        # Series tab
        self.series_tab = ctk.CTkButton(
            self.tabs_frame,
            text="📺 Series",
            command=lambda: self._switch_view("series"),
            width=120,
            corner_radius=10,
            fg_color="transparent",  # Inactive initially
            hover_color=("#e5e5e5", "#444444")
        )
        self.series_tab.pack(side="left", padx=5)
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.header_frame,
            text="🔄 Refresh",
            command=self._load_document_data,
            width=100,
            corner_radius=10
        )
        self.refresh_button.pack(side="right", padx=10)
        
        # Document path display
        self.path_frame = ctk.CTkFrame(self, corner_radius=10)
        self.path_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        path_label = ctk.CTkLabel(
            self.path_frame,
            text=f"Document: {WORD_DOC_PATH}",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70")
        )
        path_label.pack(anchor="w", padx=10, pady=5)
        
        # Content frame with table
        self.content_frame = ctk.CTkFrame(self, corner_radius=15)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Add a loading indicator initially
        self.loading_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.loading_frame.grid(row=0, column=0, sticky="nsew")
        
        loading_label = ctk.CTkLabel(
            self.loading_frame,
            text="Loading document data...",
            font=ctk.CTkFont(size=16)
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _switch_view(self, view):
        """Switch between movies and series views"""
        if view == self.current_view:
            return
        
        self.current_view = view
        
        # Update tab styling
        if view == "movies":
            self.movies_tab.configure(
                fg_color=("#4a86e8", "#2d5bb9"),
                text_color=("#ffffff", "#ffffff")
            )
            self.series_tab.configure(
                fg_color="transparent",
                text_color=("#555555", "#aaaaaa")
            )
        else:
            self.series_tab.configure(
                fg_color=("#4a86e8", "#2d5bb9"),
                text_color=("#ffffff", "#ffffff")
            )
            self.movies_tab.configure(
                fg_color="transparent",
                text_color=("#555555", "#aaaaaa")
            )
        
        # Display the appropriate data
        self._display_table()
    
    def _load_document_data(self):
        """Load data from the Word document"""
        # Show loading indicator
        for widget in self.content_frame.winfo_children():
            if widget != self.loading_frame:
                widget.destroy()
        
        self.loading_frame.grid(row=0, column=0, sticky="nsew")
        
        def load_data():
            try:
                # Open the document
                opened = self.word_handler.open_document()
                if not opened:
                    self.after(0, lambda: self._show_error("Could not open Word document. Please check the path and try again."))
                    return
                
                # Extract movie data
                movie_data = self._extract_movie_data()
                
                # Extract series data
                series_data = self._extract_series_data()
                
                # Close the document
                self.word_handler.close_document()
                
                # Update our data
                self.movie_data = movie_data
                self.series_data = series_data
                
                # Update the UI
                self.after(0, self._display_table)
                
            except Exception as e:
                print(f"Error loading document data: {e}")
                self.after(0, lambda: self._show_error(f"Error loading document data: {e}"))
                
                # Hide loading indicator
                self.loading_frame.grid_forget()
        
        # Start loading in a separate thread
        threading.Thread(target=load_data).start()
    
    def _extract_movie_data(self):
        """Extract movie data from the Word document table"""
        try:
            movies = []
            
            if not self.word_handler.document:
                return movies
                
            try:
                # Get the movie table
                movie_table = self.word_handler.movie_table
                if not movie_table:
                    return movies
                
                # Get column headers (from first row)
                headers = []
                header_row = movie_table.rows[0]
                for cell in header_row.cells:
                    headers.append(cell.text.strip())
                
                # Extract data from each row
                for row_idx in range(1, len(movie_table.rows)):
                    row = movie_table.rows[row_idx]
                    
                    # Create a dictionary for this row
                    row_data = {
                        "_row_idx": row_idx  # Store the row index for editing
                    }
                    
                    # Get the data for each column
                    for col_idx, cell in enumerate(row.cells):
                        if col_idx < len(headers):
                            row_data[headers[col_idx]] = cell.text.strip()
                    
                    movies.append(row_data)
                
                return movies
                
            except Exception as table_e:
                print(f"Error extracting from movie table: {table_e}")
                return movies
                
        except Exception as e:
            print(f"Error in _extract_movie_data: {e}")
            return []
    
    def _extract_series_data(self):
        """Extract series data from the Word document table"""
        try:
            series_list = []
            
            if not self.word_handler.document:
                return series_list
                
            try:
                # Get the series table
                series_table = self.word_handler.series_table
                if not series_table:
                    return series_list
                
                # Get column headers (from first row)
                headers = []
                header_row = series_table.rows[0]
                for cell in header_row.cells:
                    headers.append(cell.text.strip())
                
                # Extract data from each row
                for row_idx in range(1, len(series_table.rows)):
                    row = series_table.rows[row_idx]
                    
                    # Create a dictionary for this row
                    row_data = {
                        "_row_idx": row_idx  # Store the row index for editing
                    }
                    
                    # Get the data for each column
                    for col_idx, cell in enumerate(row.cells):
                        if col_idx < len(headers):
                            row_data[headers[col_idx]] = cell.text.strip()
                    
                    series_list.append(row_data)
                
                return series_list
                
            except Exception as table_e:
                print(f"Error extracting from series table: {table_e}")
                return series_list
                
        except Exception as e:
            print(f"Error in _extract_series_data: {e}")
            return []
    
    def _display_table(self):
        """Display the table based on current view"""
        # Clear the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Get the data based on the current view
        data = self.movie_data if self.current_view == "movies" else self.series_data
        
        if not data:
            # Show message if no data
            no_data_label = ctk.CTkLabel(
                self.content_frame,
                text=f"No data available for {self.current_view}. Please ensure the document contains valid tables.",
                font=ctk.CTkFont(size=16)
            )
            no_data_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        # Get the columns (assume all items have the same keys)
        columns = list(data[0].keys())
        if "_row_idx" in columns:
            columns.remove("_row_idx")  # Don't display this internal field
        
        # Create table frame
        table_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            corner_radius=0
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Buttons frame for actions
        buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Add entry button
        add_button = ctk.CTkButton(
            buttons_frame,
            text="➕ Add Entry",
            command=self._add_new_entry,
            width=120,
            corner_radius=10
        )
        add_button.pack(side="left", padx=5)
        
        # Export to CSV button
        export_button = ctk.CTkButton(
            buttons_frame,
            text="📊 Export to CSV",
            command=self._export_to_csv,
            width=150,
            corner_radius=10
        )
        export_button.pack(side="left", padx=5)
        
        # Configure the table frame grid
        for i, col in enumerate(columns):
            table_frame.grid_columnconfigure(i, weight=1, minsize=100)
        
        # Create column headers
        for i, col in enumerate(columns):
            header_label = ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=("#e0e0e0", "#333333"),
                corner_radius=6
            )
            header_label.grid(row=0, column=i, sticky="ew", padx=2, pady=2)
        
        # Create rows with data
        for row_idx, item in enumerate(data):
            for col_idx, col in enumerate(columns):
                cell_value = item.get(col, "")
                
                # Create cell frame
                cell_frame = ctk.CTkFrame(
                    table_frame,
                    fg_color=("#f9f9f9", "#2a2a2a") if row_idx % 2 == 0 else ("#f0f0f0", "#222222"),
                    corner_radius=6
                )
                cell_frame.grid(row=row_idx + 1, column=col_idx, sticky="ew", padx=2, pady=2)
                
                # Add text to cell
                cell_label = ctk.CTkLabel(
                    cell_frame,
                    text=cell_value,
                    anchor="w",
                    justify="left",
                    padx=5
                )
                cell_label.pack(side="left", fill="both", expand=True, padx=5, pady=3)
                
                # Bind click event to edit
                cell_frame.bind("<Button-1>", lambda e, r=item.get("_row_idx"), c=col, h=col, i=item: 
                              self._edit_cell(e, r, c, h, i))
                cell_label.bind("<Button-1>", lambda e, r=item.get("_row_idx"), c=col, h=col, i=item: 
                              self._edit_cell(e, r, c, h, i))
    
    def _edit_cell(self, event, row_idx, col_name, header, item):
        """Handle the edit of a cell in the table"""
        if header in ["No", "NO"]:  # Don't allow editing of the number column
            return
            
        # Create a dialog for editing
        dialog = ctk.CTkInputDialog(
            text=f"Edit {header}:",
            title=f"Edit {self.current_view.capitalize()} Data",
            entry_text=item.get(header, "")
        )
        
        # Get the new value
        new_value = dialog.get_input()
        
        # If the user provided a value, update the document
        if new_value is not None and new_value != item.get(header, ""):
            self._update_document_cell(row_idx, header, new_value)
    
    def _update_document_cell(self, row_idx, header, new_value):
        """Update a cell in the Word document"""
        def update_cell():
            try:
                # Open the document
                opened = self.word_handler.open_document()
                if not opened:
                    self.after(0, lambda: self._show_error("Could not open Word document for editing."))
                    return
                
                # Get the table and column index
                if self.current_view == "movies":
                    table = self.word_handler.movie_table
                    # Find the column index
                    col_idx = None
                    for i in range(len(table.columns)):
                        if i < len(table.columns):
                            first_cell_text = table.cell(0, i).text.strip()
                            if first_cell_text == header:
                                col_idx = i
                                break
                else:
                    table = self.word_handler.series_table
                    # Find the column index
                    col_idx = None
                    for i in range(len(table.columns)):
                        if i < len(table.columns):
                            first_cell_text = table.cell(0, i).text.strip()
                            if first_cell_text == header:
                                col_idx = i
                                break
                
                if col_idx is not None:
                    # Update the cell
                    table.cell(row_idx, col_idx).text = new_value
                    
                    # Save the document
                    self.word_handler.save_document()
                    
                    # Reload data
                    self._load_document_data()
                    
                    self.after(0, lambda: self._show_message("Cell updated successfully."))
                else:
                    self.after(0, lambda: self._show_error(f"Could not find column '{header}' in the table."))
                
                # Close document
                self.word_handler.close_document()
                
            except Exception as e:
                print(f"Error updating cell: {e}")
                self.after(0, lambda: self._show_error(f"Error updating cell: {e}"))
        
        # Start update in a separate thread
        threading.Thread(target=update_cell).start()
    
    def _add_new_entry(self):
        """Add a new entry to the table"""
        # This could open a more complex dialog to add entries
        self._show_message("Add Entry feature coming soon!", "Feature Not Available")
    
    def _export_to_csv(self):
        """Export the current table to CSV"""
        data = self.movie_data if self.current_view == "movies" else self.series_data
        
        if not data:
            self._show_error("No data to export.")
            return
        
        # Create a pandas DataFrame
        df = pd.DataFrame(data)
        
        # Remove internal columns
        if "_row_idx" in df.columns:
            df = df.drop("_row_idx", axis=1)
        
        try:
            # Get file location to save
            file_types = [("CSV Files", "*.csv"), ("All Files", "*.*")]
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=file_types,
                initialdir=os.path.expanduser("~"),
                initialfile=f"{self.current_view}_export.csv",
                title="Save CSV As"
            )
            
            if file_path:
                df.to_csv(file_path, index=False)
                self._show_message(f"Data exported to {file_path} successfully.")
        except Exception as e:
            self._show_error(f"Error exporting data: {e}")
    
    def _show_error(self, message):
        """Show an error message to the user"""
        dialog = ctk.CTkMessagebox(
            title="Error",
            message=message,
            icon="cancel",
            option_1="OK"
        )
        
    def _show_message(self, message, title="Message"):
        """Show an info message to the user"""
        dialog = ctk.CTkMessagebox(
            title=title,
            message=message,
            icon="info",
            option_1="OK"
        ) 