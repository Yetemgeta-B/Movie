import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tempfile
import datetime
from tkcalendar import Calendar, DateEntry

from core.movie_fetcher import MovieFetcher
from core.word_handler import WordHandler


class MovieTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie & Series Tracker")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Initialize objects
        self.movie_fetcher = MovieFetcher()
        self.word_handler = WordHandler()
        
        # Setup theme
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use a modern theme
        
        # Colors
        self.movie_color = "#FF8C00"  # Orange for movies
        self.series_color = "#4169E1"  # Royal blue for series
        
        # Configure styles
        self.style.configure("Movie.TFrame", background=self.movie_color)
        self.style.configure("Series.TFrame", background=self.series_color)
        self.style.configure("TButton", padding=6, relief="flat", background="#333333")
        
        # Track current view
        self.current_view = "both"  # Options: "both", "movie", "tv"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation bar
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        self.all_button = ttk.Button(nav_frame, text="All", command=lambda: self.change_view("both"))
        self.all_button.pack(side=tk.LEFT, padx=5)
        
        self.movies_button = ttk.Button(nav_frame, text="Movies", command=lambda: self.change_view("movie"))
        self.movies_button.pack(side=tk.LEFT, padx=5)
        
        self.series_button = ttk.Button(nav_frame, text="TV Series", command=lambda: self.change_view("tv"))
        self.series_button.pack(side=tk.LEFT, padx=5)
        
        # Search section
        search_frame = ttk.Frame(main_frame, padding="10")
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        search_entry.bind("<Return>", lambda e: self.search_media())
        
        self.media_type_var = tk.StringVar(value="both")
        ttk.Radiobutton(search_frame, text="Movies", variable=self.media_type_var, 
                       value="movie").grid(row=0, column=2, padx=5, pady=5)
        ttk.Radiobutton(search_frame, text="TV Series", variable=self.media_type_var, 
                       value="tv").grid(row=0, column=3, padx=5, pady=5)
        ttk.Radiobutton(search_frame, text="Both", variable=self.media_type_var, 
                       value="both").grid(row=0, column=4, padx=5, pady=5)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_media)
        search_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Results frame
        self.results_frame = ttk.Frame(main_frame, padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial message
        self.show_initial_message()
    
    def change_view(self, view_type):
        """Change the current view type"""
        self.current_view = view_type
        self.media_type_var.set(view_type)
        
        # Update UI to reflect the current view
        if view_type == "movie":
            self.status_var.set("Showing Movies view")
            self.movies_button.state(['pressed'])
            self.series_button.state(['!pressed'])
            self.all_button.state(['!pressed'])
        elif view_type == "tv":
            self.status_var.set("Showing TV Series view")
            self.movies_button.state(['!pressed'])
            self.series_button.state(['pressed'])
            self.all_button.state(['!pressed'])
        else:
            self.status_var.set("Showing All view")
            self.movies_button.state(['!pressed'])
            self.series_button.state(['!pressed'])
            self.all_button.state(['pressed'])
            
        # Clear current results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Show initial message
        self.show_initial_message()
    
    def show_initial_message(self):
        """Display initial instructions"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        message_frame = ttk.Frame(self.results_frame, padding="20")
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(message_frame, 
                 text="Welcome to Movie & Series Tracker!", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        ttk.Label(message_frame, 
                 text="Search for a movie or TV series to add to your Word document.", 
                 font=("Arial", 12)).pack(pady=5)
        
        ttk.Label(message_frame, 
                 text="1. Enter a title in the search box above", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(message_frame, 
                 text="2. Select whether to search for movies, TV series, or both", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(message_frame, 
                 text="3. Click on a result to view details", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=2)
        ttk.Label(message_frame, 
                 text="4. Add it to your Word document with a single click", 
                 font=("Arial", 11)).pack(anchor=tk.W, pady=2)
    
    def search_media(self):
        """Perform media search and display results"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search term.")
            return
        
        self.status_var.set(f"Searching for '{query}'...")
        self.root.update_idletasks()
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Determine media type for search
        media_type = self.media_type_var.get()
        if media_type == "both":
            media_type = None
        
        # Perform search in a separate thread
        threading.Thread(target=self._fetch_search_results, 
                         args=(query, media_type)).start()
    
    def _fetch_search_results(self, query, media_type):
        """Fetch search results in background thread"""
        results = self.movie_fetcher.search_media(query, media_type)
        
        # Update UI in main thread
        self.root.after(0, lambda: self._display_search_results(results))
    
    def _display_search_results(self, results):
        """Display search results"""
        if not results:
            self.status_var.set("No results found.")
            message = ttk.Label(self.results_frame, text="No results found. Try a different search term.")
            message.pack(pady=20)
            return
        
        self.status_var.set(f"Found {len(results)} results.")
        
        # Create scrollable canvas
        container = ttk.Frame(self.results_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Filter results based on current view
        filtered_results = []
        for item in results:
            if self.current_view == "both" or item.get("type") == self.current_view:
                filtered_results.append(item)
        
        if not filtered_results:
            message = ttk.Label(scrollable_frame, text="No results found in the current view. Try changing the view type.")
            message.pack(pady=20)
            return
        
        # Display results
        for i, item in enumerate(filtered_results):
            item_type = item.get("type", "unknown")
            frame_style = "Movie.TFrame" if item_type == "movie" else "Series.TFrame"
            
            result_frame = ttk.Frame(scrollable_frame, padding="10", style=frame_style)
            result_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Title and type
            title_frame = ttk.Frame(result_frame)
            title_frame.pack(fill=tk.X)
            
            title_label = ttk.Label(
                title_frame, 
                text=item.get("title", "Unknown Title"),
                font=("Arial", 12, "bold")
            )
            title_label.pack(side=tk.LEFT)
            
            type_label = ttk.Label(
                title_frame,
                text=f"[{item_type.upper()}]",
                font=("Arial", 10)
            )
            type_label.pack(side=tk.LEFT, padx=5)
            
            # Release date if available
            if item.get("release_date"):
                date_text = item["release_date"].split("-")[0] if "-" in item["release_date"] else item["release_date"]
                date_label = ttk.Label(title_frame, text=f"({date_text})")
                date_label.pack(side=tk.LEFT)
            
            # View details button
            details_button = ttk.Button(
                result_frame,
                text="View Details",
                command=lambda item_id=item.get("id"), item_type=item_type: 
                         self.show_media_details(item_id, item_type)
            )
            details_button.pack(pady=5)
    
    def show_media_details(self, item_id, item_type):
        """Show detailed information about the selected media"""
        self.status_var.set(f"Fetching details...")
        
        # Fetch details in a separate thread
        threading.Thread(target=self._fetch_media_details, 
                         args=(item_id, item_type)).start()
    
    def _fetch_media_details(self, item_id, item_type):
        """Fetch media details in background thread"""
        if item_type == "movie":
            details = self.movie_fetcher.get_movie_details(item_id)
            self.root.after(0, lambda: self._display_movie_details(details))
        else:
            details = self.movie_fetcher.get_tv_details(item_id)
            self.root.after(0, lambda: self._display_series_details(details))
    
    def _display_movie_details(self, details):
        """Display movie details"""
        if not details:
            self.status_var.set("Error fetching movie details.")
            messagebox.showerror("Error", "Failed to fetch movie details.")
            return
        
        self.status_var.set("Movie details retrieved.")
        
        # Create a details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Movie: {details.get('title', 'Unknown')}")
        details_window.geometry("500x500")
        details_window.minsize(500, 500)
        
        # Create main container
        container = ttk.Frame(details_window, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            container, 
            text=details.get("title", "Unknown Title"),
            font=("Arial", 16, "bold")
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Info frame
        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Duration
        if details.get("duration"):
            ttk.Label(info_frame, text="Duration:").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["duration"]).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Genre
        if details.get("genre"):
            ttk.Label(info_frame, text="Genre:").grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["genre"]).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Release date
        if details.get("release_date"):
            ttk.Label(info_frame, text="Release Date:").grid(row=2, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["release_date"]).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # IMDb rating
        if details.get("imdb_rating"):
            ttk.Label(info_frame, text="IMDb Rating:").grid(row=3, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["imdb_rating"]).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # RT rating
        if details.get("rt_rating"):
            ttk.Label(info_frame, text="Rotten Tomatoes:").grid(row=4, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["rt_rating"]).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Date selection frame
        date_frame = ttk.LabelFrame(container, text="Watch Date", padding="10")
        date_frame.pack(fill=tk.X, pady=10)
        
        # Date options
        date_var = tk.StringVar(value="today")
        ttk.Radiobutton(date_frame, text="Today", variable=date_var, 
                      value="today").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(date_frame, text="Custom Date", variable=date_var, 
                      value="custom").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Date picker
        self.watch_date = datetime.datetime.now()
        date_picker = DateEntry(date_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, 
                              date_pattern='MM/dd/yyyy')
        date_picker.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        date_picker.set_date(self.watch_date)
        
        # Update watch date when date entry changes
        def update_date():
            if date_var.get() == "today":
                self.watch_date = datetime.datetime.now()
            else:
                selected_date = date_picker.get_date()
                self.watch_date = datetime.datetime(
                    selected_date.year, 
                    selected_date.month, 
                    selected_date.day
                )
        
        date_var.trace_add("write", lambda *args: update_date())
        date_picker.bind("<<DateEntrySelected>>", lambda e: update_date())
        
        # Add to Word button
        add_button = ttk.Button(
            container,
            text="Add to Word Document",
            command=lambda: self.add_movie_to_word(details, details_window, self.watch_date)
        )
        add_button.pack(pady=20)
    
    def _display_series_details(self, details):
        """Display TV series details"""
        if not details:
            self.status_var.set("Error fetching series details.")
            messagebox.showerror("Error", "Failed to fetch series details.")
            return
        
        self.status_var.set("Series details retrieved.")
        
        # Create a details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Series: {details.get('title', 'Unknown')}")
        details_window.geometry("500x550")
        details_window.minsize(500, 550)
        
        # Create main container
        container = ttk.Frame(details_window, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            container, 
            text=details.get("title", "Unknown Title"),
            font=("Arial", 16, "bold")
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Info frame
        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seasons
        if details.get("seasons"):
            ttk.Label(info_frame, text="Seasons:").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=str(details["seasons"])).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Episodes
        if details.get("episodes"):
            ttk.Label(info_frame, text="Episodes:").grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=str(details["episodes"])).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Genre
        if details.get("genre"):
            ttk.Label(info_frame, text="Genre:").grid(row=2, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["genre"]).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # First air date
        if details.get("first_air_date"):
            ttk.Label(info_frame, text="First Air Date:").grid(row=3, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["first_air_date"]).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # IMDb rating
        if details.get("imdb_rating"):
            ttk.Label(info_frame, text="IMDb Rating:").grid(row=4, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["imdb_rating"]).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # RT rating
        if details.get("rt_rating"):
            ttk.Label(info_frame, text="Rotten Tomatoes:").grid(row=5, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text=details["rt_rating"]).grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Date selection frame
        date_frame = ttk.LabelFrame(container, text="Start Watching Date", padding="10")
        date_frame.pack(fill=tk.X, pady=10)
        
        # Date options
        date_var = tk.StringVar(value="today")
        ttk.Radiobutton(date_frame, text="Today", variable=date_var, 
                      value="today").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(date_frame, text="Custom Date", variable=date_var, 
                      value="custom").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Date picker
        self.start_date = datetime.datetime.now()
        date_picker = DateEntry(date_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, 
                              date_pattern='MM/dd/yyyy')
        date_picker.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        date_picker.set_date(self.start_date)
        
        # Update start date when date entry changes
        def update_date():
            if date_var.get() == "today":
                self.start_date = datetime.datetime.now()
            else:
                selected_date = date_picker.get_date()
                self.start_date = datetime.datetime(
                    selected_date.year, 
                    selected_date.month, 
                    selected_date.day
                )
        
        date_var.trace_add("write", lambda *args: update_date())
        date_picker.bind("<<DateEntrySelected>>", lambda e: update_date())
        
        # Finished checkbox and date selection
        finish_frame = ttk.LabelFrame(container, text="Series Status", padding="10")
        finish_frame.pack(fill=tk.X, pady=10)
        
        finished_var = tk.BooleanVar(value=False)
        finished_check = ttk.Checkbutton(
            finish_frame, 
            text="Mark as Finished", 
            variable=finished_var,
            command=lambda: finish_date_frame.pack(fill=tk.X, pady=(5, 0)) if finished_var.get() else finish_date_frame.pack_forget()
        )
        finished_check.grid(row=0, column=0, sticky=tk.W)
        
        # Finish date frame (hidden by default)
        finish_date_frame = ttk.Frame(finish_frame)
        
        # Finish date options
        finish_date_var = tk.StringVar(value="today")
        ttk.Radiobutton(finish_date_frame, text="Today", variable=finish_date_var, 
                      value="today").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(finish_date_frame, text="Custom Date", variable=finish_date_var, 
                      value="custom").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Finish date picker
        self.finish_date = datetime.datetime.now()
        finish_date_picker = DateEntry(finish_date_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, 
                                     date_pattern='MM/dd/yyyy')
        finish_date_picker.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        finish_date_picker.set_date(self.finish_date)
        
        # Update finish date when date entry changes
        def update_finish_date():
            if finish_date_var.get() == "today":
                self.finish_date = datetime.datetime.now()
            else:
                selected_date = finish_date_picker.get_date()
                self.finish_date = datetime.datetime(
                    selected_date.year, 
                    selected_date.month, 
                    selected_date.day
                )
        
        finish_date_var.trace_add("write", lambda *args: update_finish_date())
        finish_date_picker.bind("<<DateEntrySelected>>", lambda e: update_finish_date())
        
        # Add to Word button
        add_button = ttk.Button(
            container,
            text="Add to Word Document",
            command=lambda: self.add_series_to_word(
                details, 
                finished_var.get(),
                details_window,
                self.start_date,
                self.finish_date if finished_var.get() else None
            )
        )
        add_button.pack(pady=20)
    
    def add_movie_to_word(self, movie_data, details_window=None, watch_date=None):
        """Add the movie to the Word document"""
        self.status_var.set("Adding movie to Word document...")
        
        # Format the watch date to match requirements
        if watch_date:
            formatted_watch_date = watch_date.strftime("%b %d,%Y")
            movie_data["watch_date"] = formatted_watch_date
        
        result = self.word_handler.add_movie(movie_data)
        
        if result:
            self.status_var.set("Movie added successfully.")
            messagebox.showinfo("Success", f"Movie '{movie_data.get('title')}' added successfully.")
            if details_window:
                details_window.destroy()
        else:
            self.status_var.set("Failed to add movie.")
            messagebox.showerror("Error", "Failed to add movie to Word document.")
    
    def add_series_to_word(self, series_data, is_finished, details_window=None, start_date=None, finish_date=None):
        """Add the series to the Word document"""
        self.status_var.set("Adding series to Word document...")
        
        # Format the dates to match requirements
        if start_date:
            formatted_start_date = start_date.strftime("%b %d,%Y")
            series_data["start_date"] = formatted_start_date
            
        if finish_date and is_finished:
            formatted_finish_date = finish_date.strftime("%b %d,%Y")
            series_data["finish_date"] = formatted_finish_date
        
        result = self.word_handler.add_series(series_data, is_finished, finish_date)
        
        if result:
            self.status_var.set("Series added successfully.")
            messagebox.showinfo("Success", f"Series '{series_data.get('title')}' added successfully.")
            if details_window:
                details_window.destroy()
        else:
            self.status_var.set("Failed to add series.")
            messagebox.showerror("Error", "Failed to add series to Word document.")
    
    def close(self):
        """Close the application properly"""
        self.word_handler.close_document()
        self.root.destroy() 