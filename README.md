# 🎬 Movie and Series Tracker

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-brightgreen.svg)
![Version](https://img.shields.io/badge/version-1.2.0-orange.svg)

A beautiful and feature-rich application to track your watched movies and TV shows, with Word document integration for offline storage.

![App Screenshot](docs/images/app_screenshot.png)

## ✨ Features

- **🎥 Movie Tracking**: Search for movies, view details, and add them to your collection
- **📺 TV Series Tracking**: Keep track of your TV shows with season and episode progress
- **📊 Ratings**: Record your personal ratings and view IMDb/Rotten Tomatoes scores
- **📄 Word Integration**: Automatically save entries to a Word document for offline access
- **🌓 Dark/Light Theme**: Customizable appearance that respects your system preferences
- **📱 Modern UI**: Clean, intuitive interface built with CustomTkinter
- **📊 Document View**: View and edit your Word document data directly in the app
- **🔍 Powerful Search**: Find movies and shows using The Movie Database (TMDB) API
- **📤 Export Options**: Export your data to CSV for external use

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Microsoft Word (for document integration)
- Internet connection (for movie/series search)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/movie-tracker.git
   cd movie-tracker
   ```

2. Install required packages:
```
pip install -r requirements.txt
```

3. Configure API keys:
   - Get a free API key from [TMDB](https://www.themoviedb.org/settings/api)
   - Get a free API key from [OMDb](https://www.omdbapi.com/apikey.aspx)
   - Update `config.py` with your API keys

4. Set your Word document path in `config.py`

5. Run the application:
   ```
   python app.py
   ```

## 📋 Usage Guide

### Movies Section

1. **Search**: Enter a movie name and press Enter
2. **View Details**: Click on any movie from search results to see detailed information
3. **Add to Collection**: Click "Add to Collection" to add the movie to your list
4. **Save to Word**: Use the "Save to Word" option to add it to your Word document

### Series Section

1. **Search**: Enter a TV show name and press Enter
2. **View Details**: Click on any series from search results to see detailed information
3. **Track Progress**: Set your current season and episode when adding to collection
4. **Set Status**: Mark shows as Watching, Completed, On Hold, Dropped, or Plan to Watch

### Document View

1. **View Tables**: Browse your Word document tables directly in the app
2. **Edit Entries**: Double-click on any cell to edit its content
3. **Export Data**: Export your tables to CSV for use in other applications

### Settings

1. **Change Theme**: Switch between Light, Dark, and System themes
2. **API Keys**: Update your TMDB and OMDb API keys
3. **Document Path**: Change the path to your Word document
4. **Data Export**: Export your collection to CSV files
5. **Create Shortcut**: Create a desktop shortcut for quick access

## 🧰 Technical Details

The application is built using:

| Component | Technology |
|-----------|------------|
| UI Framework | CustomTkinter |
| Data Storage | JSON + Microsoft Word |
| API Integration | TMDB + OMDb |
| Image Handling | Pillow |
| Word Integration | win32com |
| Calendar/Date Picking | tkcalendar |

### File Structure

```
movie-tracker/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── movie_fetcher.py        # API integration for movies/series
├── word_handler.py         # Word document integration
├── requirements.txt        # Python dependencies
├── ui/                     # UI components
│   └── screens/            # Screen implementations
├── redesigned_ui/          # Enhanced UI components
│   ├── movies_screen.py    # Movies interface
│   ├── series_screen.py    # Series interface
│   └── document_view.py    # Word document viewer
├── data/                   # Local JSON storage
└── docs/                   # Documentation and resources
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [TMDB](https://www.themoviedb.org/) for their excellent movie and TV show database
- [OMDb](https://www.omdbapi.com/) for providing additional movie information
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI toolkit
- All open-source packages and libraries used in this project 

## 🔮 Future Enhancements

### Movies Section Improvements

1. **Statistics Dashboard**: Add a statistics view showing total movies watched, average rating, most watched genres, and viewing trends over time.

2. **Advanced Filtering/Sorting**: Allow users to filter search results by year, genre, rating range, or sort by different criteria (newest first, highest rated, etc.).

3. **Personal Notes**: Add a notes field where users can write personal thoughts about each movie that gets saved with their collection.

4. **Watch Later List**: Implement a "Watch Later" feature to save movies you're interested in but haven't watched yet.

5. **Movie Recommendations**: Add a recommendation engine that suggests movies based on your viewing history and ratings.

6. **Better Visualization**: Create visual representations of your movie watching habits with charts and graphs.

7. **Batch Export/Import**: Allow exporting the entire movie collection to CSV or importing from other services.

8. **Social Features**: Share favorite movies or recommendations with friends via email or social media.

9. **Keyboard Shortcuts**: Add keyboard shortcuts for common actions like search, add movie, etc.

10. **Search History**: Keep track of recent searches to easily return to previous results.

### Series Section Improvements

1. **Episode-by-Episode Tracking**: Mark individual episodes as watched within a series.
2. **Season Rating System**: Rate each season separately to track quality changes.
3. **Binge Calculator**: Calculate how long it would take to watch an entire series.
4. **Watch Status Categories**: Organize series by status: Watching, Completed, On Hold, Dropped, Plan to Watch.
5. **Character Tracker**: Keep notes on favorite characters and their development.
6. **Custom Episode Lists**: Create custom episode lists like "Essential Episodes" or "Skip These Episodes".
7. **Series Ranking**: Create and maintain ranked lists of your favorite series.
8. **Episode Reminder**: Set notifications for new episode releases.
9. **Network/Streaming Platform Filter**: Group series by their network or streaming platform.
10. **Series Progress Visualizer**: Graphical representation of your progress through different series.

### Document Section Improvements

1. **Multiple Document Templates**: Support for different Word templates for various tracking styles.
2. **PDF Export Option**: Export your collection as a nicely formatted PDF.
3. **Excel/CSV Export**: Export data in spreadsheet format for further analysis.
4. **Cover Page Generator**: Create customized cover pages for your media document.
5. **Quick Statistics Summary**: Automatically generate a summary page with key statistics.
6. **Auto-Backup System**: Schedule regular backups of your Word document.
7. **Version History**: Track changes to your document over time.
8. **Cloud Sync**: Automatically sync your document to cloud storage services.
9. **Custom Sections**: Create user-defined sections beyond just movies and series.
10. **Document Previewer**: Preview how the document will look before saving.

### Settings Section Improvements

1. **🚀 Desktop Shortcut Creator (URGENT)**: Create customizable desktop shortcuts with personalized icons that launch the application directly. Features include:
   - Custom application icon selection from built-in library or your own images
   - Configurable startup parameters (light/dark mode, specific section to open)
   - Application name customization for the desktop
   - Start menu integration with category selection
   - Task bar pinning option with custom hover text
   - Automatic shortcut updating when the application changes location

2. **🎨 Theme Customization Studio**: Build your perfect interface with:
   - Individual color controls for every UI element (backgrounds, buttons, text, borders)
   - Preset themes with day/night auto-switching based on time or system settings
   - Transparency and blur effects for modern glass-like interfaces
   - Custom animations and transition effects between screens
   - Export/import themes to share with other users

3. **⌨️ Keyboard Hotkeys Manager**: Boost your productivity with:
   - Fully customizable shortcuts for all application actions
   - Multi-key combination support with visual keyboard map
   - Profile switching for different usage scenarios (casual, power user)
   - Conflict detection and resolution between overlapping shortcuts
   - Quick reference overlay accessed via F1

4. **🔑 API Key Management System**: Securely handle your API connections:
   - Encrypted storage of TMDB/OMDB API keys
   - Usage monitoring with quota tracking and rate limit warnings
   - Automatic key rotation for improved security
   - Test connectivity button to verify API access
   - Proxy configuration for restricted networks

5. **💾 Data Control Center**: Take charge of your information:
   - Import from popular services (IMDb, Letterboxd, Trakt, etc.)
   - Export in multiple formats (JSON, CSV, XML, SQL)
   - Selective backup of specific data categories
   - Scheduled automatic backups to local or cloud storage
   - Data recovery tools for corrupted files

6. **🔄 Auto-Update Configuration**: Stay current with:
   - Update channel selection (stable, beta, development)
   - Scheduled update checks during off-hours
   - Bandwidth limiting for metered connections
   - Rollback capability to previous versions
   - Update notifications with detailed release notes

7. **🌐 Language & Regional Settings**: Personalize your experience:
   - Support for 15+ languages with community contribution tools
   - Region-specific content ratings systems (MPAA, BBFC, etc.)
   - Customizable date, time, and number formats
   - Right-to-left language support for Arabic, Hebrew, etc.
   - Built-in translation editor for contributing improvements

8. **📅 Date Format Customization**: Format dates your way:
   - Presets for international standards (US, EU, ISO, etc.)
   - Custom format builder with live preview
   - Relative date options ("Yesterday" instead of actual date)
   - Calendar system options (Gregorian, Lunar, etc.)
   - Consistent formatting across the app and exported documents

9. **🔔 Smart Notification Center**: Stay informed with:
   - Granular control over notification types and frequency
   - Custom sounds and visual styles for different alerts
   - Focus modes to temporarily silence non-critical notifications
   - Scheduled quiet hours for uninterrupted viewing
   - External notification integration with system tray

10. **📝 Document Formatting Studio**: Perfect your Word documents:
    - Field-by-field formatting rules (capitalization, truncation, etc.)
    - Custom header/footer templates with dynamic content
    - Conditional formatting based on ratings or other criteria
    - Font and styling presets for consistent documents
    - Table layout designer with drag-and-drop simplicity

11. **🔐 Privacy & Security Hub**: Protect your data:
    - Configurable data retention policies
    - Password protection for the application or specific sections
    - Private browsing mode that leaves no history
    - Data anonymization for statistics sharing
    - Complete data purging tools with secure deletion

12. **⚡ Performance Optimizer**: Fine-tune your experience:
    - Cache size management for optimal performance
    - Startup item selection to reduce loading time
    - Hardware acceleration toggles for different components
    - Memory usage monitoring and optimization
    - Offline mode settings for use without internet

### Overall Project Features

1. **Mobile Companion App**: Access your collection on-the-go with a synchronized mobile app.
2. **Browser Extension**: Quick-add media from streaming sites with a browser extension.
3. **Media Server Integration**: Connect with Plex, Emby, or Jellyfin to track your server content.
4. **Social Sharing**: Share ratings and reviews with friends or on social media.
5. **Trakt.tv Integration**: Sync with Trakt.tv for universal tracking across platforms.
6. **IMDb/Letterboxd Import**: Import your existing collections from other platforms.
7. **Watch Party Coordination**: Create virtual watch parties with friends.
8. **Achievement System**: Earn badges for milestones (100 movies watched, etc.).
9. **Smart Recommendations**: Get personalized recommendations based on your taste.
10. **Year in Review**: Generate an annual summary of your viewing habits.

## Settings Architecture

The application uses a centralized settings management system through the `SettingsHandler` class. This provides:

- **JSON-based configuration storage** - Settings are saved in a `config.json` file
- **Legacy support** - Can import settings from the old `config.py` file
- **Default values** - Sensible defaults for all settings
- **Easy access** - Simple get/set methods for accessing settings
- **Theme management** - Methods to control appearance mode and color theme
- **Table configuration** - Column mappings for Word document tables
- **Offline mode** - Use the app without internet by caching movie and series data

### Key Settings

- **API Keys** - TMDB and OMDB API keys
- **Word Document Path** - Path to your tracking Word document
- **Appearance Mode** - System/Light/Dark
- **Color Theme** - Blue, Green, Dark-Blue
- **Offline Mode** - Enable/disable offline functionality
- **Cache Size** - Control how many items to cache for offline use

## Usage

1. Install requirements: `pip install -r requirements.txt`
2. Run the application: `python main.py`
3. Enter your API keys in the Settings screen
4. Select your Word document
5. Start tracking your movies and TV shows!

## Requirements

- Python 3.6+
- customtkinter
- Pillow
- requests
- tkcalendar
- pywin32
- pandas 