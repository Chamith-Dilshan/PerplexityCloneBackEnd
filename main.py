from fastapi import FastAPI

from pydantic_models.chat_body import ChatBody
from services import sort_service_service
from services.search_service import SearchService
from services.sort_service_service import SortSourceService

app = FastAPI()
search_service = SearchService()
sort_source_service = SortSourceService()

# chat module
@app.post("/chat")
def chat_endpoint(body: ChatBody):
    # Search the web for relavant sources
    search_results = search_service.web_search(body.query)
    # Sort out the sources
    sorted_result = sort_source_service.sort_service(body.query, search_results)
    # generate the response using LLM model
    
    return body.query