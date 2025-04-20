# API Keys - Replace with your actual keys
TMDB_API_KEY = "8be0b2a820d07b03ef239072842c3ce6"  # Get from https://www.themoviedb.org/settings/api
OMDB_API_KEY = "bea763d2"  # Get from https://www.omdbapi.com/apikey.aspx

# Settings
WORD_DOC_PATH = r"C:\Users\HP\OneDrive\Desktop\Movies.docx"  # Update with your actual document path

# Table formatting settings
MOVIE_TABLE_INDEX = 2  # The movie table is the 2nd table in document (index starts at 1)
SERIES_TABLE_INDEX = 1  # The series table is the 1st table in document

# Column indices for movie table (0-based)
MOVIE_COLUMNS = {
    "NO": 0,
    "NAME": 1,
    "TIME_DURATION": 2,
    "GENRE": 3,
    "WATCH_DATE": 4,
    "RELEASE_DATE": 5,
    "RATE": 6,
    "IMDB_RATING": 7,
    "RT_RATING": 8
}

# Column indices for series table (0-based)
SERIES_COLUMNS = {
    "NO": 0,
    "NAME": 1,
    "SEASON": 2,
    "EPISODE": 3,
    "GENRE": 4,
    "STARTING_DATE": 5,
    "FINISHING_DATE": 6,
    "FIRST_EPI_DATE": 7,
    "RATE": 8,
    "IMDB_RATING": 9,
    "RT_RATING": 10,
    "FINISHED": 11
} 