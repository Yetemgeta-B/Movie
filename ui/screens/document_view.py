import customtkinter as ctk
from typing import List, Dict, Callable, Optional
import os
import json
from pathlib import Path
import threading
import pandas as pd
from config import WORD_DOC_PATH, MOVIE_TABLE_INDEX, SERIES_TABLE_INDEX
from word_handler import WordHandler

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
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Header title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📄 Document View",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(side="left", padx=10, pady=10)
        
        # View selection tabs
        self.tabs_frame = ctk.CTkFrame(self.header_frame)
        self.tabs_frame.pack(side="right", padx=10, pady=10)
        
        # Movies tab
        self.movies_tab = ctk.CTkButton(
            self.tabs_frame,
            text="🎬 Movies",
            command=lambda: self._switch_view("movies"),
            width=120,
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
            fg_color="transparent",  # Inactive initially
            hover_color=("#e5e5e5", "#444444")
        )
        self.series_tab.pack(side="left", padx=5)
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.header_frame,
            text="🔄 Refresh",
            command=self._load_document_data,
            width=100
        )
        self.refresh_button.pack(side="right", padx=10)
        
        # Document path display
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        path_label = ctk.CTkLabel(
            self.path_frame,
            text=f"Document: {WORD_DOC_PATH}",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70")
        )
        path_label.pack(anchor="w", padx=10, pady=5)
        
        # Content frame with table
        self.content_frame = ctk.CTkFrame(self)
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
                self.word_handler.close_document(save=False)
                
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
            
            if not self.word_handler.doc:
                return movies
                
            try:
                table = self.word_handler.doc.Tables(MOVIE_TABLE_INDEX)
                
                # Get column headers (from first row)
                headers = []
                for col_idx in range(1, table.Columns.Count + 1):
                    cell_text = table.Cell(1, col_idx).Range.Text.strip().rstrip('\r\a\x07')
                    headers.append(cell_text)
                
                # Extract data from each row (starting from second row)
                for row_idx in range(2, table.Rows.Count + 1):
                    movie = {}
                    
                    for col_idx, header in enumerate(headers, start=1):
                        cell_text = table.Cell(row_idx, col_idx).Range.Text.strip().rstrip('\r\a\x07')
                        movie[header] = cell_text
                    
                    # Add row number for reference
                    movie["_row"] = row_idx
                    
                    movies.append(movie)
                    
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
            
            if not self.word_handler.doc:
                return series_list
                
            try:
                table = self.word_handler.doc.Tables(SERIES_TABLE_INDEX)
                
                # Get column headers (from first row)
                headers = []
                for col_idx in range(1, table.Columns.Count + 1):
                    cell_text = table.Cell(1, col_idx).Range.Text.strip().rstrip('\r\a\x07')
                    headers.append(cell_text)
                
                # Extract data from each row (starting from second row)
                for row_idx in range(2, table.Rows.Count + 1):
                    series = {}
                    
                    for col_idx, header in enumerate(headers, start=1):
                        cell_text = table.Cell(row_idx, col_idx).Range.Text.strip().rstrip('\r\a\x07')
                        series[header] = cell_text
                    
                    # Add row number for reference
                    series["_row"] = row_idx
                    
                    series_list.append(series)
                    
            except Exception as table_e:
                print(f"Error extracting from series table: {table_e}")
            
            return series_list
        except Exception as e:
            print(f"Error in _extract_series_data: {e}")
            return []
    
    def _display_table(self):
        """Display the table based on current view"""
        # Hide loading indicator
        self.loading_frame.grid_forget()
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create table frame
        table_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=("white", "#2b2b2b")
        )
        table_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Get the data for the current view
        data = self.movie_data if self.current_view == "movies" else self.series_data
        
        if not data:
            # Show empty state
            empty_label = ctk.CTkLabel(
                table_frame,
                text=f"No {'movie' if self.current_view == 'movies' else 'series'} data found in the document.",
                font=ctk.CTkFont(size=14)
            )
            empty_label.pack(pady=50)
            return
        
        # Get all column headers
        headers = list(data[0].keys())
        if "_row" in headers:
            headers.remove("_row")  # Don't show internal row reference
        
        # Create table grid
        num_rows = len(data) + 1  # +1 for header
        num_cols = len(headers)
        
        # Configure grid
        for i in range(num_cols):
            table_frame.grid_columnconfigure(i, weight=1, minsize=100)
        
        # Add headers
        for col_idx, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                fg_color=("#e0e0e0", "#3d3d3d"),
                corner_radius=6,
                padx=10,
                pady=5
            )
            header_label.grid(row=0, column=col_idx, sticky="ew", padx=2, pady=2)
        
        # Add rows
        for row_idx, item in enumerate(data, start=1):
            row_bg = ("#f5f5f5", "#333333") if row_idx % 2 == 0 else ("#ebebeb", "#2e2e2e")
            
            for col_idx, header in enumerate(headers):
                cell_value = item.get(header, "")
                
                cell_frame = ctk.CTkFrame(
                    table_frame,
                    fg_color=row_bg,
                    corner_radius=6
                )
                cell_frame.grid(row=row_idx, column=col_idx, sticky="ew", padx=2, pady=2)
                
                cell_label = ctk.CTkLabel(
                    cell_frame,
                    text=cell_value,
                    wraplength=150,
                    justify="left",
                    padx=10,
                    pady=5
                )
                cell_label.pack(fill="both", expand=True)
                
                # Add cell edit on double click
                cell_frame.bind("<Double-1>", lambda e, r=row_idx, c=col_idx, h=header, item=item: self._edit_cell(e, r, c, h, item))
        
        # Add actions row at the bottom
        actions_frame = ctk.CTkFrame(self.content_frame)
        actions_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(10, 0))
        
        # Add new entry button
        add_button = ctk.CTkButton(
            actions_frame,
            text=f"Add New {'Movie' if self.current_view == 'movies' else 'Series'}",
            command=self._add_new_entry,
            width=200
        )
        add_button.pack(side="left", padx=10, pady=10)
        
        # Export button
        export_button = ctk.CTkButton(
            actions_frame,
            text="Export to CSV",
            command=self._export_to_csv,
            width=150
        )
        export_button.pack(side="right", padx=10, pady=10)
    
    def _edit_cell(self, event, row_idx, col_idx, header, item):
        """Show dialog to edit a cell value"""
        dialog = ctk.CTkInputDialog(
            text=f"Edit {header}",
            title="Edit Cell"
        )
        
        current_value = item.get(header, "")
        result = dialog.get_input()
        
        if result is not None and result != current_value:
            # Update local data
            item[header] = result
            
            # Update the display
            cell_frame = event.widget
            for widget in cell_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text=result)
            
            # Update the Word document
            self._update_document_cell(item["_row"], header, result)
    
    def _update_document_cell(self, row_idx, header, new_value):
        """Update a cell in the Word document"""
        def update_cell():
            try:
                # Open the document
                opened = self.word_handler.open_document()
                if not opened:
                    self.after(0, lambda: self._show_error("Could not open Word document for updating."))
                    return
                
                # Get the table and column index
                if self.current_view == "movies":
                    table = self.word_handler.doc.Tables(MOVIE_TABLE_INDEX)
                    
                    # Find column index for the header
                    col_idx = 1  # Default
                    for i in range(1, table.Columns.Count + 1):
                        cell_text = table.Cell(1, i).Range.Text.strip().rstrip('\r\a\x07')
                        if cell_text == header:
                            col_idx = i
                            break
                else:
                    table = self.word_handler.doc.Tables(SERIES_TABLE_INDEX)
                    
                    # Find column index for the header
                    col_idx = 1  # Default
                    for i in range(1, table.Columns.Count + 1):
                        cell_text = table.Cell(1, i).Range.Text.strip().rstrip('\r\a\x07')
                        if cell_text == header:
                            col_idx = i
                            break
                
                # Update the cell
                table.Cell(row_idx, col_idx).Range.Text = new_value
                
                # Save and close document
                self.word_handler.close_document(save=True)
                
                # Show success message
                self.after(0, lambda: self._show_message("Cell updated successfully.", "Success"))
                
            except Exception as e:
                print(f"Error updating cell: {e}")
                self.after(0, lambda: self._show_error(f"Error updating cell: {e}"))
                
                # Make sure document is closed even on error
                try:
                    self.word_handler.close_document(save=False)
                except:
                    pass
        
        # Run in a separate thread to prevent UI blocking
        threading.Thread(target=update_cell).start()
    
    def _add_new_entry(self):
        """Add a new entry to the table"""
        # This would be a more complex dialog with fields for all columns
        self._show_message("This feature is coming soon!", "Coming Soon")
    
    def _export_to_csv(self):
        """Export the current table to CSV"""
        try:
            data = self.movie_data if self.current_view == "movies" else self.series_data
            
            if not data:
                self._show_error("No data to export.")
                return
            
            # Create DataFrame without internal _row field
            cleaned_data = []
            for item in data:
                row = {k: v for k, v in item.items() if k != "_row"}
                cleaned_data.append(row)
                
            df = pd.DataFrame(cleaned_data)
            
            # Get save path
            file_type = "movie" if self.current_view == "movies" else "series"
            save_path = f"{file_type}_export.csv"
            
            # Save to CSV
            df.to_csv(save_path, index=False)
            
            self._show_message(f"Data exported to {save_path}", "Export Complete")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            self._show_error(f"Error exporting to CSV: {e}")
    
    def _show_error(self, message):
        """Show an error message"""
        dialog = ctk.CTkInputDialog(
            text=message,
            title="Error"
        )
        dialog.get_input()
    
    def _show_message(self, message, title="Message"):
        """Show a message dialog"""
        dialog = ctk.CTkInputDialog(
            text=message,
            title=title
        )
        dialog.get_input() 