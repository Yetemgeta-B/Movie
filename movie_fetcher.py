import requests
import datetime
import json
import os
from pathlib import Path
from settings_handler import settings

class MovieFetcher:
    def __init__(self):
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.omdb_base_url = "http://www.omdbapi.com/"
        
        # Create cache directory if it doesn't exist
        self.cache_dir = Path("data/cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_path(self, cache_type, query):
        """Get the path to a cache file"""
        # Create a safe filename from the query
        safe_query = "".join(c if c.isalnum() else "_" for c in query)
        return self.cache_dir / f"{cache_type}_{safe_query}.json"
        
    def _save_to_cache(self, cache_type, query, data):
        """Save data to cache file"""
        try:
            cache_path = self._get_cache_path(cache_type, query)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "data": data
                }, f)
            return True
        except Exception as e:
            print(f"Error saving to cache: {e}")
            return False
            
    def _load_from_cache(self, cache_type, query):
        """Load data from cache file"""
        try:
            cache_path = self._get_cache_path(cache_type, query)
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                return cached_data.get("data", [])
            return None
        except Exception as e:
            print(f"Error loading from cache: {e}")
            return None
        
    def search_media(self, query, media_type=None):
        """
        Search for movies or TV shows based on query
        media_type: 'movie', 'tv', or None (for both)
        """
        # Check if offline mode is enabled
        if settings.is_offline_mode():
            cache_key = f"search_{media_type}" if media_type else "search_multi"
            cached_results = self._load_from_cache(cache_key, query)
            if cached_results:
                print(f"Using cached results for '{query}'")
                return cached_results
            else:
                print(f"No cached results for '{query}' in offline mode")
                return []
        
        tmdb_api_key = settings.get("TMDB_API_KEY", "")
        if not tmdb_api_key:
            print("TMDB API key is missing")
            return []
            
        if media_type:
            endpoint = f"{self.tmdb_base_url}/search/{media_type}"
        else:
            endpoint = f"{self.tmdb_base_url}/search/multi"
            
        params = {
            "api_key": tmdb_api_key,
            "query": query,
            "include_adult": "false"
        }
        
        try:
            print(f"Searching for '{query}' using endpoint: {endpoint}")
            response = requests.get(endpoint, params=params, timeout=10)
            
            # Print response details for debugging
            print(f"Response status: {response.status_code}")
            
            # Check for API specific errors
            if response.status_code == 401:
                print("API key invalid or expired")
                return []
                
            if response.status_code == 404:
                print("Resource not found")
                return []
            
            response.raise_for_status()
            
            # Get and parse JSON response
            response_data = response.json()
            
            # Check for API error messages
            if 'success' in response_data and response_data['success'] is False:
                error_message = response_data.get('status_message', 'Unknown API error')
                print(f"API Error: {error_message}")
                return []
                
            results = response_data.get("results", [])
            
            # Log search results for debugging
            print(f"Search found {len(results)} results for '{query}'")
            
            # Format the results
            formatted_results = []
            for item in results:
                # For multi search
                media_type_value = item.get("media_type", media_type)
                
                if media_type_value == "movie" or media_type == "movie":
                    formatted_results.append({
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "name": item.get("title"),  # Add name for consistency
                        "type": "movie",
                        "release_date": item.get("release_date"),
                        "poster_path": item.get("poster_path"),
                        "overview": item.get("overview", "")
                    })
                elif media_type_value == "tv" or media_type == "tv":
                    formatted_results.append({
                        "id": item.get("id"),
                        "title": item.get("name"),  # Add title for consistency
                        "name": item.get("name"),
                        "type": "tv",
                        "first_air_date": item.get("first_air_date"),
                        "poster_path": item.get("poster_path"),
                        "overview": item.get("overview", "")
                    })
            
            # Log formatted results
            print(f"Formatted {len(formatted_results)} results")
            
            # Save to cache
            cache_key = f"search_{media_type}" if media_type else "search_multi"
            self._save_to_cache(cache_key, query, formatted_results)
            
            return formatted_results
        except requests.RequestException as e:
            print(f"Error searching for media: {e}")
            return []
    
    def get_movie_details(self, movie_id):
        """Get detailed information about a movie from TMDB and OMDB"""
        # Check if offline mode is enabled
        if settings.is_offline_mode():
            cached_details = self._load_from_cache("movie_details", str(movie_id))
            if cached_details:
                print(f"Using cached details for movie ID {movie_id}")
                return cached_details
            else:
                print(f"No cached details for movie ID {movie_id} in offline mode")
                return {}
        
        # Get basic details from TMDB
        tmdb_api_key = settings.get("TMDB_API_KEY", "")
        omdb_api_key = settings.get("OMDB_API_KEY", "")
        
        tmdb_endpoint = f"{self.tmdb_base_url}/movie/{movie_id}"
        params = {
            "api_key": tmdb_api_key,
            "append_to_response": "credits,release_dates"
        }
        
        try:
            print(f"Fetching movie details for ID: {movie_id}")
            tmdb_response = requests.get(tmdb_endpoint, params=params, timeout=10)
            
            # Check for API specific errors
            if tmdb_response.status_code == 401:
                print("TMDB API key invalid or expired")
                return {}
                
            if tmdb_response.status_code == 404:
                print("Movie not found")
                return {}
                
            tmdb_response.raise_for_status()
            tmdb_data = tmdb_response.json()
            
            # Extract IMDb ID to query OMDB
            imdb_id = tmdb_data.get("imdb_id")
            
            if not imdb_id:
                print("No IMDb ID found for this movie")
                
            # Get additional details from OMDB using IMDb ID
            omdb_params = {
                "apikey": omdb_api_key,
                "i": imdb_id
            }
            
            omdb_data = {}
            if imdb_id:
                try:
                    print(f"Fetching OMDB data for IMDb ID: {imdb_id}")
                    omdb_response = requests.get(self.omdb_base_url, params=omdb_params, timeout=10)
                    
                    if omdb_response.status_code == 401:
                        print("OMDB API key invalid or expired")
                    elif omdb_response.status_code == 404:
                        print("Movie not found in OMDB")
                    else:
                        omdb_response.raise_for_status()
                        omdb_data = omdb_response.json()
                        
                        # Check if there's an error in OMDB response
                        if omdb_data.get("Response") == "False":
                            print(f"OMDB Error: {omdb_data.get('Error', 'Unknown error')}")
                            omdb_data = {}
                except Exception as e:
                    print(f"Error fetching from OMDB: {e}")
                    omdb_data = {}
            
            # Format runtime as "1h 43m"
            runtime_minutes = tmdb_data.get("runtime", 0)
            hours = runtime_minutes // 60
            minutes = runtime_minutes % 60
            formatted_runtime = f"{hours}h {minutes}m"
            
            # Format the release date in "Mar 12, 2025" format
            release_date = tmdb_data.get("release_date", "")
            if release_date:
                date_obj = datetime.datetime.strptime(release_date, "%Y-%m-%d")
                formatted_release_date = date_obj.strftime("%b %d, %Y")
            else:
                formatted_release_date = ""
                
            # Extract ratings
            imdb_rating = omdb_data.get("imdbRating", "")
            imdb_score = f"{imdb_rating}/10" if imdb_rating and imdb_rating != "N/A" else ""
            
            rt_rating = ""
            for rating in omdb_data.get("Ratings", []):
                if rating.get("Source") == "Rotten Tomatoes":
                    rt_rating = rating.get("Value", "")
            
            # Format the genres - ensure at least 2 descriptors with fallbacks
            genre_list = [genre.get("name") for genre in tmdb_data.get("genres", [])]
            
            # If only one genre, use a fallback
            if len(genre_list) == 1:
                # Try to get more specific subgenre from OMDB
                omdb_genres = omdb_data.get("Genre", "").split(", ")
                if len(omdb_genres) > 1 and omdb_genres[0] != "N/A":
                    # Use OMDB genres if available
                    genre_list = omdb_genres[:2]
                else:
                    # Add a fallback secondary genre
                    primary_genre = genre_list[0]
                    if primary_genre == "Action":
                        genre_list.append("Thriller")
                    elif primary_genre == "Comedy":
                        genre_list.append("Drama")
                    elif primary_genre == "Drama":
                        genre_list.append("Thriller")
                    elif primary_genre == "Horror":
                        genre_list.append("Thriller")
                    elif primary_genre == "Science Fiction":
                        genre_list.append("Action")
                    else:
                        genre_list.append("Drama")
            
            # Limit to 2 genres
            genre_list = genre_list[:2]
            genres = "/".join(genre_list)
            
            # Extract director information from credits
            director = ""
            if "credits" in tmdb_data and "crew" in tmdb_data["credits"]:
                directors = [person.get("name") for person in tmdb_data["credits"]["crew"] 
                           if person.get("job") == "Director"]
                if directors:
                    director = ", ".join(directors[:2])  # Limit to 2 directors
            
            # If no director found in TMDB, try OMDB
            if not director and "Director" in omdb_data and omdb_data["Director"] != "N/A":
                director = omdb_data["Director"]
                
            # Extract main cast (actors)
            cast = ""
            if "credits" in tmdb_data and "cast" in tmdb_data["credits"]:
                actors = [person.get("name") for person in tmdb_data["credits"]["cast"][:6]]
                if actors:
                    cast = ", ".join(actors)
            
            # If no cast found in TMDB, try OMDB
            if not cast and "Actors" in omdb_data and omdb_data["Actors"] != "N/A":
                cast = omdb_data["Actors"]
            
            # Format title in title case
            title = tmdb_data.get("title", "").title()
            
            # Build comprehensive detail dictionary
            result = {
                "title": title,
                "runtime": runtime_minutes,
                "duration": formatted_runtime,
                "genres": genres,
                "release_date": formatted_release_date,
                "director": director,
                "cast": cast,
                "imdb_rating": imdb_score,
                "rt_rating": rt_rating,
                "combined_rating": f"{imdb_score} {rt_rating}",
                "imdb_id": imdb_id,
                "tagline": tmdb_data.get("tagline", "")
            }
            
            # Add budget and revenue if available
            if "budget" in tmdb_data and tmdb_data["budget"]:
                result["budget"] = f"${tmdb_data['budget']:,}"
            
            if "revenue" in tmdb_data and tmdb_data["revenue"]:
                result["revenue"] = f"${tmdb_data['revenue']:,}"
            
            # Save to cache
            self._save_to_cache("movie_details", str(movie_id), result)
                
            return result
            
        except requests.RequestException as e:
            print(f"Error fetching movie details: {e}")
            return {}
    
    def get_omdb_details(self, imdb_id):
        """Get detailed information from OMDB API using IMDb ID"""
        if not settings.get("OMDB_API_KEY", "") or not imdb_id:
            return {}
            
        # Get details from OMDB using IMDb ID
        omdb_params = {
            "apikey": settings.get("OMDB_API_KEY", ""),
            "i": imdb_id
        }
        
        try:
            print(f"Fetching OMDB data for IMDb ID: {imdb_id}")
            omdb_response = requests.get(self.omdb_base_url, params=omdb_params, timeout=10)
            
            if omdb_response.status_code == 401:
                print("OMDB API key invalid or expired")
                return {}
            elif omdb_response.status_code == 404:
                print("Item not found in OMDB")
                return {}
            else:
                omdb_response.raise_for_status()
                omdb_data = omdb_response.json()
                
                # Check if there's an error in OMDB response
                if omdb_data.get("Response") == "False":
                    print(f"OMDB Error: {omdb_data.get('Error', 'Unknown error')}")
                    return {}
                    
                return omdb_data
        except Exception as e:
            print(f"Error fetching from OMDB: {e}")
            return {}
    
    def get_series_details(self, tv_id, include_cast=False, include_external=False):
        """
        Get detailed information about a TV series
        
        Args:
            tv_id: The TMDB ID of the TV series
            include_cast: Whether to include detailed cast information
            include_external: Whether to include external API data like OMDB
        
        Returns:
            Dictionary with series details
        """
        # Check if offline mode is enabled
        if settings.is_offline_mode():
            cached_details = self._load_from_cache("series_details", str(tv_id))
            if cached_details:
                print(f"Using cached details for series ID {tv_id}")
                return cached_details
            else:
                print(f"No cached details for series ID {tv_id} in offline mode")
                return {}
                
        # Get basic details from TMDB
        tmdb_endpoint = f"{self.tmdb_base_url}/tv/{tv_id}"
        
        # Build the append_to_response parameter based on what we need
        append_to_response = ["external_ids", "next_episode_to_air", "last_episode_to_air"]
        
        if include_cast:
            append_to_response.append("credits")
            append_to_response.append("aggregate_credits")  # More complete cast list
        
        params = {
            "api_key": settings.get("TMDB_API_KEY", ""),
            "append_to_response": ",".join(append_to_response)
        }
        
        try:
            print(f"Fetching TV series details for ID: {tv_id}")
            tmdb_response = requests.get(tmdb_endpoint, params=params, timeout=10)
            
            # Check for API specific errors
            if tmdb_response.status_code == 401:
                print("TMDB API key invalid or expired")
                return {}
                
            if tmdb_response.status_code == 404:
                print("TV series not found")
                return {}
                
            tmdb_response.raise_for_status()
            tmdb_data = tmdb_response.json()
            
            # Extract IMDb ID
            imdb_id = tmdb_data.get("external_ids", {}).get("imdb_id")
            
            if not imdb_id:
                print("No IMDb ID found for this TV series")
            
            # Get additional details from OMDB if requested
            omdb_data = {}
            if include_external and imdb_id:
                omdb_data = self.get_omdb_details(imdb_id)
            
            # Format the first air date in "Mar 12, 2025" format
            first_air_date = tmdb_data.get("first_air_date", "")
            if first_air_date:
                date_obj = datetime.datetime.strptime(first_air_date, "%Y-%m-%d")
                formatted_first_air_date = date_obj.strftime("%b %d, %Y")
            else:
                formatted_first_air_date = ""
                
            # Extract ratings
            imdb_rating = omdb_data.get("imdbRating", "")
            imdb_score = f"{imdb_rating}/10" if imdb_rating and imdb_rating != "N/A" else ""
            
            rt_rating = ""
            for rating in omdb_data.get("Ratings", []):
                if rating.get("Source") == "Rotten Tomatoes":
                    rt_rating = rating.get("Value", "")
            
            # Format the genres
            genre_list = [genre.get("name") for genre in tmdb_data.get("genres", [])]
            
            # If only one genre, try to get more from OMDB
            if len(genre_list) <= 1 and omdb_data:
                omdb_genres = omdb_data.get("Genre", "").split(", ")
                if len(omdb_genres) > 1 and omdb_genres[0] != "N/A":
                    # Use OMDB genres if available
                    genre_list = omdb_genres[:3]
            
            # Format genres as a string
            genres = "/".join(genre_list[:3])
            
            # Get series creator
            creator = ""
            if "created_by" in tmdb_data and tmdb_data["created_by"]:
                creator_names = [person.get("name", "") for person in tmdb_data["created_by"]]
                creator = ", ".join(creator_names)
            
            # Get director from OMDB if no creator found
            if not creator and "Director" in omdb_data and omdb_data["Director"] != "N/A":
                creator = omdb_data["Director"]
            
            # Extract cast members
            cast = ""
            # Use aggregate_credits for a more complete cast list if available
            if include_cast and "aggregate_credits" in tmdb_data and "cast" in tmdb_data["aggregate_credits"]:
                cast_members = [person.get("name", "") for person in tmdb_data["aggregate_credits"]["cast"][:8]]
                cast = ", ".join(cast_members)
            # Fall back to regular credits if aggregate not available
            elif include_cast and "credits" in tmdb_data and "cast" in tmdb_data["credits"]:
                cast_members = [person.get("name", "") for person in tmdb_data["credits"]["cast"][:8]]
                cast = ", ".join(cast_members)
            # If no cast found in TMDB, try OMDB
            elif omdb_data and "Actors" in omdb_data and omdb_data["Actors"] != "N/A":
                cast = omdb_data["Actors"]
                
            # Get upcoming episode information if available
            upcoming_info = ""
            upcoming_date = ""
            if "next_episode_to_air" in tmdb_data and tmdb_data["next_episode_to_air"]:
                next_ep = tmdb_data["next_episode_to_air"]
                if "air_date" in next_ep and next_ep["air_date"]:
                    try:
                        date_obj = datetime.datetime.strptime(next_ep["air_date"], "%Y-%m-%d")
                        upcoming_date = date_obj.strftime("%b %d, %Y")
                    except:
                        upcoming_date = next_ep["air_date"]
                        
                season_num = next_ep.get("season_number", "?")
                episode_num = next_ep.get("episode_number", "?")
                episode_name = next_ep.get("name", "Upcoming Episode")
                
                upcoming_info = f"S{season_num}E{episode_num}: {episode_name}"
                
            # Get last aired episode information if available
            last_episode_info = ""
            if "last_episode_to_air" in tmdb_data and tmdb_data["last_episode_to_air"]:
                last_ep = tmdb_data["last_episode_to_air"]
                if "air_date" in last_ep and last_ep["air_date"]:
                    try:
                        date_obj = datetime.datetime.strptime(last_ep["air_date"], "%Y-%m-%d")
                        last_air_date = date_obj.strftime("%b %d, %Y")
                    except:
                        last_air_date = last_ep["air_date"]
                        
                season_num = last_ep.get("season_number", "?")
                episode_num = last_ep.get("episode_number", "?")
                episode_name = last_ep.get("name", "Last Episode")
                
                last_episode_info = f"S{season_num}E{episode_num}: {episode_name} ({last_air_date})"
            
            # Check if the show is finished
            status = tmdb_data.get("status", "Unknown")
            is_finished = status.lower() == "ended" or status.lower() == "canceled"
            
            result = {
                "title": tmdb_data.get("name", ""),
                "name": tmdb_data.get("name", ""),
                "number_of_seasons": tmdb_data.get("number_of_seasons", 0),
                "number_of_episodes": tmdb_data.get("number_of_episodes", 0),
                "genres": genres,
                "creator": creator,
                "cast": cast,
                "first_air_date": formatted_first_air_date,
                "imdb_rating": imdb_score,
                "rt_rating": rt_rating,
                "poster_path": tmdb_data.get("poster_path"),
                "overview": tmdb_data.get("overview", ""),
                "imdb_id": imdb_id,
                "status": status,
                "is_finished": is_finished,
                "upcoming_episode": upcoming_info,
                "upcoming_date": upcoming_date,
                "last_episode": last_episode_info,
                "network": ", ".join([network.get("name", "") for network in tmdb_data.get("networks", [])])
            }
            
            # Save to cache
            self._save_to_cache("series_details", str(tv_id), result)
            
            return result
            
        except requests.RequestException as e:
            print(f"Error fetching TV details: {e}")
            return {}
            
    def get_series_upcoming_episodes(self, tv_id):
        """
        Get more detailed information about upcoming episodes for a series
        
        Args:
            tv_id: The TMDB ID of the TV series
            
        Returns:
            Dictionary with upcoming episode details
        """
        if not settings.get("TMDB_API_KEY", ""):
            return {}
            
        try:
            # First get the current season number
            series_endpoint = f"{self.tmdb_base_url}/tv/{tv_id}"
            params = {
                "api_key": settings.get("TMDB_API_KEY", ""),
                "append_to_response": "next_episode_to_air"
            }
            
            series_response = requests.get(series_endpoint, params=params, timeout=10)
            series_response.raise_for_status()
            series_data = series_response.json()
            
            # Check if we have a next episode
            if "next_episode_to_air" not in series_data or not series_data["next_episode_to_air"]:
                return {}
                
            next_episode = series_data["next_episode_to_air"]
            current_season = next_episode.get("season_number")
            
            if not current_season:
                return {}
                
            # Get the full season details to see all upcoming episodes
            season_endpoint = f"{self.tmdb_base_url}/tv/{tv_id}/season/{current_season}"
            season_params = {
                "api_key": settings.get("TMDB_API_KEY", "")
            }
            
            season_response = requests.get(season_endpoint, params=season_params, timeout=10)
            season_response.raise_for_status()
            season_data = season_response.json()
            
            # Find all episodes that haven't aired yet
            today = datetime.datetime.now().date()
            upcoming_episodes = []
            
            for episode in season_data.get("episodes", []):
                if not episode.get("air_date"):
                    continue
                    
                try:
                    air_date = datetime.datetime.strptime(episode["air_date"], "%Y-%m-%d").date()
                    if air_date >= today:
                        # Format for display
                        formatted_date = air_date.strftime("%b %d, %Y")
                        episode_num = episode.get("episode_number", "?")
                        episode_name = episode.get("name", "Upcoming Episode")
                        
                        upcoming_episodes.append({
                            "season": current_season,
                            "episode": episode_num,
                            "name": episode_name,
                            "air_date": formatted_date,
                            "days_until": (air_date - today).days
                        })
                except Exception as e:
                    print(f"Error processing episode date: {e}")
                    
            # Sort by air date
            upcoming_episodes.sort(key=lambda x: x.get("days_until", 999))
            
            # Return formatted details
            if upcoming_episodes:
                next_ep = upcoming_episodes[0]
                
                # Format the episode information
                upcoming_info = f"S{next_ep['season']}E{next_ep['episode']}: {next_ep['name']}"
                upcoming_date = next_ep["air_date"]
                days_until = next_ep["days_until"]
                
                return {
                    "upcoming_episode": upcoming_info,
                    "upcoming_date": upcoming_date,
                    "days_until": days_until,
                    "future_episodes": len(upcoming_episodes),
                    "season_in_progress": current_season
                }
                
            return {}
            
        except Exception as e:
            print(f"Error fetching upcoming episodes: {e}")
            return {} 