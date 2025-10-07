import time
from typing import List, Dict, Optional
from dataforseo_client import DataForSEOClient
from web_crawler import WebCrawler
from google_ranking_client import GoogleRankingClient

class SearchEngine:
    def __init__(self):
        self.dataforseo_client = DataForSEOClient()
        self.web_crawler = WebCrawler()
        self.ranking_client = GoogleRankingClient()
    
    async def search(self, query: str, location: str = "United States", language: str = "en") -> Dict:
        """
        Main search function that orchestrates the entire process
        
        Args:
            query: Search query
            location: Geographic location for search
            language: Language for search
            
        Returns:
            Dictionary containing search results with rankings and metadata
        """
        start_time = time.time()
        
        # Step 1: Get SERP results from DataForSEO
        print(f"🔍 Fetching SERP results for query: '{query}'")
        serp_results = self.dataforseo_client.get_live_serp_results(query, location, language)
        
        if not serp_results:
            return {
                'query': query,
                'location': location,
                'language': language,
                'error': 'No SERP results found',
                'results': [],
                'metadata': {
                    'total_time_seconds': time.time() - start_time,
                    'serp_count': 0,
                    'crawled_count': 0,
                    'ranked_count': 0
                }
            }
        
        print(f"✅ Found {len(serp_results)} SERP results")
        
        # Step 2: Extract URLs for crawling
        urls_to_crawl = [result['url'] for result in serp_results if result.get('url')]
        
        if not urls_to_crawl:
            return {
                'query': query,
                'location': location,
                'language': language,
                'error': 'No valid URLs found in SERP results',
                'results': [],
                'metadata': {
                    'total_time_seconds': time.time() - start_time,
                    'serp_count': len(serp_results),
                    'crawled_count': 0,
                    'ranked_count': 0
                }
            }
        
        # Step 3: Crawl URLs to get content (using async-safe method)
        print(f"🕷️ Crawling {len(urls_to_crawl)} URLs...")
        crawl_start = time.time()
        crawled_content = await self.web_crawler.crawl_urls_async_safe(urls_to_crawl)
        crawl_time = time.time() - crawl_start
        print(f"✅ Crawling completed in {crawl_time:.2f} seconds")
        
        # Step 4: Combine SERP data with crawled content
        combined_results = []
        for i, serp_result in enumerate(serp_results):
            if i < len(crawled_content):
                crawl_data = crawled_content[i]
                combined_result = {
                    # Original SERP data
                    'serp_position': serp_result.get('position', i + 1),
                    'serp_title': serp_result.get('title', ''),
                    'serp_description': serp_result.get('description', ''),
                    'url': serp_result.get('url', ''),
                    'domain': serp_result.get('domain', ''),
                    'breadcrumb': serp_result.get('breadcrumb', ''),
                    'website_name': serp_result.get('website_name', ''),
                    
                    # Crawled content data
                    'title': crawl_data.get('title', ''),
                    'description': crawl_data.get('description', ''),
                    'content': crawl_data.get('content', ''),
                    'headings': crawl_data.get('headings', ''),
                    'word_count': crawl_data.get('word_count', 0),
                    'crawl_status': crawl_data.get('status', 'unknown'),
                    'crawl_status_code': crawl_data.get('status_code', 0),
                }
                combined_results.append(combined_result)
        
        successful_crawls = [r for r in combined_results if r.get('crawl_status') == 'success']
        print(f"✅ Successfully crawled {len(successful_crawls)} out of {len(combined_results)} pages")
        
        # Step 5: Rank content using Google Ranking API
        if successful_crawls:
            print(f"📊 Ranking content using Google Ranking API...")
            ranking_start = time.time()
            ranked_results = self.ranking_client.rank_documents(query, successful_crawls)
            ranking_time = time.time() - ranking_start
            print(f"✅ Ranking completed in {ranking_time:.2f} seconds")
        else:
            print("⚠️ No successful crawls to rank")
            ranked_results = combined_results
        
        # Step 6: Add failed crawls back to results (without ranking scores)
        failed_crawls = [r for r in combined_results if r.get('crawl_status') != 'success']
        for failed in failed_crawls:
            failed['ranking_score'] = 0.0
            failed['original_position'] = failed.get('serp_position', 0)
        
        all_results = ranked_results + failed_crawls
        
        # Sort by ranking score (successful crawls first, then by original position)
        all_results.sort(key=lambda x: (-x.get('ranking_score', 0), x.get('original_position', 999)))
        
        total_time = time.time() - start_time
        
        return {
            'query': query,
            'location': location,
            'language': language,
            'results': all_results,
            'metadata': {
                'total_time_seconds': round(total_time, 2),
                'crawl_time_seconds': round(crawl_time, 2),
                'ranking_time_seconds': round(ranking_time if 'ranking_time' in locals() else 0, 2),
                'serp_count': len(serp_results),
                'crawled_count': len(combined_results),
                'successful_crawls': len(successful_crawls),
                'ranked_count': len(ranked_results) if ranked_results else 0,
                'total_results': len(all_results),
                'google_ranking_api_used': len(successful_crawls) > 0
            }
        }
    
    def get_search_summary(self, search_results: Dict) -> Dict:
        """
        Generate a summary of search results
        """
        # Always return the expected structure, even for empty results
        if not search_results.get('results'):
            return {
                'query': search_results.get('query', ''),
                'total_results': 0,
                'successfully_ranked': 0,
                'top_ranked_url': None,
                'top_ranking_score': 0,
                'average_ranking_score': 0,
                'domains_found': 0,
                'total_word_count': 0,
                'processing_time': search_results.get('metadata', {}).get('total_time_seconds', 0)
            }
        
        results = search_results['results']
        successful_results = [r for r in results if r.get('ranking_score', 0) > 0]
        
        summary = {
            'query': search_results.get('query', ''),
            'total_results': len(results),
            'successfully_ranked': len(successful_results),
            'top_ranked_url': successful_results[0]['url'] if successful_results else None,
            'top_ranking_score': successful_results[0]['ranking_score'] if successful_results else 0,
            'average_ranking_score': round(
                sum(r.get('ranking_score', 0) for r in successful_results) / len(successful_results), 3
            ) if successful_results else 0,
            'domains_found': len(set(r.get('domain', '') for r in results if r.get('domain'))),
            'total_word_count': sum(r.get('word_count', 0) for r in results),
            'processing_time': search_results.get('metadata', {}).get('total_time_seconds', 0)
        }
        
        return summary
    
    def test_all_services(self) -> Dict:
        """
        Test connectivity to all external services
        """
        tests = {
            'dataforseo': False,
            'google_ranking': False,
            'web_crawler': True  # Always available
        }
        
        # Test DataForSEO (simple check if credentials are configured)
        if (self.dataforseo_client.login and 
            self.dataforseo_client.password):
            tests['dataforseo'] = True
        
        # Test Google Ranking API
        tests['google_ranking'] = self.ranking_client.test_connection()
        
        return tests 