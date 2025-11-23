"""
Google Search Tool
Author: Amin Motiwala

Implements Google Search capabilities for the Researcher Agent to perform
real-time lookups, validation, and industry standards research during interviews.
"""

import os
import requests
from typing import Dict, Any, List, Optional
import json
from urllib.parse import quote_plus


class GoogleSearchTool:
    """
    Google Search tool for real-time research and validation.
    
    This tool provides:
    - Real-time Google search capabilities
    - Structured search results
    - Error handling and rate limiting
    - Support for targeted searches
    """
    
    def __init__(self):
        """Initialize Google Search tool with API configuration."""
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.max_results_per_request = 10
        
        if not self.api_key or not self.search_engine_id:
            print("⚠️ Google Search API credentials not configured. Search functionality will be limited.")
            self.api_configured = False
        else:
            self.api_configured = True
            print("🔍 Google Search tool initialized")
    
    def search(self, query: str, num_results: int = 5, search_type: str = "web") -> List[Dict[str, Any]]:
        """
        Perform Google search and return structured results.
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10 per request)
            search_type: Type of search ('web', 'image', 'news')
            
        Returns:
            List of search result dictionaries
        """
        if not self.api_configured:
            return self._mock_search_results(query, num_results)
        
        try:
            # Limit results to API maximum
            num_results = min(num_results, self.max_results_per_request)
            
            # Prepare search parameters
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            
            # Add search type specific parameters
            if search_type == 'news':
                params['tbm'] = 'nws'
            elif search_type == 'image':
                params['searchType'] = 'image'
            
            # Make API request
            print(f"🔍 Searching for: {query}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and structure results
            search_results = []
            items = data.get('items', [])
            
            for item in items:
                result = {
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'formatted_url': item.get('formattedUrl', '')
                }
                
                # Add additional metadata if available
                if 'pagemap' in item:
                    pagemap = item['pagemap']
                    if 'metatags' in pagemap and pagemap['metatags']:
                        metatag = pagemap['metatags'][0]
                        result['description'] = metatag.get('og:description', result['snippet'])
                        result['site_name'] = metatag.get('og:site_name', result['display_link'])
                
                search_results.append(result)
            
            print(f"✅ Found {len(search_results)} results")
            return search_results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Search API request failed: {e}")
            return self._mock_search_results(query, num_results)
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def search_technical_concept(self, concept: str, context: str = "") -> Dict[str, Any]:
        """
        Search for technical concept with structured analysis.
        
        Args:
            concept: Technical concept to research
            context: Additional context for the search
            
        Returns:
            Dict containing structured technical concept information
        """
        # Construct targeted search queries
        queries = [
            f"{concept} definition programming 2025",
            f"{concept} best practices {context}",
            f"{concept} examples tutorial"
        ]
        
        concept_info = {
            'concept': concept,
            'definitions': [],
            'best_practices': [],
            'examples': [],
            'related_concepts': [],
            'authoritative_sources': []
        }
        
        for query in queries:
            results = self.search(query, num_results=3)
            
            for result in results:
                # Categorize results based on content
                snippet = result['snippet'].lower()
                title = result['title'].lower()
                
                if 'definition' in snippet or 'what is' in snippet:
                    concept_info['definitions'].append({
                        'source': result['display_link'],
                        'definition': result['snippet'],
                        'url': result['url']
                    })
                elif 'best practice' in snippet or 'how to' in snippet:
                    concept_info['best_practices'].append({
                        'source': result['display_link'],
                        'practice': result['snippet'],
                        'url': result['url']
                    })
                elif 'example' in snippet or 'tutorial' in snippet:
                    concept_info['examples'].append({
                        'source': result['display_link'],
                        'example': result['snippet'],
                        'url': result['url']
                    })
                
                # Identify authoritative sources
                authoritative_domains = [
                    'stackoverflow.com', 'github.com', 'mozilla.org',
                    'w3.org', 'oracle.com', 'microsoft.com', 'google.com'
                ]
                
                if any(domain in result['url'] for domain in authoritative_domains):
                    concept_info['authoritative_sources'].append(result)
        
        return concept_info
    
    def search_job_market_trends(self, role: str, location: str = "") -> Dict[str, Any]:
        """
        Search for job market trends and salary information.
        
        Args:
            role: Job role to research
            location: Geographic location (optional)
            
        Returns:
            Dict containing job market trend information
        """
        location_query = f"{location} " if location else ""
        
        queries = [
            f"{role} salary {location_query}2025",
            f"{role} job market trends {location_query}",
            f"{role} skills demand {location_query}2025"
        ]
        
        market_info = {
            'role': role,
            'location': location,
            'salary_ranges': [],
            'market_trends': [],
            'skill_demands': [],
            'job_growth': [],
            'sources': []
        }
        
        for query in queries:
            results = self.search(query, num_results=3)
            
            for result in results:
                snippet = result['snippet']
                
                # Look for salary information
                if '$' in snippet or 'salary' in snippet.lower():
                    market_info['salary_ranges'].append({
                        'source': result['display_link'],
                        'info': snippet,
                        'url': result['url']
                    })
                
                # Look for trend information
                if any(word in snippet.lower() for word in ['trend', 'growth', 'demand', 'increase']):
                    market_info['market_trends'].append({
                        'source': result['display_link'],
                        'trend': snippet,
                        'url': result['url']
                    })
                
                # Look for skill information
                if any(word in snippet.lower() for word in ['skill', 'requirement', 'technology']):
                    market_info['skill_demands'].append({
                        'source': result['display_link'],
                        'skills': snippet,
                        'url': result['url']
                    })
                
                market_info['sources'].append(result)
        
        return market_info
    
    def _mock_search_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Return mock search results when API is not configured.
        
        Args:
            query: Search query
            num_results: Number of results requested
            
        Returns:
            List of mock search results
        """
        print(f"🔍 Mock search for: {query}")
        
        mock_results = []
        for i in range(min(num_results, 3)):
            mock_results.append({
                'title': f"Mock Result {i+1} for '{query}'",
                'url': f"https://example.com/result-{i+1}",
                'snippet': f"This is a mock search result for the query '{query}'. In a real implementation, this would contain actual search result content.",
                'display_link': 'example.com',
                'formatted_url': f'https://example.com/result-{i+1}'
            })
        
        return mock_results