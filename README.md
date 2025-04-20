# 🎬 Movie Tracker

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)

A modern desktop application for tracking movies and TV series, with comprehensive details and Word document integration.

## 📋 Overview

Movie Tracker is a feature-rich application that helps you:
- Search for movies and TV shows using TMDB and OMDB APIs
- View detailed information about movies and series
- Track your personal ratings and watch dates
- Save entries to a Microsoft Word document
- Use a clean, modern interface built with CustomTkinter

## ✨ Key Features

### 🎬 Movies
- Search global movie database (TMDB)
- View comprehensive details (cast, director, ratings)
- Add movies to your collection with custom ratings
- Save movie information to Word document
- See IMDb and Rotten Tomatoes ratings

### 📺 TV Series
- Track TV shows with detailed information
- View upcoming episodes with countdown timer
- See cast, genres, and creators
- Save series to Word document
- Track personal ratings

### 📝 Document Integration
- Save entries to Microsoft Word
- Proper formatting and columns
- Keeps Word file open after saving
- Show success indicators

### 🌙 User Interface
- Modern, clean design with CustomTkinter
- Light and dark mode support
- Responsive layout
- Desktop shortcut creation

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Microsoft Word (for document integration)
- Internet connection (for movie/series search)
- Windows OS

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Yetemgeta-B/Movie.git
   cd Movie
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up API keys:
   - Get a free API key from [TMDB](https://www.themoviedb.org/settings/api)
   - Get a free API key from [OMDb](https://www.omdbapi.com/apikey.aspx)
   - Add these keys to `config.py`

4. Run the application:
   ```
   python main.py
   ```

5. Create a desktop shortcut (optional):
   ```
   python create_shortcut.py
   ```

## 📁 Project Structure

```
Movie-Tracker/
├── main.py              # Application entry point
├── app.py               # Core application logic
├── gui.py               # GUI components
├── movie_fetcher.py     # API integration
├── word_handler.py      # Word document integration
├── settings_handler.py  # Settings management
├── config.py            # Configuration settings
├── create_shortcut.py   # Desktop shortcut creator
├── ui/                  # UI components and screens
├── redesigned_ui/       # Enhanced UI components
└── data/                # Local storage
```

## 📷 Screenshots

*Screenshots will be added here*

## 🧠 How It Works

1. **Search**: Enter a movie or series name in the search box
2. **View Details**: Click on a search result to see comprehensive information
3. **Add to Collection**: Click "Save to Word" to add to your document
4. **Rate**: Set your personal rating before saving

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [TMDB](https://www.themoviedb.org/) for their comprehensive movie and TV API
- [OMDb API](https://www.omdbapi.com/) for additional movie information
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern UI components
- All open-source packages used in this project 