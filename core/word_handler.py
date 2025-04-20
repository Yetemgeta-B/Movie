import win32com.client
import datetime
from core.settings_handler import settings

class WordHandler:
    def __init__(self):
        self.word_app = None
        self.doc = None
        
    def open_document(self):
        """Open the Word document"""
        try:
            word_doc_path = settings.get("WORD_DOC_PATH", "")
            if not word_doc_path:
                print("Word document path is not set")
                return False
                
            self.word_app = win32com.client.Dispatch("Word.Application")
            self.word_app.Visible = True
            self.doc = self.word_app.Documents.Open(word_doc_path)
            return True
        except Exception as e:
            print(f"Error opening Word document: {e}")
            return False
    
    def close_document(self, save=True):
        """Close the Word document"""
        if self.doc:
            if save:
                self.doc.Save()
            self.doc.Close()
            self.doc = None
        
        if self.word_app:
            self.word_app.Quit()
            self.word_app = None
    
    def get_next_movie_number(self):
        """Get the next available number for a movie entry"""
        if not self.doc:
            return 1
            
        try:
            movie_table_index = settings.get_movie_table_index()
            movie_columns = settings.get_movie_columns()
            
            table = self.doc.Tables(movie_table_index)
            # Find the last row with content
            for row_idx in range(table.Rows.Count, 1, -1):
                cell_value = table.Cell(row_idx, movie_columns["NO"] + 1).Range.Text
                # Cell text ends with special characters, remove them
                cell_value = cell_value.strip('\r\a\x07')
                if cell_value and cell_value.isdigit():
                    return int(cell_value) + 1
            
            return 1  # If no entries found
        except Exception as e:
            print(f"Error getting next movie number: {e}")
            return 1
    
    def get_next_series_number(self):
        """Get the next available number for a series entry"""
        if not self.doc:
            return 1
            
        try:
            series_table_index = settings.get_series_table_index()
            series_columns = settings.get_series_columns()
            
            table = self.doc.Tables(series_table_index)
            # Find the last row with content
            for row_idx in range(table.Rows.Count, 1, -1):
                cell_value = table.Cell(row_idx, series_columns["NO"] + 1).Range.Text
                # Cell text ends with special characters, remove them
                cell_value = cell_value.strip('\r\a\x07')
                if cell_value and cell_value.isdigit():
                    return int(cell_value) + 1
            
            return 1  # If no entries found
        except Exception as e:
            print(f"Error getting next series number: {e}")
            return 1
    
    def add_movie(self, movie_data):
        """Add a new movie entry to the table"""
        if not self.doc:
            if not self.open_document():
                return False
        
        try:
            movie_table_index = settings.get_movie_table_index()
            movie_columns = settings.get_movie_columns()
            
            table = self.doc.Tables(movie_table_index)
            next_number = self.get_next_movie_number()
            
            # Add new row
            new_row = table.Rows.Add()
            
            # Fill in data
            new_row.Cells(movie_columns["NO"] + 1).Range.Text = str(next_number)
            
            # Movie title (NAME column)
            new_row.Cells(movie_columns["NAME"] + 1).Range.Text = movie_data.get("title", "")
            
            # Handle time duration (use the formatted duration directly)
            duration = movie_data.get("duration", "")
            if not duration and movie_data.get("time_duration"):
                duration = movie_data.get("time_duration")
            new_row.Cells(movie_columns["TIME_DURATION"] + 1).Range.Text = duration
            
            # Handle genres
            genre = movie_data.get("genre", "")
            if not genre:
                genre = movie_data.get("genres", "")
            new_row.Cells(movie_columns["GENRE"] + 1).Range.Text = genre
            
            # Set watch date from data or use today
            if movie_data.get("watch_date"):
                new_row.Cells(movie_columns["WATCH_DATE"] + 1).Range.Text = movie_data.get("watch_date")
            else:
                today = datetime.datetime.now().strftime("%b %d, %Y")
                new_row.Cells(movie_columns["WATCH_DATE"] + 1).Range.Text = today
            
            # Release date
            new_row.Cells(movie_columns["RELEASE_DATE"] + 1).Range.Text = movie_data.get("release_date", "")
            
            # User rating - properly formatted X.X/10
            user_rating = movie_data.get("user_rating", "")
            new_row.Cells(movie_columns["RATE"] + 1).Range.Text = user_rating
            
            # IMDb rating - in separate column
            imdb_rating = movie_data.get("imdb_rating", "")
            new_row.Cells(movie_columns["IMDB_RATING"] + 1).Range.Text = imdb_rating
            
            # RT rating - in separate column (percentage)
            rt_rating = movie_data.get("rt_rating", "")
            # Remove percentage sign for numeric column if needed
            if rt_rating and rt_rating.endswith("%"):
                rt_value = rt_rating.replace("%", "")
                new_row.Cells(movie_columns["RT_RATING"] + 1).Range.Text = rt_value
            else:
                new_row.Cells(movie_columns["RT_RATING"] + 1).Range.Text = rt_rating
            
            # Handle rewatch status
            if "rewatch" in movie_data and movie_data["rewatch"]:
                current_text = new_row.Cells(movie_columns["IMDb_RATING"] + 1).Range.Text
                new_row.Cells(movie_columns["IMDb_RATING"] + 1).Range.Text = f"{current_text}\n(Rewatch)"
            
            return True
        except Exception as e:
            print(f"Error adding movie: {e}")
            return False
    
    def add_series(self, series_data, keep_open=True):
        """Add a new series entry to the table"""
        if not self.doc:
            if not self.open_document():
                return False
        
        try:
            series_table_index = settings.get_series_table_index()
            series_columns = settings.get_series_columns()
            
            table = self.doc.Tables(series_table_index)
            next_number = self.get_next_series_number()
            
            # Add new row
            new_row = table.Rows.Add()
            
            # Fill in data
            new_row.Cells(series_columns["NO"] + 1).Range.Text = str(next_number)
            
            # Series name - Title case (capitalize first letter of each word)
            title = series_data.get("title", "")
            if not title:
                title = series_data.get("name", "")
            title = title.title()  # Convert to title case (first letter of each word capitalized)
            new_row.Cells(series_columns["NAME"] + 1).Range.Text = title
            
            # Season information - allow multiple field names for compatibility
            season = series_data.get("season", "")
            if not season:
                season = series_data.get("seasons", "")
            new_row.Cells(series_columns["SEASON"] + 1).Range.Text = str(season)
            
            # Episode information
            episode = series_data.get("episode", "")
            if not episode:
                episode = series_data.get("episodes", "")
            new_row.Cells(series_columns["EPISODE"] + 1).Range.Text = str(episode)
            
            # Genre information
            genre = series_data.get("genre", "")
            if not genre:
                genre = series_data.get("genres", "")
            new_row.Cells(series_columns["GENRE"] + 1).Range.Text = genre
            
            # Starting date (when user started watching)
            start_date = series_data.get("start_date", "")
            if not start_date:
                start_date = series_data.get("starting_date", "")
                if not start_date:
                    start_date = series_data.get("watch_date", "")
            
            if start_date:
                new_row.Cells(series_columns["STARTING_DATE"] + 1).Range.Text = start_date
            else:
                # If start date is not available, leave it blank
                new_row.Cells(series_columns["STARTING_DATE"] + 1).Range.Text = ""
            
            # Finishing date
            finish_date = series_data.get("finish_date", "")
            if not finish_date:
                finish_date = series_data.get("finishing_date", "")
            
            # Only add finish date if it's provided and not empty
            if finish_date and finish_date.strip():
                new_row.Cells(series_columns["FINISHING_DATE"] + 1).Range.Text = finish_date
            else:
                new_row.Cells(series_columns["FINISHING_DATE"] + 1).Range.Text = ""
            
            # First episode air date
            first_air_date = series_data.get("first_air_date", "")
            if not first_air_date:
                first_air_date = series_data.get("first_episode_date", "")
            new_row.Cells(series_columns["FIRST_EPI_DATE"] + 1).Range.Text = first_air_date
            
            # User rating - ensure X/10 format
            user_rating = series_data.get("user_rating", "")
            if user_rating:
                # If rating doesn't already have /10 format, add it
                if isinstance(user_rating, (int, float)):
                    user_rating = f"{user_rating:.1f}/10"
                elif "/10" not in user_rating:
                    try:
                        # Try to convert to float and format
                        rating_value = float(user_rating.strip())
                        user_rating = f"{rating_value:.1f}/10"
                    except:
                        # If conversion fails, use as is
                        pass
                        
            new_row.Cells(series_columns["RATE"] + 1).Range.Text = user_rating
            
            # IMDb rating - ensure X/10 format
            imdb_rating = series_data.get("imdb_rating", "")
            if imdb_rating and "/10" not in imdb_rating:
                try:
                    # Try to convert to float and format
                    rating_value = float(imdb_rating.strip())
                    imdb_rating = f"{rating_value:.1f}/10"
                except:
                    # If conversion fails, use as is
                    pass
                    
            new_row.Cells(series_columns["IMDB_RATING"] + 1).Range.Text = imdb_rating
            
            # RT rating - ensure X% format
            rt_rating = series_data.get("rt_rating", "")
            if rt_rating and not rt_rating.endswith("%") and rt_rating.strip():
                # Try to clean up the rating to just the number
                rt_value = "".join([c for c in rt_rating if c.isdigit()])
                if rt_value:
                    rt_rating = f"{rt_value}%"
                    new_row.Cells(series_columns["RT_RATING"] + 1).Range.Text = rt_value
                else:
                    new_row.Cells(series_columns["RT_RATING"] + 1).Range.Text = rt_rating
            else:
                # If it already has % or is empty, use as is
                if rt_rating.endswith("%"):
                    # Remove percentage sign for numeric column
                    rt_value = rt_rating.replace("%", "")
                    new_row.Cells(series_columns["RT_RATING"] + 1).Range.Text = rt_value
                else:
                    new_row.Cells(series_columns["RT_RATING"] + 1).Range.Text = rt_rating
            
            # Finished status with coming season info
            is_finished = series_data.get("finished", False)
            coming_season = series_data.get("coming_season", "")
            
            if is_finished:
                finished_text = "Yes"
            else:
                if coming_season:
                    finished_text = f"No({coming_season})"
                else:
                    finished_text = "No"
                    
            new_row.Cells(series_columns["FINISHED"] + 1).Range.Text = finished_text
            
            # Progress information (if provided)
            if "progress" in series_data and series_data["progress"]:
                progress = series_data["progress"]
                # Add to either IMDb or RT column (whichever is empty)
                if not imdb_rating:
                    new_row.Cells(series_columns["IMDB_RATING"] + 1).Range.Text = f"Current: {progress}"
                elif not rt_rating:
                    new_row.Cells(series_columns["RT_RATING"] + 1).Range.Text = f"Current: {progress}"
            
            # Save document but keep it open if requested
            self.doc.Save()
            
            # Close the document if not keep_open
            if not keep_open:
                self.close_document(save=False)  # Already saved
            
            return True
        except Exception as e:
            print(f"Error adding series: {e}")
            return False 