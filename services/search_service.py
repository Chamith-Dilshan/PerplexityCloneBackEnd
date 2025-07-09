
from config import Settings
from tavily import TavilyClient
import trafilatura

settings = Settings()
tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

class SearchService:
    def web_search(self, query: str):
        output = []
        try:
            response = tavily_client.search(query=query, max_results=20)
            search_result = response.get("results", [])
            
            for result in search_result:
                if "url" in result:
                    url = result.get("url")
                    try:
                        content = trafilatura.fetch_url(url)
                        if content:
                            extracted_content = trafilatura.extract(content, include_comments=False)
                            content_text = extracted_content if extracted_content else "Content could not be extracted."
                        else:
                            content_text = "Content could not be fetched."
                        
                        output.append({
                            "title": result.get("title", "No Title"),
                            "url": url,
                            "content": content_text
                        })
                    except Exception as e:
                        output.append({
                            "title": result.get("title", "No Title"),
                            "url": url,
                            "content": f"Error fetching content: {str(e)}"
                        })
                else:
                    output.append({
                        "title": result.get("title", "No Title"),
                        "url": "No URL found",
                        "content": result.get("content", "No content available")
                    })
            
            print(f"Search completed. Found {len(output)} results for query: {query}")
            return output
        
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []