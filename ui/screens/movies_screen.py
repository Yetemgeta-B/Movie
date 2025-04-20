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
from core.movie_fetcher import MovieFetcher
from core.word_handler import WordHandler
from tkcalendar import Calendar, DateEntry

class MoviesScreen(ctk.CTkFrame):
    """
    Movies screen for the application.
    Displays a clean search interface for finding and adding movies.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Initialize variables
        self.movies_data = []
        self.movie_fetcher = MovieFetcher()
        self.word_handler = WordHandler()
        self.current_details_frame = None
        
        # Load movie data
        self.data_file = Path("data/movies.json")
        self._load_movies()
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the UI elements for the movies screen"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Header title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🎬 Movies",
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
            placeholder_text="Search movies...",
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
            text="🎬",
            font=ctk.CTkFont(size=48)
        )
        welcome_icon.pack(pady=(0, 10))
        
        welcome_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Search for movies to add to your collection",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_text.pack(pady=5)
        
        instruction_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Type a movie name in the search box and press Enter",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        instruction_text.pack(pady=5)
        
        # Back to results button (hidden initially)
        self.back_button = ctk.CTkButton(
            self,
            text="← Back to Results",
            command=self._back_to_results,
            width=150,
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9")
        )
        # Don't grid it yet - will be shown when needed
        
        # Movie details container (hidden initially)
        self.details_container = ctk.CTkFrame(self, fg_color="transparent")
        # Don't grid it yet - will be shown when needed
    
    def _load_movies(self):
        """Load movies from the data file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    self.movies_data = json.load(f)
            else:
                # Create directory if it doesn't exist
                self.data_file.parent.mkdir(parents=True, exist_ok=True)
                # Create empty file
                with open(self.data_file, "w") as f:
                    json.dump([], f)
                self.movies_data = []
        except Exception as e:
            print(f"Error loading movies: {e}")
            self.movies_data = []
    
    def _save_movies(self):
        """Save movies to the data file"""
        try:
            # Create directory if it doesn't exist
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, "w") as f:
                json.dump(self.movies_data, f, indent=2)
        except Exception as e:
            print(f"Error saving movies: {e}")
    
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
        def search_movies():
            try:
                # Search online
                api_results = self.movie_fetcher.search_media(search_text, "movie")
                
                # Process and display results
                self.after(0, lambda: self._display_search_results(api_results, search_text))
            except Exception as e:
                print(f"Error searching online: {e}")
                self.after(0, lambda: self._show_search_error(str(e)))
                
        # Start the search in a separate thread
        threading.Thread(target=search_movies).start()
    
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
                text=f"No movies found for '{search_query}'",
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
        
        # Create a movie card for each result
        for i, movie in enumerate(results):
            self._create_movie_result_card(results_grid, movie, i)
    
    def _create_movie_result_card(self, parent, movie, index):
        """Create a card for a movie search result"""
        # Card frame
        card = ctk.CTkFrame(
            parent, 
            corner_radius=10,
            border_width=1,
            border_color=("lightgray", "gray30")
        )
        card.pack(fill="x", padx=10, pady=5)
        
        # Make the entire card clickable
        card.bind("<Button-1>", lambda e, m=movie: self._show_movie_details(m))
        
        # Configure grid
        card.grid_columnconfigure(1, weight=1)
        
        # Movie poster frame
        poster_frame = ctk.CTkFrame(
            card, 
            width=90, 
            height=135,
            fg_color=("gray90", "gray20")
        )
        poster_frame.grid(row=0, column=0, padx=10, pady=10)
        poster_frame.bind("<Button-1>", lambda e, m=movie: self._show_movie_details(m))
        
        # If movie has poster URL, load it
        poster_url = f"https://image.tmdb.org/t/p/w185{movie.get('poster_path')}" if movie.get('poster_path') else None
        if poster_url:
            self._load_movie_poster(poster_url, poster_frame)
        else:
            # Placeholder text
            poster_label = ctk.CTkLabel(
                poster_frame, 
                text="🎬",
                font=ctk.CTkFont(size=32)
            )
            poster_label.place(relx=0.5, rely=0.5, anchor="center")
            poster_label.bind("<Button-1>", lambda e, m=movie: self._show_movie_details(m))
        
        # Movie details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        details_frame.bind("<Button-1>", lambda e, m=movie: self._show_movie_details(m))
        
        # Title and year
        title = movie.get("title", "Unknown")
        year = movie.get("release_date", "")[:4] if movie.get("release_date") else ""
        
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
        title_label.bind("<Button-1>", lambda e, m=movie: self._show_movie_details(m))
        
        # Overview/description (truncated)
        overview = movie.get("overview", "")
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
            overview_label.bind("<Button-1>", lambda e, m=movie: self._show_movie_details(m))
        
        # Change button to "View Details" to better indicate functionality
        select_button = ctk.CTkButton(
            details_frame,
            text="View Details",
            width=120,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(weight="bold"),
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9"),
            command=lambda: self._show_movie_details(movie)
        )
        select_button.pack(anchor="e", pady=(10, 0))
    
    def _load_movie_poster(self, url, frame, size=(90, 135)):
        """Load movie poster from URL in a separate thread"""
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
                                text="🎬",
                                font=ctk.CTkFont(size=32 if size[0] < 100 else 64)
                            )
                            placeholder.place(relx=0.5, rely=0.5, anchor="center")
                        except Exception as placeholder_error:
                            print(f"Error creating placeholder: {placeholder_error}")
                
                self.after(0, show_placeholder)
        
        # Start thread to load image
        threading.Thread(target=load_image).start()
    
    def _show_movie_details(self, movie):
        """Show the movie details in an expanded view"""
        # First fetch full details
        movie_id = movie.get("id")
        if not movie_id:
            self._show_error("Could not fetch movie details")
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
            text=f"Fetching details for\n{movie.get('title', 'movie')}...",
            font=ctk.CTkFont(size=14)
        )
        loading_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        def fetch_details():
            try:
                details = self.movie_fetcher.get_movie_details(movie_id)
                self.after(0, lambda: self._display_movie_details(loading_dialog, movie, details))
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Error fetching movie details: {e}"))
                self.after(0, loading_dialog.destroy)
        
        # Start the fetch in a separate thread
        threading.Thread(target=fetch_details).start()
    
    def _display_movie_details(self, loading_dialog, movie, details):
        """Display detailed movie information in the main content area"""
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
        
        # If movie has poster URL, load it with higher resolution
        poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None
        if poster_url:
            self._load_movie_poster(poster_url, poster_frame, size=(300, 450))
        else:
            # Placeholder text
            poster_label = ctk.CTkLabel(
                poster_frame, 
                text="🎬",
                font=ctk.CTkFont(size=64)
            )
            poster_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Action buttons
        action_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        add_button = ctk.CTkButton(
            action_frame,
            text="Add to Collection",
            command=lambda: self._show_movie_add_dialog(None, movie, details),
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
        
        # Movie details in right column
        # Title and year
        title = movie.get("title", "Unknown")
        year = movie.get("release_date", "")[:4] if movie.get("release_date") else ""
        
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
        
        # Tagline if available
        if "tagline" in details and details["tagline"]:
            tagline_label = ctk.CTkLabel(
                right_column,
                text=details["tagline"],
                font=ctk.CTkFont(size=16, slant="italic"),
                text_color=("gray40", "gray70")
            )
            tagline_label.pack(anchor="w", pady=(0, 15))
        
        # Ratings display
        if "imdb_rating" in details or "rt_rating" in details:
            ratings_frame = ctk.CTkFrame(right_column, fg_color="transparent")
            ratings_frame.pack(fill="x", pady=(0, 15))
            
            if "imdb_rating" in details and details["imdb_rating"]:
                imdb_frame = ctk.CTkFrame(
                ratings_frame,
                fg_color=("#f5c518", "#f5c518"),
                corner_radius=5
            )
            imdb_frame.pack(side="left", padx=(0, 10))
            
            imdb_label = ctk.CTkLabel(
                imdb_frame,
                    text=f"IMDb: {details['imdb_rating']}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                text_color="black",
                padx=8,
                pady=2
            )
            imdb_label.pack()
        
            if "rt_rating" in details and details["rt_rating"]:
                rt_color = "#fa320a" if float(details["rt_rating"].replace("%", "")) >= 60 else "#76b900"
                rt_value = details["rt_rating"]
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
        
        # Info grid: runtime, genres, director, release date
        info_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Runtime
        info_row = 0
        if "runtime" in details and details["runtime"]:
            runtime_label = ctk.CTkLabel(
                info_frame,
                text="Runtime:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            runtime_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            # Format runtime as hours and minutes
            minutes = int(details["runtime"])
            hours = minutes // 60
            mins = minutes % 60
            formatted_runtime = f"{hours}h {mins}m ({minutes} minutes)"
            
            runtime_value = ctk.CTkLabel(
                info_frame,
                text=formatted_runtime,
                anchor="w"
            )
            runtime_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
        
        # Genres
        if "genres" in details and details["genres"]:
            genres_label = ctk.CTkLabel(
                info_frame,
                text="Genres:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            genres_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            genres_value = ctk.CTkLabel(
                info_frame,
                text=details["genres"],
                anchor="w",
                wraplength=400,
                justify="left"
            )
            genres_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
        
        # Director
        if "director" in details and details["director"]:
            director_label = ctk.CTkLabel(
                info_frame,
                text="Director:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            director_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            director_value = ctk.CTkLabel(
                info_frame,
                text=details["director"],
                anchor="w"
            )
            director_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
        
        # Release date
        if "release_date" in details and details["release_date"]:
            release_label = ctk.CTkLabel(
                info_frame,
                text="Release Date:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            release_label.grid(row=info_row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            release_value = ctk.CTkLabel(
                info_frame,
                text=details["release_date"],
                anchor="w"
            )
            release_value.grid(row=info_row, column=1, sticky="w", pady=2)
            info_row += 1
        
        # Cast/Actors (if available)
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
        
        # Add a nice overview separator
        separator = ctk.CTkFrame(right_column, height=1, fg_color="gray70")
        separator.pack(fill="x", pady=10)

        # Overview
        if "overview" in movie and movie["overview"]:
            overview_label = ctk.CTkLabel(
                right_column,
                text="Overview:",
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w"
            )
            overview_label.pack(anchor="w", pady=(0, 5))
            
            overview_text = ctk.CTkLabel(
                right_column,
                text=movie["overview"],
                font=ctk.CTkFont(size=14),
                wraplength=500,
                justify="left"
            )
            overview_text.pack(anchor="w", pady=(0, 15))
    
    def _back_to_results(self):
        """Go back to search results or welcome screen"""
        # Clear current view
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # If we have saved search results, restore them
        if hasattr(self, 'last_search_results') and self.last_search_results:
            for widget in self.last_search_results:
                try:
                    # Check if widget still exists
                    widget.winfo_exists()
                    widget.pack(fill="x", padx=10, pady=5)
                except Exception:
                    # Widget was destroyed, skip it
                    continue
        else:
            # If no search results, show welcome screen
            self._create_welcome_screen()
    
    def _show_error(self, message):
        """Show an error message to the user"""
        dialog = ctk.CTkInputDialog(
            text=message,
            title="Error"
        )
        dialog.get_input()
        
    def _show_message(self, message, title="Message"):
        """Show an informational message to the user"""
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
            text="🎬",
            font=ctk.CTkFont(size=48)
        )
        welcome_icon.pack(pady=(0, 10))
        
        welcome_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Search for movies to add to your collection",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_text.pack(pady=5)
        
        instruction_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Type a movie name in the search box and press Enter",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        instruction_text.pack(pady=5)

    def _show_movie_add_dialog(self, loading_dialog, movie, details):
        """Show dialog to add movie with watch date and rating"""
        if loading_dialog:
            loading_dialog.destroy()
        
        dialog = MovieAddDialog(self, movie, details)
        dialog.wait_window()  # Wait for the dialog to close
        
        # If movie was added, refresh the view
        if hasattr(dialog, "result") and dialog.result:
            # Add the movie to data
            self.movies_data.append(dialog.result)
            self._save_movies()
            
            # No popup message - removed
            
            # Go back to results or welcome screen
            self._back_to_results()

    def _create_welcome_screen(self):
        """Create the initial welcome screen with search"""
        # Clear any existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Create header
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 Movies",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Create search frame
        search_frame = ctk.CTkFrame(self.content_frame)
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search for a movie:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        search_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter movie title...",
            font=ctk.CTkFont(size=14),
            height=35
        )
        self.search_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.search_entry.bind("<Return>", self._on_search)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=lambda: self._on_search(None),
            height=35,
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9")
        )
        search_button.pack(side="right", padx=10, pady=(0, 10))
        
        # Welcome message and instructions
        welcome_frame = ctk.CTkFrame(self.content_frame)
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to Movie Tracker",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        welcome_label.pack(pady=(20, 10))
        
        instructions_label = ctk.CTkLabel(
            welcome_frame,
            text="Search for a movie to add it to your collection.\nYou can rate movies and save details to your Word document.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        instructions_label.pack(pady=(0, 20))


class MovieAddDialog(ctk.CTkToplevel):
    """Dialog for adding a movie with watch date and rating"""
    
    def __init__(self, parent, movie, details):
        super().__init__(parent)
        self.title("Add Movie")
        self.geometry("700x650")  # Increased size for better visibility
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog properly on the screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Store movie data
        self.movie = movie
        self.details = details
        self.parent = parent
        self.result = None
        self.saved_to_word = False
        
        # Initialize Word handler
        self.word_handler = WordHandler()
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create UI for the add dialog"""
        # Main frame with padding
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create two columns
        left_column = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_column = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Poster frame in left column
        poster_frame = ctk.CTkFrame(
            left_column, 
            width=240, 
            height=360,
            fg_color=("gray90", "gray20")
        )
        poster_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # If movie has poster URL, load it
        poster_url = f"https://image.tmdb.org/t/p/w500{self.movie.get('poster_path')}" if self.movie.get('poster_path') else None
        if poster_url:
            self._load_poster(poster_url, poster_frame)
        else:
            # Placeholder text
            poster_label = ctk.CTkLabel(
                poster_frame, 
                text="🎬",
                font=ctk.CTkFont(size=64)
            )
            poster_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Save to Word button (at the bottom of the left column)
        self.save_word_button = ctk.CTkButton(
            left_column,
            text="Save to Word",
            command=self._save_to_word,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9")
        )
        self.save_word_button.pack(fill="x", padx=10, pady=5)
        
        # Cancel button (at the bottom of the left column)
        cancel_button = ctk.CTkButton(
            left_column,
            text="Cancel",
            command=self.destroy,
            height=40,
            fg_color="gray70",
            hover_color="gray50"
        )
        cancel_button.pack(fill="x", padx=10, pady=5)
        
        # Movie details in right column
        # Header with movie info
        header_frame = ctk.CTkFrame(right_column)
        header_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Movie title and year
        title = self.movie.get("title", "Unknown")
        year = self.movie.get("release_date", "")[:4] if self.movie.get("release_date") else ""
        
        title_text = title
        if year:
            title_text += f" ({year})"
            
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 0))
        
        # Movie details grid to display all info
        details_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=(10, 0))
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Row counter
        row = 0
        
        # Duration/Runtime
        if "runtime" in self.details and self.details["runtime"]:
            minutes = int(self.details["runtime"])
            hours = minutes // 60
            mins = minutes % 60
            runtime_text = f"{hours}h {mins}m ({minutes} minutes)"
            
            duration_label = ctk.CTkLabel(
                details_frame,
                text="Duration:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            duration_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            duration_value = ctk.CTkLabel(
                details_frame,
                text=runtime_text,
                anchor="w"
            )
            duration_value.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
        
        # Genres
        if "genres" in self.details and self.details["genres"]:
            genre_label = ctk.CTkLabel(
                details_frame,
                text="Genres:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            genre_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            genre_value = ctk.CTkLabel(
                details_frame,
                text=self.details["genres"],
                anchor="w"
            )
            genre_value.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
        # Release date
        if "release_date" in self.details and self.details["release_date"]:
            release_label = ctk.CTkLabel(
                details_frame,
                text="Release Date:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            )
            release_label.grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
            
            release_value = ctk.CTkLabel(
                details_frame,
                text=self.details["release_date"],
                anchor="w"
            )
            release_value.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
        # Ratings display
        ratings_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        ratings_frame.pack(pady=(10, 10))
        
        if "imdb_rating" in self.details and self.details["imdb_rating"]:
            imdb_frame = ctk.CTkFrame(
                ratings_frame,
                fg_color=("#f5c518", "#f5c518"),
                corner_radius=5
            )
            imdb_frame.pack(side="left", padx=(0, 10))
            
            imdb_label = ctk.CTkLabel(
                imdb_frame,
                text=f"IMDb: {self.details['imdb_rating']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="black",
                padx=8,
                pady=2
            )
            imdb_label.pack()
        
        if "rt_rating" in self.details and self.details["rt_rating"]:
            rt_color = "#fa320a" if float(self.details["rt_rating"].replace("%", "")) >= 60 else "#76b900"
            rt_value = self.details["rt_rating"]
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
        
        # Separator
        separator = ctk.CTkFrame(right_column, height=2, fg_color="gray70")
        separator.pack(fill="x", padx=10, pady=10)
        
        # Form section title
        form_title = ctk.CTkLabel(
            right_column,
            text="Add Movie Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.pack(pady=(0, 10))

        # Watch date section
        date_frame = ctk.CTkFrame(right_column)
        date_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        date_label = ctk.CTkLabel(
            date_frame,
            text="When did you watch this movie?",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        date_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Date options
        date_options_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        date_options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Today option
        self.date_var = ctk.StringVar(value="today")
        
        today_radio = ctk.CTkRadioButton(
            date_options_frame,
            text="Today",
            variable=self.date_var,
            value="today",
            command=self._toggle_date_option,
            fg_color="#4a86e8",  # Match app blue color
            hover_color="#2d5bb9"  # Darker blue for hover
        )
        today_radio.pack(anchor="w", padx=10, pady=5)
        
        # Custom date option
        custom_date_frame = ctk.CTkFrame(date_options_frame, fg_color="transparent")
        custom_date_frame.pack(fill="x", padx=10, pady=5)
        
        custom_radio = ctk.CTkRadioButton(
            custom_date_frame,
            text="Custom date: ",
            variable=self.date_var,
            value="custom",
            command=self._toggle_date_option,
            fg_color="#4a86e8",
            hover_color="#2d5bb9"
        )
        custom_radio.pack(side="left")
        
        # Date picker
        self.date_entry = DateEntry(
            custom_date_frame,
            width=20,
            state="disabled"
        )
        self.date_entry.pack(side="left", padx=10)
        
        # Rating section
        rating_frame = ctk.CTkFrame(right_column)
        rating_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        rating_label = ctk.CTkLabel(
            rating_frame,
            text="Your Rating:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        rating_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Rating control frame with plus/minus buttons
        rating_control_frame = ctk.CTkFrame(rating_frame, fg_color="transparent")
        rating_control_frame.pack(fill="x", padx=20, pady=5)
        
        # Minus button
        minus_button = ctk.CTkButton(
            rating_control_frame,
            text="-",
            width=30,
            height=30,
            command=self._decrease_rating,
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9")
        )
        minus_button.pack(side="left", padx=(0, 5))
        
        # Rating slider
        self.rating_var = ctk.DoubleVar(value=8.0)
        
        rating_slider = ctk.CTkSlider(
            rating_control_frame,
            from_=1,
            to=10,
            number_of_steps=36,  # Allow 0.25 increments
            variable=self.rating_var,
            command=self._update_rating_label
        )
        rating_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        # Plus button
        plus_button = ctk.CTkButton(
            rating_control_frame,
            text="+",
            width=30,
            height=30,
            command=self._increase_rating,
            fg_color=("#4a86e8", "#2d5bb9"),
            hover_color=("#3a76d8", "#1d4ba9")
        )
        plus_button.pack(side="left", padx=(5, 0))
        
        # Rating value display
        self.rating_display = ctk.CTkLabel(
            rating_frame,
            text="8.0/10",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.rating_display.pack(anchor="center", pady=(5, 10))

    def _load_poster(self, url, frame):
        """Load movie poster from URL in a separate thread"""
        # Show loading indicator
        loading_label = ctk.CTkLabel(
            frame, 
            text="Loading poster...",
            font=ctk.CTkFont(size=14)
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        
        def load_image():
            try:
                response = requests.get(url, timeout=10)
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((240, 360), Image.LANCZOS)
                
                # Schedule the UI update on the main thread
                def update_ui():
                    try:
                        # Use CTkImage
                        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 360))
                        
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
                    try:
                        # Show placeholder on error
                        placeholder = ctk.CTkLabel(
                            frame, 
                            text="🎬",
                            font=ctk.CTkFont(size=64)
                        )
                        placeholder.place(relx=0.5, rely=0.5, anchor="center")
                    except Exception as placeholder_error:
                        print(f"Error creating placeholder: {placeholder_error}")
                
                self.after(0, show_placeholder)
        
        # Start thread to load image
        threading.Thread(target=load_image).start()
        
    def _toggle_date_option(self):
        """Toggle between today and custom date entry"""
        if self.date_var.get() == "custom":
            self.date_entry.configure(state="normal")
        else:
            self.date_entry.configure(state="disabled")
    
    def _increase_rating(self):
        """Increase rating by 0.25"""
        current = self.rating_var.get()
        if current < 10:
            self.rating_var.set(min(10, current + 0.25))
            self._update_rating_label(self.rating_var.get())
    
    def _decrease_rating(self):
        """Decrease rating by 0.25"""
        current = self.rating_var.get()
        if current > 1:
            self.rating_var.set(max(1, current - 0.25))
            self._update_rating_label(self.rating_var.get())
    
    def _update_rating_label(self, value):
        """Update the rating label when slider is moved"""
        self.rating_display.configure(text=f"{value:.2f}/10")
    
    def _format_watch_date(self):
        """Format the watch date based on selection"""
        if self.date_var.get() == "today":
            return datetime.datetime.now().strftime("%b %d, %Y")
        else:
            # Get the date from DateEntry and format it
            date = self.date_entry.get_date()
            return date.strftime("%b %d, %Y")
    
    def _save_to_word(self):
        """Save movie details to Word document with correct field names matching the table"""
        try:
            # Get watch date and rating
            watch_date = self._format_watch_date()
            user_rating = self.rating_var.get()
            
            # Format runtime properly (convert minutes to "Xh Ym" format)
            time_duration = ""
            if "runtime" in self.details and self.details["runtime"]:
                minutes = int(self.details["runtime"])
                hours = minutes // 60
                remaining_minutes = minutes % 60
                time_duration = f"{hours}h {remaining_minutes}m"
            
            # Format ratings consistently (X.X/10 for user/IMDb, Y% for RT)
            imdb_rating = ""
            if "imdb_rating" in self.details and self.details["imdb_rating"]:
                imdb_rating = f"{self.details['imdb_rating']}"
                if "/10" not in imdb_rating:
                    imdb_rating += "/10"
            
            rt_rating = ""
            if "rt_rating" in self.details and self.details["rt_rating"]:
                rt_rating = self.details["rt_rating"]
                if "%" not in rt_rating:
                    rt_rating += "%"
            
            # Prepare data for Word document with exact field names matching the table
            word_data = {
                # Main fields exactly matching the required columns
                "title": self.movie.get("title", ""),  # Name column
                "duration": time_duration,  # TimeDuration column (2h 38m format)
                "genres": self.details.get("genres", ""),  # Genre column (Action/Sci-Fi format)
                "watch_date": watch_date,  # Watch date column
                "release_date": self.details.get("release_date", ""),  # Release date column 
                "user_rating": f"{user_rating:.2f}/10",  # Rating column (9.9/10 format)
                "imdb_rating": imdb_rating,  # IMDb rating column (8.8/10 format)
                "rt_rating": rt_rating,  # RT column (87% format)
                
                # Set rewatch to False since we removed that section
                "rewatch": False
            }
            
            # Add to Word document
            word_added = self.word_handler.add_movie(word_data)
            
            if word_added:
                self.saved_to_word = True
                # Don't close the document, keep it open
                
                # Update the button appearance
                self.save_word_button.configure(
                    text="✓ Saved to Word", 
                    state="disabled",
                    fg_color="green"
                )
                
                # Create a visually appealing success message
                success_frame = ctk.CTkFrame(self, fg_color="#32CD32")  # Green background
                success_frame.pack(fill="x", padx=20, pady=(0, 20))
                
                success_icon = ctk.CTkLabel(
                    success_frame,
                    text="✓",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="white"
                )
                success_icon.pack(side="left", padx=(20, 10), pady=10)
                
                success_message = ctk.CTkLabel(
                    success_frame,
                    text=f"'{self.movie.get('title')}' added to Word document!",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white"
                )
                success_message.pack(side="left", padx=10, pady=10)
                
                # Create result data for passing back
                self.result = {
                    "title": self.movie.get("title", ""),
                    "date_added": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "watch_date": watch_date,
                    "user_rating": user_rating,
                    "word_added": True
                }
                
                # Add optional details
                if "runtime" in self.details:
                    self.result["runtime"] = self.details["runtime"]
                if "genres" in self.details:
                    self.result["genres"] = self.details["genres"]
                if "director" in self.details:
                    self.result["director"] = self.details["director"]
                if "release_date" in self.details:
                    self.result["release_date"] = self.details["release_date"]
                if "imdb_rating" in self.details and self.details["imdb_rating"]:
                    try:
                        rating = float(self.details["imdb_rating"].replace("/10", ""))
                        self.result["imdb_rating"] = rating
                    except:
                        pass
                if "rt_rating" in self.details and self.details["rt_rating"]:
                    try:
                        rating = float(self.details["rt_rating"].replace("%", ""))
                        self.result["rt_rating"] = rating
                    except:
                        pass
                if "cast" in self.details:
                    self.result["cast"] = self.details["cast"]
                if "overview" in self.movie:
                    self.result["overview"] = self.movie["overview"]
                
            else:
                # Show error if failed
                error_frame = ctk.CTkFrame(self, fg_color="#FF5252")  # Red background
                error_frame.pack(fill="x", padx=20, pady=(0, 20))
                
                error_icon = ctk.CTkLabel(
                    error_frame,
                    text="✗",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="white"
                )
                error_icon.pack(side="left", padx=(20, 10), pady=10)
                
                error_message = ctk.CTkLabel(
                    error_frame,
                    text="Error saving to Word document. Please try again.",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white"
                )
                error_message.pack(side="left", padx=10, pady=10)
                
        except Exception as e:
            print(f"Error saving to Word: {e}")
            
            # Show error in a frame
            error_frame = ctk.CTkFrame(self, fg_color="#FF5252")  # Red background
            error_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            error_icon = ctk.CTkLabel(
                error_frame,
                text="✗",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
            error_icon.pack(side="left", padx=(20, 10), pady=10)
            
            error_message = ctk.CTkLabel(
                error_frame,
                text=f"Error: {str(e)}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            error_message.pack(side="left", padx=10, pady=10)