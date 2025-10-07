import requests
import json
from typing import List, Dict, Optional
from config import Config

class DataForSEOClient:
    def __init__(self):
        self.login = Config.DATAFORSEO_LOGIN
        self.password = Config.DATAFORSEO_PASSWORD
        self.base_url = Config.DATAFORSEO_BASE_URL
        
    def get_live_serp_results(self, query: str, location: str = "United States", language: str = "en") -> List[Dict]:
        """
        Fetch live SERP results from DataForSEO API
        
        Args:
            query: Search query
            location: Location for search (default: United States)
            language: Language for search (default: en)
            
        Returns:
            List of search result dictionaries
        """
        url = f"{self.base_url}/serp/google/organic/live/advanced"
        
        payload = [{
            "keyword": query,
            "location_name": location,
            "language_code": language,
            "device": "desktop",
            "os": "windows",
            "depth": 20  # Get first 20 results
        }]
        
        try:
            response = requests.post(
                url,
                auth=(self.login, self.password),
                headers={'content-type': 'application/json'},
                data=json.dumps(payload),
                timeout=Config.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status_code') == 20000:
                # Extract organic results
                tasks = data.get('tasks', [])
                if tasks and tasks[0].get('status_code') == 20000 and tasks[0].get('result'):
                    items = tasks[0]['result'][0].get('items', [])
                    # Filter only organic results and extract relevant data
                    organic_results = []
                    for item in items:
                        if item.get('type') == 'organic':
                            organic_results.append({
                                'position': item.get('rank_group', 0),
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'description': item.get('description', ''),
                                'domain': item.get('domain', ''),
                                'breadcrumb': item.get('breadcrumb', ''),
                                'website_name': item.get('website_name', '')
                            })
                    return organic_results
                else:
                    # Check if there's a task-level error
                    if tasks and tasks[0].get('status_code') != 20000:
                        print(f"DataForSEO Task Error: {tasks[0].get('status_message', 'Unknown task error')}")
                    else:
                        print("No results found in API response")
                    return []
            else:
                print(f"API Error: {data.get('status_message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_location_code(self, location_name: str) -> Optional[int]:
        """
        Get location code for a given location name
        """
        url = f"{self.base_url}/serp/google/locations"
        
        try:
            response = requests.get(
                url,
                auth=(self.login, self.password),
                timeout=Config.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status_code') == 20000:
                tasks = data.get('tasks', [])
                if tasks and tasks[0].get('result'):
                    locations = tasks[0]['result']
                    for location in locations:
                        if location.get('location_name', '').lower() == location_name.lower():
                            return location.get('location_code')
            
            return None
            
        except Exception as e:
            print(f"Error getting location code: {e}")
            return None 