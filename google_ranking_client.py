import os
from google.cloud import discoveryengine_v1 as discoveryengine
from typing import List, Dict, Optional
from config import Config

class GoogleRankingClient:
    def __init__(self):
        self.project_id = Config.GOOGLE_CLOUD_PROJECT_ID
        self.location = Config.GOOGLE_RANKING_LOCATION
        self.ranking_config = Config.GOOGLE_RANKING_CONFIG
        self.model = Config.GOOGLE_RANKING_MODEL
        
        # Initialize the client
        try:
            self.client = discoveryengine.RankServiceClient()
        except Exception as e:
            print(f"Error initializing Google Ranking client: {e}")
            self.client = None
    
    def rank_documents(self, query: str, documents: List[Dict[str, str]]) -> List[Dict]:
        """
        Rank documents using Google's Ranking API
        
        Args:
            query: The search query
            documents: List of document dictionaries with keys: id, title, content
            
        Returns:
            List of ranked documents with scores
        """
        if not self.client:
            print("Google Ranking client not initialized")
            return self._fallback_ranking(documents)
        
        if not self.project_id:
            print("Google Cloud Project ID not configured")
            return self._fallback_ranking(documents)
        
        try:
            # Prepare ranking records
            ranking_records = []
            for i, doc in enumerate(documents):
                # Combine title and content for ranking
                content_for_ranking = ""
                if doc.get('title'):
                    content_for_ranking += f"Title: {doc['title']}\n"
                if doc.get('description'):
                    content_for_ranking += f"Description: {doc['description']}\n"
                if doc.get('content'):
                    content_for_ranking += f"Content: {doc['content']}"
                
                # Limit content length for API
                if len(content_for_ranking) > 8000:  # Conservative limit
                    content_for_ranking = content_for_ranking[:8000] + "..."
                
                ranking_record = discoveryengine.RankingRecord(
                    id=str(i),
                    title=doc.get('title', '')[:200],  # Limit title length
                    content=content_for_ranking
                )
                ranking_records.append(ranking_record)
            
            # Build the ranking config path
            ranking_config_path = self.client.ranking_config_path(
                project=self.project_id,
                location=self.location,
                ranking_config=self.ranking_config
            )
            
            # Create the request
            request = discoveryengine.RankRequest(
                ranking_config=ranking_config_path,
                model=self.model,
                top_n=len(documents),  # Return all documents ranked
                query=query,
                records=ranking_records
            )
            
            # Make the API call
            response = self.client.rank(request=request)
            
            # Process the response
            ranked_results = []
            for ranked_record in response.records:
                original_index = int(ranked_record.id)
                original_doc = documents[original_index]
                
                ranked_doc = original_doc.copy()
                ranked_doc['ranking_score'] = round(ranked_record.score, 4)
                ranked_doc['original_position'] = original_index + 1
                
                ranked_results.append(ranked_doc)
            
            return ranked_results
            
        except Exception as e:
            print(f"Error calling Google Ranking API: {e}")
            return self._fallback_ranking(documents)
    
    def _fallback_ranking(self, documents: List[Dict]) -> List[Dict]:
        """
        Fallback ranking method when Google API is not available
        Uses simple keyword matching as a basic ranking mechanism
        """
        print("Using fallback ranking method")
        
        for i, doc in enumerate(documents):
            # Simple scoring based on presence of content
            score = 0.1  # Base score
            
            if doc.get('content'):
                score += min(len(doc['content']) / 1000, 0.5)  # Content length factor
            if doc.get('title'):
                score += 0.2  # Title presence bonus
            if doc.get('description'):
                score += 0.1  # Description presence bonus
            
            doc['ranking_score'] = round(min(score, 1.0), 4)
            doc['original_position'] = i + 1
        
        # Sort by score descending
        return sorted(documents, key=lambda x: x['ranking_score'], reverse=True)
    
    def test_connection(self) -> bool:
        """Test if the Google Ranking API is accessible"""
        if not self.client or not self.project_id:
            return False
        
        try:
            # Test with a simple query
            test_records = [
                discoveryengine.RankingRecord(
                    id="test",
                    title="Test Document",
                    content="This is a test document for API connectivity."
                )
            ]
            
            ranking_config_path = self.client.ranking_config_path(
                project=self.project_id,
                location=self.location,
                ranking_config=self.ranking_config
            )
            
            request = discoveryengine.RankRequest(
                ranking_config=ranking_config_path,
                model=self.model,
                top_n=1,
                query="test",
                records=test_records
            )
            
            response = self.client.rank(request=request)
            return len(response.records) > 0
            
        except Exception as e:
            print(f"Google Ranking API connection test failed: {e}")
            return False 