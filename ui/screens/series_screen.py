import customtkinter as ctk
from typing import List, Dict, Callable, Optional
import os
import json
from pathlib import Path
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO
import datetime
import webbrowser
from movie_fetcher import MovieFetcher
from word_handler import WordHandler
from tkcalendar import Calendar, DateEntry
from tkinter import ttk
import re
from customtkinter.windows.widgets.theme import ThemeManager

class SeriesScreen(ctk.CTkFrame):
    """
    Series screen for the application.
    Displays a clean search interface for finding and adding TV series.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Initialize variables
        self.series_data = []
        self.movie_fetcher = MovieFetcher()
        self.word_handler = WordHandler()
        
        # Load series data
        self.data_file = Path("data/series.json")
        self._load_series()
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI elements for the series screen"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Header title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📺 TV Series",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(side="left", padx=10, pady=10)
        
        # Search frame with icon
        self.search_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color=("#f0f0f0", "#333333"),
            corner_radius=8
        )
        self.search_frame.pack(side="right", padx=10, pady=10, fill="x", expand=True)
        
        # Search icon
        self.search_icon = ctk.CTkLabel(
            self.search_frame,
            text="🔍",
            font=ctk.CTkFont(size=16),
            width=20
        )
        self.search_icon.pack(side="left", padx=(10, 0))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search TV series...",
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.search_entry.bind("<Return>", self._on_search)
        
        # Content frame with search results
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome message
        self.welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.welcome_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        welcome_icon = ctk.CTkLabel(
            self.welcome_frame,
            text="📺",
            font=ctk.CTkFont(size=48)
        )
        welcome_icon.pack(pady=(0, 10))
        
        welcome_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Search for TV series to add to your collection",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_text.pack(pady=5)
        
        instruction_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Type a series name in the search box and press Enter",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        instruction_text.pack(pady=5)
    
    def _load_series(self):
        """Load series from the data file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    self.series_data = json.load(f)
            else:
                # Create directory if it doesn't exist
                self.data_file.parent.mkdir(parents=True, exist_ok=True)
                # Create empty file
                with open(self.data_file, "w") as f:
                    json.dump([], f)
                self.series_data = []
        except Exception as e:
            print(f"Error loading series data: {e}")
            self.series_data = []
    
    def _save_series(self):
        """Save series to the data file"""
        try:
            # Create directory if it doesn't exist
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, "w") as f:
                json.dump(self.series_data, f, indent=2)
        except Exception as e:
            print(f"Error saving series data: {e}")
    
    def _on_search(self, event):
        """Handle search when Enter is pressed"""
        search_text = self.search_entry.get().strip()
        if not search_text:
            return
            
        # Clear previous content
        for widget in self.content_frame.winfo_children():
                widget.destroy()
        
        # Show loading indicator
        loading_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        loading_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text=f"Searching for '{search_text}'...",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        loading_label.pack(pady=10)
        
        # Search online
        def search_series():
            try:
                # Search online
                api_results = self.movie_fetcher.search_media(search_text, "tv")
                
                # Process and display results
                self.after(0, lambda: self._display_search_results(api_results, search_text))
            except Exception as e:
                print(f"Error searching online: {e}")
                self.after(0, lambda: self._show_search_error(str(e)))
                
        # Start the search in a separate thread
        threading.Thread(target=search_series).start()
    
    def _display_search_results(self, results, search_query):
        """Display search results with thumbnails"""
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # If we have no results
        if not results:
            empty_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, padx=20, pady=50)
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text=f"No TV series found for '{search_query}'",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            empty_label.pack(pady=10)
            
            suggestion_label = ctk.CTkLabel(
                empty_frame,
                text="Try a different search term",
                font=ctk.CTkFont(size=14),
                text_color="gray70"
            )
            suggestion_label.pack(pady=5)
            return
        
        # Results heading
        results_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Search Results ({len(results)} found):",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Results grid
        results_grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        results_grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a series card for each result
        for i, series in enumerate(results):
            self._create_series_result_card(results_grid, series, i)
    
    def _create_series_result_card(self, parent, series, index):
        """Create a card for a series search result"""
        # Card frame
        card = ctk.CTkFrame(
            parent, 
            corner_radius=10,
            border_width=1,
            border_color=("lightgray", "gray30")
        )
        card.pack(fill="x", padx=10, pady=5)
        
        # Configure grid
        card.grid_columnconfigure(1, weight=1)
        
        # Make the entire card clickable
        card.bind("<Button-1>", lambda e, s=series: self._show_series_details(s))
        
        # Series poster frame
        poster_frame = ctk.CTkFrame(
            card, 
            width=90, 
            height=135,
            fg_color=("gray90", "gray20")
        )
        poster_frame.grid(row=0, column=0, padx=10, pady=10)
        poster_frame.bind("<Button-1>", lambda e, s=series: self._show_series_details(s))
        
        # If series has poster URL, load it
        poster_url = f"https://image.tmdb.org/t/p/w185{series.get('poster_path')}" if series.get('poster_path') else None
        if poster_url:
            self._load_series_poster(poster_url, poster_frame)
        else:
            # Placeholder text
            poster_label = ctk.CTkLabel(
                poster_frame, 
                text="📺",
                font=ctk.CTkFont(size=32)
            )
            poster_label.place(relx=0.5, rely=0.5, anchor="center")
            poster_label.bind("<Button-1>", lambda e, s=series: self._show_series_details(s))
        
        # Series details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        details_frame.bind("<Button-1>", lambda e, s=series: self._show_series_details(s))
        
        # Title and year
        title = series.get("name", "Unknown")
        year = series.get("first_air_date", "")[:4] if series.get("first_air_date") else ""
        
        title_year = f"{title}"
        if year:
            title_year += f" ({year})"
            
        title_label = ctk.CTkLabel(
            details_frame,
            text=title_year,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")
        title_label.bind("<Button-1>", lambda e, s=series: self._show_series_details(s))
        
        # Overview/description (truncated)
        overview = series.get("overview", "")
        if overview:
            if len(overview) > 150:
                overview = overview[:150] + "..."
                
            overview_label = ctk.CTkLabel(
                details_frame,
                text=overview,
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray70"),
                anchor="w",
                wraplength=400,
                justify="left"
            )
            overview_label.pack(anchor="w", pady=(5, 0))
            overview_label.bind("<Button-1>", lambda e, s=series: self._show_series_details(s))
        
        # Select button
        select_button = ctk.CTkButton(
            details_frame,
            text="View Details",
            width=120,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(weight="bold"),
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9"),
            command=lambda: self._show_series_details(series)
        )
        select_button.pack(anchor="e", pady=(10, 0))
    
    def _load_series_poster(self, url, frame, size=(90, 135)):
        """Load series poster from URL in a separate thread"""
        # Create a flag to track if the frame is destroyed
        frame_alive = True
        frame._poster_loading = True  # Mark this frame as loading a poster
        
        def check_frame_exists():
            # This needs to be called from the main thread
            nonlocal frame_alive
            try:
                frame.winfo_exists()  # Will raise TclError if destroyed
                return True
            except Exception:
                frame_alive = False
                return False
        
        def load_image():
            try:
                response = requests.get(url, timeout=10)
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize(size, Image.LANCZOS)
                
                # Schedule the UI update on the main thread
                def update_ui():
                    if check_frame_exists():
                        try:
                            # Use CTkImage
                            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
                            
                            # Create label with CTkImage
                            img_label = ctk.CTkLabel(frame, text="", image=ctk_img)
                            img_label.place(relx=0.5, rely=0.5, anchor="center")
                            
                            # Keep a reference to prevent garbage collection
                            if not hasattr(frame, "_image_refs"):
                                frame._image_refs = []
                            frame._image_refs.append(ctk_img)
                        except Exception as e:
                            print(f"Error updating UI with image: {e}")
                
                # Schedule UI update on main thread
                self.after(0, update_ui)
                
            except Exception as e:
                print(f"Error loading image: {e}")
                
                # Schedule showing placeholder on main thread
                def show_placeholder():
                    if check_frame_exists():
                        try:
                            # Show placeholder on error
                            placeholder = ctk.CTkLabel(
                                frame, 
                                text="📺",
                                font=ctk.CTkFont(size=32 if size[0] < 100 else 64)
                            )
                            placeholder.place(relx=0.5, rely=0.5, anchor="center")
                        except Exception as placeholder_error:
                            print(f"Error creating placeholder: {placeholder_error}")
                
                self.after(0, show_placeholder)
        
        # Start thread to load image
        threading.Thread(target=load_image).start()
    
    def _show_series_details(self, series):
        """Show the series details in an expanded view"""
        # First fetch full details
        series_id = series.get("id")
        if not series_id:
            self._show_error("Could not fetch series details")
            return
            
        # Show loading dialog
        loading_dialog = ctk.CTkToplevel(self)
        loading_dialog.title("Fetching Details")
        loading_dialog.geometry("300x100")
        loading_dialog.resizable(False, False)
        loading_dialog.transient(self)
        loading_dialog.grab_set()
        
        # Center dialog
        loading_dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - loading_dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - loading_dialog.winfo_height()) // 2
        loading_dialog.geometry(f"+{x}+{y}")
        
        loading_label = ctk.CTkLabel(
            loading_dialog,
            text=f"Fetching details for\n{series.get('name', 'series')}...",
            font=ctk.CTkFont(size=14)
        )
        loading_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        def fetch_details():
            try:
                # Fetch comprehensive details from both TMDB and OMDB APIs
                details = self.movie_fetcher.get_series_details(series_id, include_cast=True, include_external=True)
                
                # Additionally fetch IMDb and RT ratings if available
                if "imdb_id" in details and details["imdb_id"]:
                    omdb_details = self.movie_fetcher.get_omdb_details(details["imdb_id"])
                    if omdb_details:
                        # Add OMDB specific details
                        details["imdb_rating"] = omdb_details.get("imdbRating", "")
                        details["rt_rating"] = omdb_details.get("Ratings", [])
                        # Extract RT rating if available
                        for rating in details["rt_rating"]:
                            if rating.get("Source") == "Rotten Tomatoes":
                                details["rt_rating"] = rating.get("Value", "")
                                break
                        if isinstance(details["rt_rating"], list):
                            details["rt_rating"] = ""
                
                # Get information about upcoming episodes
                if series.get("in_production", False):
                    upcoming_details = self.movie_fetcher.get_series_upcoming_episodes(series_id)
                    if upcoming_details:
                        details.update(upcoming_details)
                
                self.after(0, lambda: self._display_series_details(loading_dialog, series, details))
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Error fetching series details: {e}"))
                self.after(0, loading_dialog.destroy)
        
        # Start the fetch in a separate thread
        threading.Thread(target=fetch_details).start()
    
    def _display_series_details(self, loading_dialog, series, details):
        """Display detailed series information in the main content area"""
        loading_dialog.destroy()
        
        # Save the current search results
        self.last_search_results = []
        for widget in self.content_frame.winfo_children():
            self.last_search_results.append(widget)
            widget.pack_forget()  # Hide but don't destroy
        
        # Add back button at the top of the content frame
        back_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        back_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        back_button = ctk.CTkButton(
            back_frame,
            text="← Back to Results",
            command=self._back_to_results,
            width=150,
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9")
        )
        back_button.pack(side="left")
        
        # Create detail view container
        detail_view = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        detail_view.pack(fill="both", expand=True)
        
        # Create two columns
        left_column = ctk.CTkFrame(detail_view, fg_color="transparent")
        left_column.pack(side="left", fill="both", padx=(0, 20))
        
        right_column = ctk.CTkFrame(detail_view, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True)
        
        # Poster frame in left column
        poster_frame = ctk.CTkFrame(
            left_column, 
            width=300, 
            height=450,
            fg_color=("gray90", "gray20")
        )
        poster_frame.pack(padx=10, pady=10)
        
        # If series has poster URL, load it with higher resolution
        poster_url = f"https://image.tmdb.org/t/p/w500{series.get('poster_path')}" if series.get('poster_path') else None
        if poster_url:
            self._load_series_poster(poster_url, poster_frame, size=(300, 450))
        else:
            # Placeholder text
            poster_label = ctk.CTkLabel(
                poster_frame, 
                text="📺",
                font=ctk.CTkFont(size=64)
            )
            poster_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Action buttons
        action_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        add_button = ctk.CTkButton(
            action_frame,
            text="Add to Collection",
            command=lambda: self._show_series_add_dialog(None, series, details),
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_button.pack(fill="x", padx=5, pady=5)
        
        # IMDb link if available
        if "imdb_id" in details and details["imdb_id"]:
            imdb_button = ctk.CTkButton(
                action_frame,
                text="Visit IMDb Page",
                command=lambda: webbrowser.open(f"https://www.imdb.com/title/{details['imdb_id']}"),
                fg_color="#f5c518",
                text_color="black",
                hover_color="#d4a700",
                height=40,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            imdb_button.pack(fill="x", padx=5, pady=5)
        
        # Status indicator for series
        status_indicator = None
        if "status" in details:
            status_text = details.get("status", "")
            if status_text:
                status_color = "#32CD32"  # Green for ongoing/returning
                if status_text.lower() == "ended":
                    status_color = "gray70"
                elif status_text.lower() == "canceled":
                    status_color = "#FF6347"  # Red for canceled
                
                status_frame = ctk.CTkFrame(
                    action_frame,
                    fg_color=status_color,
                    corner_radius=5,
                    height=40
                )
                status_frame.pack(fill="x", padx=5, pady=5)
                
                status_indicator = ctk.CTkLabel(
                    status_frame,
                    text=f"Status: {status_text}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white" if status_text.lower() != "ended" else "black",
                    padx=8,
                    pady=2
                )
                status_indicator.pack(pady=5)
        
        # Series details in right column
        # Title and year
        title = series.get("name", "Unknown")
        year = series.get("first_air_date", "")[:4] if series.get("first_air_date") else ""
        
        title_text = title
        if year:
            title_text += f" ({year})"
            
        title_label = ctk.CTkLabel(
            right_column,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold"),
            wraplength=500,
            justify="left"
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Network if available
        if "network" in details and details["network"]:
            network_label = ctk.CTkLabel(
                right_column,
                text=details["network"],
                font=ctk.CTkFont(size=16),
                text_color=("gray40", "gray70")
            )
            network_label.pack(anchor="w", pady=(0, 15))
        
        # Ratings display
        if "imdb_rating" in details or "rt_rating" in details:
            ratings_frame = ctk.CTkFrame(right_column, fg_color="transparent")
            ratings_frame.pack(fill="x", pady=(0, 15))
            
            if "imdb_rating" in details and details["imdb_rating"]:
                imdb_frame = ctk.CTkFrame(
                    ratings_frame,
                    fg_color=("#f5c518", "#f5c518"),  # IMDb yellow
                    corner_radius=5
                )
                imdb_frame.pack(side="left", padx=(0, 10))
                
                # Ensure IMDb rating has the right format
                imdb_value = details["imdb_rating"]
                if "/10" not in imdb_value:
                    imdb_value = f"{imdb_value}/10"
                
                imdb_label = ctk.CTkLabel(
                    imdb_frame,
                    text=f"IMDb: {imdb_value}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="black",
                    padx=8,
                    pady=2
                )
                imdb_label.pack()
            
            if "rt_rating" in details and details["rt_rating"]:
                # Determine color based on RT rating
                rt_value = details["rt_rating"]
                # Extract percentage if it's a string like "75%"
                rt_percentage = 0
                if isinstance(rt_value, str):
                    rt_percentage_match = re.search(r'(\d+)', rt_value)
                    if rt_percentage_match:
                        rt_percentage = int(rt_percentage_match.group(1))
                
                rt_color = "#fa320a" if rt_percentage >= 60 else "#76b900"  # Red for fresh, green for rotten
                
                # Ensure RT value has % symbol
                if "%" not in rt_value and rt_value:
                    rt_value = f"{rt_value}%"
                
                rt_frame = ctk.CTkFrame(
                    ratings_frame,
                    fg_color=(rt_color, rt_color),
                    corner_radius=5
                )
                rt_frame.pack(side="left")
                
                rt_label = ctk.CTkLabel(
                    rt_frame,
                    text=f"RT: {rt_value}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white",
                    padx=8,
                    pady=2
                )
                rt_label.pack()
        
        # Info grid: seasons, episodes, genres, creator, release date
        info_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))
        info_frame.grid_columnconfigure(1, weight=1)
        
        info_row = 0
        
        # Seasons and episodes
        if "number_of_seasons" in details and "number_of_episodes" in details:
            seasons_label = ctk.CTkLabel(
                info_frame,
                text="Seasons/Episodes:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            seasons_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            seasons_value = ctk.CTkLabel(
                info_frame,
                text=f"{details['number_of_seasons']} Seasons, {details['number_of_episodes']} Episodes",
                anchor="w"
            )
            seasons_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
            
        # Genres
        if "genres" in details and details["genres"]:
            genre_label = ctk.CTkLabel(
                info_frame,
                text="Genres:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            genre_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            genre_value = ctk.CTkLabel(
                info_frame,
                text=details["genres"],
                anchor="w",
                wraplength=400,
                justify="left"
            )
            genre_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
            
        # Creator/Director
        if "creator" in details and details["creator"]:
            creator_label = ctk.CTkLabel(
                info_frame,
                text="Creator:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            creator_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            creator_value = ctk.CTkLabel(
                info_frame,
                text=details["creator"],
                anchor="w",
                wraplength=400,
                justify="left"
            )
            creator_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
            
        # Cast members
        if "cast" in details and details["cast"]:
            cast_label = ctk.CTkLabel(
                info_frame,
                text="Main Cast:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            cast_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            cast_value = ctk.CTkLabel(
                info_frame,
                text=details["cast"],
                anchor="w",
                wraplength=400,
                justify="left"
            )
            cast_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
            
        # First air date
        if "first_air_date" in details and details["first_air_date"]:
            air_date_label = ctk.CTkLabel(
                info_frame,
                text="First Air Date:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            air_date_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            air_date_value = ctk.CTkLabel(
                info_frame,
                text=details["first_air_date"],
                anchor="w"
            )
            air_date_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
            
        # Last episode info
        if "last_episode" in details and details["last_episode"]:
            last_ep_label = ctk.CTkLabel(
                info_frame,
                text="Last Episode:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            last_ep_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            last_ep_value = ctk.CTkLabel(
                info_frame,
                text=details["last_episode"],
                anchor="w",
                wraplength=400,
                justify="left"
            )
            last_ep_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
            
        # Separators are helpful for visual organization
        if "upcoming_episode" in details and details["upcoming_episode"]:
            # Add separator
            separator = ttk.Separator(info_frame, orient="horizontal")
            separator.grid(row=info_row, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 15))
            info_row += 1
            
        # Upcoming episode info
        if "upcoming_episode" in details and details["upcoming_episode"]:
            # Create a special highlighted frame for upcoming episode
            upcoming_frame = ctk.CTkFrame(
                right_column,
                corner_radius=10,
                border_width=1,
                border_color=("#4a86e8", "#2d5bb9"),
                fg_color=("gray95", "gray15")
            )
            upcoming_frame.pack(fill="x", pady=(0, 15), padx=5)
            
            # Header with icon
            upcoming_header = ctk.CTkFrame(
                upcoming_frame,
                corner_radius=8,
                fg_color=("#4CAF50", "#4CAF50"),  # Green color for better visibility
            )
            upcoming_header.pack(fill="x", padx=0, pady=0)
            
            header_label = ctk.CTkLabel(
                upcoming_header,
                text="📅 Upcoming Episode",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=8)
            
            # Episode details
            upcoming_content = ctk.CTkFrame(upcoming_frame, fg_color="transparent")
            upcoming_content.pack(fill="x", padx=15, pady=10)
            
            # Title and code
            ep_title_parts = details["upcoming_episode"].split(":")
            if len(ep_title_parts) > 1:
                ep_code = ep_title_parts[0].strip()
                ep_title = ep_title_parts[1].split("(")[0].strip()
                
                code_label = ctk.CTkLabel(
                    upcoming_content,
                    text=ep_code,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                code_label.pack(anchor="w", pady=(0, 5))
                
                title_label = ctk.CTkLabel(
                    upcoming_content,
                    text=f'"{ep_title}"',
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                title_label.pack(anchor="w", pady=(0, 5))
            else:
                # Fallback if format is different
                title_label = ctk.CTkLabel(
                    upcoming_content,
                    text=details["upcoming_episode"],
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                title_label.pack(anchor="w", pady=(0, 5))
            
            # Air date with countdown
            if "upcoming_date" in details and details["upcoming_date"]:
                try:
                    # Parse date and calculate days remaining
                    today = datetime.datetime.now().date()
                    air_date = datetime.datetime.strptime(details["upcoming_date"], "%b %d, %Y").date()
                    days_remaining = (air_date - today).days
                    
                    # Create a frame for the date info
                    date_frame = ctk.CTkFrame(upcoming_content, fg_color="transparent")
                    date_frame.pack(fill="x", pady=(5, 0))
                    
                    # Air date display
                    date_label = ctk.CTkLabel(
                        date_frame,
                        text=f"Airs on {details['upcoming_date']}",
                        font=ctk.CTkFont(size=14),
                        text_color=("gray50", "gray70")
                    )
                    date_label.pack(side="left", anchor="w")
                    
                    # Countdown display with appropriate colors
                    if days_remaining > 0:
                        countdown_text = f"{days_remaining} days remaining"
                        if days_remaining <= 7:
                            countdown_color = "#FF9800"  # Orange for soon
                        else:
                            countdown_color = "#4CAF50"  # Green for further away
                    elif days_remaining == 0:
                        countdown_text = "Airing today!"
                        countdown_color = "#F44336"  # Red for today
                    else:
                        countdown_text = "Already aired"
                        countdown_color = "#9E9E9E"  # Gray for past
                    
                    countdown_frame = ctk.CTkFrame(
                        date_frame,
                        fg_color=countdown_color,
                        corner_radius=5
                    )
                    countdown_frame.pack(side="right", padx=(10, 0))
                    
                    countdown_label = ctk.CTkLabel(
                        countdown_frame,
                        text=countdown_text,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="white",
                        padx=8,
                        pady=2
                    )
                    countdown_label.pack()
                    
                except Exception as e:
                    print(f"Error calculating days: {e}")
                    # Fallback if date parsing fails
                    date_label = ctk.CTkLabel(
                        upcoming_content,
                        text=f"Airs on {details['upcoming_date']}",
                        font=ctk.CTkFont(size=14),
                        text_color=("gray50", "gray70")
                    )
                    date_label.pack(anchor="w", pady=(0, 5))

        # Add a nice overview separator
        separator = ctk.CTkFrame(right_column, height=1, fg_color="gray70")
        separator.pack(fill="x", pady=10)

        # Overview
        if "overview" in series and series["overview"]:
            overview_label = ctk.CTkLabel(
                right_column,
                text="Overview:",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            )
            overview_label.pack(anchor="w", pady=(0, 5))
            
            overview_text = ctk.CTkLabel(
                right_column,
                text=series["overview"],
                font=ctk.CTkFont(size=14),
                wraplength=500,
                justify="left"
            )
            overview_text.pack(anchor="w", pady=(0, 15))
    
    def _back_to_results(self):
        """Return to search results view"""
        # Clear the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Add back the search results
        if hasattr(self, 'last_search_results') and self.last_search_results:
            for widget in self.last_search_results:
                widget.pack(fill="x", padx=10, pady=5)
        else:
            self._create_ui()  # Recreate the welcome view
    
    def _show_series_add_dialog(self, loading_dialog, series, details):
        """Show dialog to add series with watch info and rating"""
        if loading_dialog:
            loading_dialog.destroy()
        
        # Ensure clean start by destroying any existing dialogs
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                try:
                    widget.destroy()
                except:
                    pass
        
        # Prepare data for the dialog
        dialog_data = series.copy()
        
        # Add details to dialog data
        if details:
            # Ensure we have genres in a format the dialog expects
            if "genres" in details and isinstance(details["genres"], str):
                dialog_data["genres"] = [g.strip() for g in details["genres"].split(",")]
            elif "genres" in details:
                dialog_data["genres"] = details["genres"]
            
            # Add key information from details
            for key in ["number_of_seasons", "number_of_episodes", "imdb_rating", "rt_rating", "first_air_date", 
                       "creator", "cast", "status", "network"]:
                if key in details:
                    dialog_data[key] = details[key]
        
        # Create and show dialog with proper styling
        dialog = SeriesAddDialog(self, dialog_data, self.word_handler)
        
        # Make sure dialog comes to front
        dialog.focus_force()
        dialog.lift()
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # If series was added, refresh the view
        if hasattr(dialog, "result") and dialog.result:
            # Add the series to data
            self.series_data.append(dialog.result)
            self._save_series()
            
            # Go back to results or welcome screen (don't show popup)
            self._back_to_results()
    
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
    
    def _show_search_error(self, error):
        """Show search error and reset to welcome screen"""
        self._show_error(f"Error searching: {error}")
        
        # Clear content frame and recreate welcome message
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        self.welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.welcome_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        welcome_icon = ctk.CTkLabel(
            self.welcome_frame,
            text="📺",
            font=ctk.CTkFont(size=48)
        )
        welcome_icon.pack(pady=(0, 10))
        
        welcome_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Search for TV series to add to your collection",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_text.pack(pady=5)
        
        instruction_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Type a series name in the search box and press Enter",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        instruction_text.pack(pady=5)


class SeriesAddDialog(ctk.CTkToplevel):
    """Dialog for adding a series"""
    
    def __init__(self, parent, series_data, word_handler=None):
        super().__init__(parent)
        
        self.parent = parent
        self.series_data = series_data
        self.word_handler = word_handler
        self.result = None
        
        # Configure the dialog
        self.title("Add Series")
        self.geometry("850x600")
        self.resizable(False, False)
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Create UI
        self._create_ui()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def _create_ui(self):
        """Create the UI elements"""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create left and right frames
        left_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", padx=(0, 10))
        
        right_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Left side - Poster and buttons
        poster_frame = ctk.CTkFrame(left_frame, width=300, height=450)
        poster_frame.pack(pady=(0, 15))
        poster_frame.pack_propagate(False)
        
        # Load and display poster
        if self.series_data.get("poster_path"):
            poster_image = self._load_poster(self.series_data["poster_path"], size=(300, 450))
            if poster_image:
                poster_label = ctk.CTkLabel(poster_frame, text="", image=poster_image)
                poster_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Placeholder text if no poster available
                placeholder = ctk.CTkLabel(
                    poster_frame, 
                    text="📺",
                    font=ctk.CTkFont(size=64)
                )
                placeholder.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Placeholder text if no poster available
            placeholder = ctk.CTkLabel(
                poster_frame, 
                text="📺",
                font=ctk.CTkFont(size=64)
            )
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        # Save to Word button
        save_to_word_button = ctk.CTkButton(
            left_frame,
            text="Save to Word",
            command=self._save_to_word,
            height=40,
            fg_color=("#4a86e8", "#2d5bb9"),  # Blue color similar to accent
            hover_color=("#3a76d8", "#1d4ba9")  # Slightly darker shade for hover
        )
        save_to_word_button.pack(fill="x", pady=(0, 10))
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            left_frame,
            text="Cancel",
            command=self.destroy,
            height=40,
            fg_color=("#e0e0e0", "#444444"),  # Gray colors for button
            hover_color=("#cccccc", "#333333"),  # Darker gray for hover
            text_color=("black", "white")  # Text color based on theme
        )
        cancel_button.pack(fill="x")
        
        # Right side - Series information
        # Title
        series_name = self.series_data.get("name", "Unknown Series")
        title_label = ctk.CTkLabel(
            right_frame,
            text=series_name,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Series Info section
        info_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        info_container.pack(fill="both", expand=True)
        
        # Basic info
        basic_info_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        basic_info_frame.pack(fill="x", pady=(0, 15))
        
        # Format runtime, genre, release date in a clean layout
        if "number_of_seasons" in self.series_data:
            seasons_text = f"{self.series_data['number_of_seasons']} Seasons"
        else:
            seasons_text = ""
            
        if "number_of_episodes" in self.series_data:
            episodes_text = f"{self.series_data['number_of_episodes']} Episodes"
        else:
            episodes_text = ""
            
        if "genres" in self.series_data:
            if isinstance(self.series_data["genres"], list):
                genres_text = "/".join(self.series_data["genres"])
            else:
                genres_text = self.series_data["genres"]
        else:
            genres_text = ""
            
        if "first_air_date" in self.series_data:
            first_air_date_text = self.series_data["first_air_date"]
        else:
            first_air_date_text = ""
        
        # Display seasons/episodes
        if seasons_text:
            seasons_label = ctk.CTkLabel(basic_info_frame, text="Seasons:", width=120, anchor="e")
            seasons_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
            
            self.season_entry = ctk.CTkEntry(basic_info_frame, width=150)
            self.season_entry.grid(row=0, column=1, sticky="w", pady=(0, 5), padx=(10, 0))
            self.season_entry.insert(0, str(self.series_data.get("number_of_seasons", "")))
        
        if episodes_text:
            episodes_label = ctk.CTkLabel(basic_info_frame, text="Episodes:", width=120, anchor="e")
            episodes_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
            
            self.episode_entry = ctk.CTkEntry(basic_info_frame, width=150)
            self.episode_entry.grid(row=1, column=1, sticky="w", pady=(0, 5), padx=(10, 0))
            self.episode_entry.insert(0, str(self.series_data.get("number_of_episodes", "")))
        
        # Genres
        genres_label = ctk.CTkLabel(basic_info_frame, text="Genres:", width=120, anchor="e")
        genres_label.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.genre_entry = ctk.CTkEntry(basic_info_frame, width=350)
        self.genre_entry.grid(row=2, column=1, sticky="w", pady=(0, 5), padx=(10, 0))
        self.genre_entry.insert(0, genres_text)
        
        # First air date
        first_air_date_label = ctk.CTkLabel(basic_info_frame, text="First Air Date:", width=120, anchor="e")
        first_air_date_label.grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        self.first_air_entry = ctk.CTkEntry(basic_info_frame, width=150)
        self.first_air_entry.grid(row=3, column=1, sticky="w", pady=(0, 5), padx=(10, 0))
        self.first_air_entry.insert(0, first_air_date_text)
        
        # Create hidden entries for IMDb and RT ratings
        self.imdb_entry = ctk.CTkEntry(basic_info_frame)
        self.rt_entry = ctk.CTkEntry(basic_info_frame)
        
        # Display IMDb and RT ratings with badges
        ratings_frame = ctk.CTkFrame(basic_info_frame, fg_color="transparent")
        ratings_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        # IMDb rating badge
        if "imdb_rating" in self.series_data and self.series_data["imdb_rating"]:
            imdb_value = self.series_data["imdb_rating"].replace("/10", "")
            
            imdb_frame = ctk.CTkFrame(
                ratings_frame,
                fg_color=("#f5c518", "#f5c518"),  # IMDb yellow
                corner_radius=5
            )
            imdb_frame.pack(side="left", padx=(0, 10))
            
            imdb_label = ctk.CTkLabel(
                imdb_frame,
                text=f"IMDb: {imdb_value}/10",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="black",
                padx=8,
                pady=2
            )
            imdb_label.pack()
            
            # Store IMDb rating in hidden entry
            self.imdb_entry.insert(0, imdb_value)
        else:
            # Default IMDb rating
            self.imdb_entry.insert(0, "")
            
            # Show a gray IMDb badge
            imdb_frame = ctk.CTkFrame(
                ratings_frame,
                fg_color=("#f5c518", "#f5c518"),  # IMDb yellow
                corner_radius=5
            )
            imdb_frame.pack(side="left", padx=(0, 10))
            
            imdb_label = ctk.CTkLabel(
                imdb_frame,
                text="IMDb: N/A",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="black",
                padx=8,
                pady=2
            )
            imdb_label.pack()
        
        # RT rating badge
        if "rt_rating" in self.series_data and self.series_data["rt_rating"]:
            rt_value = self.series_data["rt_rating"]
            rt_number = "".join(filter(str.isdigit, rt_value))
            rt_percentage = int(rt_number) if rt_number else 0
            
            # Red for fresh (≥60%), green for rotten (<60%)
            rt_color = "#fa320a" if rt_percentage >= 60 else "#76b900"
            
            # Ensure RT value has % symbol
            if "%" not in rt_value:
                rt_value = f"{rt_value}%"
            
            rt_frame = ctk.CTkFrame(
                ratings_frame,
                fg_color=(rt_color, rt_color),
                corner_radius=5
            )
            rt_frame.pack(side="left")
            
            rt_label = ctk.CTkLabel(
                rt_frame,
                text=f"RT: {rt_value}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white",
                padx=8,
                pady=2
            )
            rt_label.pack()
            
            # Store RT rating in hidden entry
            self.rt_entry.insert(0, rt_value)
        else:
            # Default RT rating
            self.rt_entry.insert(0, "")
            
            # Show a default RT badge
            rt_frame = ctk.CTkFrame(
                ratings_frame,
                fg_color=("#fa320a", "#fa320a"),  # RT red color
                corner_radius=5
            )
            rt_frame.pack(side="left")
            
            rt_label = ctk.CTkLabel(
                rt_frame,
                text="RT: N/A",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white",
                padx=8,
                pady=2
            )
            rt_label.pack()
        
        # Add separator
        separator = ctk.CTkFrame(info_container, height=1, fg_color="gray70")
        separator.pack(fill="x", pady=15)
        
        # Add Series Details title
        details_title = ctk.CTkLabel(
            info_container,
            text="Add Series Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        details_title.pack(anchor="w", pady=(0, 15))
        
        # Watch Information section
        watch_info_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        watch_info_frame.pack(fill="x", pady=5)
        
        # Start Date section
        start_date_label = ctk.CTkLabel(
            watch_info_frame, 
            text="When did you start watching this series?",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        start_date_label.pack(anchor="w", pady=(0, 5))
        
        # Start date options frame
        start_date_options = ctk.CTkFrame(watch_info_frame, fg_color="transparent")
        start_date_options.pack(fill="x", pady=(0, 10))
        
        self.start_date_var = ctk.StringVar(value="today")
        
        start_today_radio = ctk.CTkRadioButton(
            start_date_options,
            text="Today",
            variable=self.start_date_var,
            value="today",
            command=self._toggle_start_date_option
        )
        start_today_radio.pack(side="left", padx=(0, 15))
        
        start_custom_radio = ctk.CTkRadioButton(
            start_date_options,
            text="Custom date:",
            variable=self.start_date_var,
            value="custom",
            command=self._toggle_start_date_option
        )
        start_custom_radio.pack(side="left", padx=(0, 15))
        
        start_unknown_radio = ctk.CTkRadioButton(
            start_date_options,
            text="Don't Know/N/A",
            variable=self.start_date_var,
            value="unknown",
            command=self._toggle_start_date_option
        )
        start_unknown_radio.pack(side="left")
        
        # Start date calendar frame
        self.start_calendar_frame = ctk.CTkFrame(watch_info_frame)
        self.start_calendar_frame.pack(fill="x", pady=(0, 10))
        
        # Configure calendar with proper theming
        if ctk.get_appearance_mode().lower() == "dark":
            self.start_calendar = Calendar(
                self.start_calendar_frame, 
                selectmode="day",
                date_pattern="yyyy-mm-dd",
                background="#2b2b2b",
                foreground="#DCE4EE",
                bordercolor="#565B5E",
                headersbackground="#1f1f1f",
                headersforeground="#DCE4EE",
                selectbackground="#3a646e",
                selectforeground="white",
                normalbackground="#2b2b2b",
                normalforeground="#DCE4EE",
                weekendbackground="#262626",
                weekendforeground="#DCE4EE",
                othermonthbackground="#1f1f1f",
                othermonthforeground="gray60"
            )
        else:
            self.start_calendar = Calendar(
                self.start_calendar_frame, 
                selectmode="day",
                date_pattern="yyyy-mm-dd",
                background="white",
                foreground="black",
                bordercolor="#cccccc",
                headersbackground="#f0f0f0",
                headersforeground="black",
                selectbackground="#5cafdf",
                selectforeground="white",
                normalbackground="white",
                normalforeground="black",
                weekendbackground="#f0f0f0",
                weekendforeground="black",
                othermonthbackground="#f5f5f5",
                othermonthforeground="gray60"
            )
            
        self.start_calendar.pack(padx=10, pady=10)
        self.start_calendar_frame.pack_forget()  # Hide initially
        
        # Finish Date section
        finish_date_label = ctk.CTkLabel(
            watch_info_frame, 
            text="When did you finish watching this series?",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        finish_date_label.pack(anchor="w", pady=(10, 5))
        
        # Finish date options frame
        finish_date_options = ctk.CTkFrame(watch_info_frame, fg_color="transparent")
        finish_date_options.pack(fill="x", pady=(0, 10))
        
        self.finish_date_var = ctk.StringVar(value="today")
        
        finish_today_radio = ctk.CTkRadioButton(
            finish_date_options,
            text="Today",
            variable=self.finish_date_var,
            value="today",
            command=self._toggle_finish_date_option
        )
        finish_today_radio.pack(side="left", padx=(0, 15))
        
        finish_custom_radio = ctk.CTkRadioButton(
            finish_date_options,
            text="Custom date:",
            variable=self.finish_date_var,
            value="custom",
            command=self._toggle_finish_date_option
        )
        finish_custom_radio.pack(side="left", padx=(0, 15))
        
        finish_unknown_radio = ctk.CTkRadioButton(
            finish_date_options,
            text="Don't Know/N/A",
            variable=self.finish_date_var,
            value="unknown",
            command=self._toggle_finish_date_option
        )
        finish_unknown_radio.pack(side="left")
        
        # Coming season info frame (shown when finish_date is unknown)
        self.coming_season_frame = ctk.CTkFrame(watch_info_frame, fg_color="transparent")
        self.coming_season_frame.pack(fill="x", pady=(0, 10))
        
        coming_season_label = ctk.CTkLabel(
            self.coming_season_frame,
            text="Coming season year (if known):",
            width=180,
            anchor="e"
        )
        coming_season_label.pack(side="left", padx=(0, 10))
        
        self.coming_season_entry = ctk.CTkEntry(
            self.coming_season_frame,
            width=100,
            placeholder_text="e.g. 2025"
        )
        self.coming_season_entry.pack(side="left")
        
        self.coming_season_frame.pack_forget()  # Hide initially
        
        # Finish date calendar frame
        self.finish_calendar_frame = ctk.CTkFrame(watch_info_frame)
        self.finish_calendar_frame.pack(fill="x", pady=(0, 10))
        
        # Configure calendar with proper theming
        if ctk.get_appearance_mode().lower() == "dark":
            self.finish_calendar = Calendar(
                self.finish_calendar_frame, 
                selectmode="day",
                date_pattern="yyyy-mm-dd",
                background="#2b2b2b",
                foreground="#DCE4EE",
                bordercolor="#565B5E",
                headersbackground="#1f1f1f",
                headersforeground="#DCE4EE",
                selectbackground="#3a646e",
                selectforeground="white",
                normalbackground="#2b2b2b",
                normalforeground="#DCE4EE",
                weekendbackground="#262626",
                weekendforeground="#DCE4EE",
                othermonthbackground="#1f1f1f",
                othermonthforeground="gray60"
            )
        else:
            self.finish_calendar = Calendar(
                self.finish_calendar_frame, 
                selectmode="day",
                date_pattern="yyyy-mm-dd",
                background="white",
                foreground="black",
                bordercolor="#cccccc",
                headersbackground="#f0f0f0",
                headersforeground="black",
                selectbackground="#5cafdf",
                selectforeground="white",
                normalbackground="white",
                normalforeground="black",
                weekendbackground="#f0f0f0",
                weekendforeground="black",
                othermonthbackground="#f5f5f5",
                othermonthforeground="gray60"
            )
            
        self.finish_calendar.pack(padx=10, pady=10)
        self.finish_calendar_frame.pack_forget()  # Hide initially
        
        # Rating section
        rating_label = ctk.CTkLabel(
            watch_info_frame, 
            text="Your Rating:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        rating_label.pack(anchor="w", pady=(10, 5))
        
        # Rating controls
        rating_control_frame = ctk.CTkFrame(watch_info_frame, fg_color="transparent")
        rating_control_frame.pack(fill="x", pady=(0, 10))
        
        # Minus button
        minus_button = ctk.CTkButton(
            rating_control_frame,
            text="-",
            width=30,
            height=30,
            command=self._decrease_rating
        )
        minus_button.pack(side="left")
        
        # Rating slider
        self.rating_slider = ctk.CTkSlider(
            rating_control_frame,
            from_=0,
            to=10,
            number_of_steps=100,
            width=350
        )
        self.rating_slider.pack(side="left", padx=10)
        self.rating_slider.set(8.0)  # Default to 8.0
        self.rating_slider.configure(command=self._update_rating_label)
        
        # Plus button
        plus_button = ctk.CTkButton(
            rating_control_frame,
            text="+",
            width=30,
            height=30,
            command=self._increase_rating
        )
        plus_button.pack(side="left")
        
        # Rating display
        self.rating_display = ctk.CTkLabel(
            rating_control_frame,
            text="8.0/10",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.rating_display.pack(side="left", padx=10)
        
        # Success and error message frames at the bottom of right_frame
        self.success_frame = ctk.CTkFrame(
            right_frame, 
            fg_color="#4CAF50",  # Green color
            corner_radius=5,
            height=40
        )
        self.success_frame.pack(fill="x", pady=(15, 0))
        self.success_frame.pack_propagate(False)
        
        self.success_label = ctk.CTkLabel(
            self.success_frame, 
            text="✓ Series saved to Word successfully!",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.success_label.place(relx=0.5, rely=0.5, anchor="center")
        self.success_frame.pack_forget()  # Hide initially
        
        self.error_frame = ctk.CTkFrame(
            right_frame, 
            fg_color="#F44336",  # Red color
            corner_radius=5,
            height=40
        )
        self.error_frame.pack(fill="x", pady=(15, 0))
        self.error_frame.pack_propagate(False)
        
        self.error_label = ctk.CTkLabel(
            self.error_frame, 
            text="Error saving series to Word!",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.error_label.place(relx=0.5, rely=0.5, anchor="center")
        self.error_frame.pack_forget()  # Hide initially

    def _load_poster(self, poster_path, size=(150, 225)):
        """Load a poster image with specified size"""
        if not poster_path:
            return None
            
        try:
            img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            response = requests.get(img_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            
            # Resize to the specified size
            img = img.resize(size, Image.LANCZOS)
            
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"Error loading poster: {e}")
            return None

    def _toggle_start_date_option(self):
        """Toggle the start date calendar"""
        if self.start_date_var.get() == "custom":
            self.start_calendar_frame.pack(fill="x", pady=(0, 10))
        else:
            self.start_calendar_frame.pack_forget()

    def _toggle_finish_date_option(self):
        """Toggle the finish date calendar and coming season field"""
        if self.finish_date_var.get() == "custom":
            self.finish_calendar_frame.pack(fill="x", pady=(0, 10))
            self.coming_season_frame.pack_forget()
        elif self.finish_date_var.get() == "unknown":
            self.finish_calendar_frame.pack_forget()
            self.coming_season_frame.pack(fill="x", pady=(0, 10))
        else:
            self.finish_calendar_frame.pack_forget()
            self.coming_season_frame.pack_forget()

    def _get_appearance_mode(self):
        """Get the current appearance mode"""
        return ctk.get_appearance_mode().lower()

    def _update_rating_label(self, value=None):
        """Update the rating label with the current slider value"""
        if value is None:
            value = self.rating_slider.get()
        self.rating_display.configure(text=f"{value:.1f}/10")

    def _increase_rating(self):
        """Increase the rating by 0.25"""
        current_value = self.rating_slider.get()
        new_value = min(10, current_value + 0.25)
        self.rating_slider.set(new_value)
        self._update_rating_label(new_value)

    def _decrease_rating(self):
        """Decrease the rating by 0.25"""
        current_value = self.rating_slider.get()
        new_value = max(0, current_value - 0.25)
        self.rating_slider.set(new_value)
        self._update_rating_label(new_value)

    def _format_start_date(self):
        """Format the start date based on the selected option"""
        if self.start_date_var.get() == "today":
            return datetime.datetime.now().strftime("%b %d, %Y")
        elif self.start_date_var.get() == "custom":
            selected_date = self.start_calendar.get_date()
            try:
                date_obj = datetime.datetime.strptime(selected_date, "%Y-%m-%d")
                return date_obj.strftime("%b %d, %Y")  # Format as "Apr 19, 2025"
            except:
                return selected_date
        else:  # Unknown/N/A
            return ""

    def _format_finish_date(self):
        """Format the finish date based on the selected option"""
        if self.finish_date_var.get() == "today":
            return datetime.datetime.now().strftime("%b %d, %Y")
        elif self.finish_date_var.get() == "custom":
            selected_date = self.finish_calendar.get_date()
            try:
                date_obj = datetime.datetime.strptime(selected_date, "%Y-%m-%d")
                return date_obj.strftime("%b %d, %Y")  # Format as "Apr 19, 2025"
            except:
                return selected_date
        else:  # Unknown/N/A
            return ""

    def _save_to_word(self):
        """Save the series to a Word document"""
        try:
            # Get values from form
            start_date = self._format_start_date()
            finish_date = self._format_finish_date()
            user_rating = self.rating_slider.get()
            coming_season = self.coming_season_entry.get().strip() if self.finish_date_var.get() == "unknown" else ""
            
            # Check if required fields are filled
            if not self.season_entry.get().strip() or not self.episode_entry.get().strip():
                raise ValueError("Season and episode count are required")
            
            # Format the user rating with "/10"
            formatted_user_rating = f"{user_rating:.1f}/10"
            
            # Prepare data for Word
            word_data = {
                "title": self.series_data.get("name", ""),
                "season": self.season_entry.get().strip(),
                "episodes": self.episode_entry.get().strip(),
                "genres": self.genre_entry.get().strip(),
                "first_air_date": self.first_air_entry.get().strip(),
                "start_date": start_date,
                "finish_date": finish_date,
                "user_rating": formatted_user_rating,
                "imdb_rating": self.imdb_entry.get().strip(),
                "rt_rating": self.rt_entry.get().strip(),
                "finished": finish_date != "",  # Finished if finish date is provided
                "coming_season": coming_season,  # Add coming season info
                "overview": self.series_data.get("overview", "")
            }
            
            # Add to Word document
            if self.word_handler:
                # Always open a new document connection
                self.word_handler.open_document()
                
                # Add series to document
                success = self.word_handler.add_series(word_data)
                
                if success:
                    # Show success message
                    self.error_frame.pack_forget()
                    self.success_frame.pack(fill="x", pady=(15, 0))
                    
                    # Store result for parent to know it was successful
                    self.result = word_data
                    
                    # Close the dialog after 3 seconds
                    self.after(3000, self.destroy)
                else:
                    # Show error message for failed save
                    self.success_frame.pack_forget()
                    self.error_label.configure(text="Error saving to Word document")
                    self.error_frame.pack(fill="x", pady=(15, 0))
            else:
                raise ValueError("Word handler not available")
                
        except ValueError as e:
            # Show specific error message for validation errors
            self.success_frame.pack_forget()
            self.error_label.configure(text=f"Error: {str(e)}")
            self.error_frame.pack(fill="x", pady=(15, 0))
        except Exception as e:
            # Show error message for other errors
            self.success_frame.pack_forget()
            self.error_label.configure(text=f"Error: {str(e)}")
            self.error_frame.pack(fill="x", pady=(15, 0))