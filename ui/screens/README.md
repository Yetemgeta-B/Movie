# Redesigned Movie and Series Tracker

This directory contains the redesigned UI for the Movie and Series Tracker application. The redesign focuses on simplicity and clean user experience while ensuring important functionality is preserved.

## Changes Implemented

1. **Clean Minimal Interface**
   - Removed all previously searched movies/series display
   - Removed sort by feature and other distractions
   - Created a clean welcome screen with clear instructions

2. **Enhanced Search Experience**
   - Shows a "Searching..." indicator during search operations
   - Results displayed with thumbnails and brief descriptions
   - Clear selection button to continue

3. **New Detail Selection Interface**
   - Custom dialog for adding items to collection
   - Watch date selector with today/custom date options and calendar
   - Rating slider for simple input
   - For series: added viewing status selection (Watching, Completed, etc.)

4. **Docx Integration**
   - Added separate columns for IMDb and Rotten Tomatoes ratings
   - Updates the document with all selected information

## Implementation Instructions

1. **Dependencies Installation**
   ```
   pip install tkcalendar
   ```

2. **File Replacement**
   Replace the existing UI screen implementations with these redesigned files:
   - `ui/screens/movies_screen.py` → Replace with `redesigned_ui/movies_screen.py`
   - `ui/screens/series_screen.py` → Replace with `redesigned_ui/series_screen.py`

3. **Word Handler Updates**
   Ensure your `word_handler.py` file properly handles separate IMDb and RT ratings when adding entries.

4. **App.py Integration**
   No changes needed to `app.py` as the screen class names remain the same.

## Usage

The new interface flow is:
1. User enters a search term in the search box and presses Enter
2. "Searching..." appears while results are fetched
3. Results display with thumbnails and descriptions
4. User clicks "Select" on their desired item
5. Detail dialog appears asking for:
   - Watch date (today or custom with calendar)
   - User rating (slider from 1-10)
   - For series: viewing status
6. User clicks "Add" and the item is added to both collection and Word document

## Notes

1. Make sure the `movie_fetcher.py` can properly handle both movies and TV series searches.
2. The `tkcalendar` package is required for the DateEntry widget.
3. Word documents should be properly formatted to include separate columns for IMDb and RT ratings. 