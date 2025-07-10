import asyncio
from fastapi import FastAPI, WebSocket

from pydantic_models.chat_body import ChatBody
from services.llm_service import LLMService
from services.search_service import SearchService
from services.sort_service_service import SortSourceService

app = FastAPI()
search_service = SearchService()
sort_source_service = SortSourceService()
llm_service = LLMService()

# chat websocket
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket:WebSocket):
    await websocket.accept()

    try:
        await asyncio.sleep(0.1)
        data = await websocket.receive_json()
        print("Received data:", data)
        query = data.get("query", "")
        if not query:
            await websocket.send_text("Query cannot be empty.")
            return
        # Search the web for relavant sources
        search_results = search_service.web_search(query)
        print("Search results:", search_results)
        # Sort out the sources
        sorted_result = sort_source_service.sort_service(query, search_results)
        print("Sorted results:", sorted_result)
        # send sorted web results 
        await asyncio.sleep(0.1)
        await websocket.send_json({
            "type": "search_results",
            "data": sorted_result
        })
        print("Sorted results sent to client.")
        # generate the response using LLM model
        for chunk in llm_service.generate_response_stream(query, sorted_result):
            await asyncio.sleep(0.1)
            await websocket.send_json({
                "type": "content",
                "data":chunk
            })
        print("Response sent to client.")
    except Exception as e:
        print("An error occurred while processing the websocket connection. Error:", str(e))
    finally:
        await websocket.close()

# chat module
@app.post("/chat")
def chat_endpoint(body: ChatBody):
    # Search the web for relavant sources
    search_results = search_service.web_search(body.query)
    # Sort out the sources
    sorted_result = sort_source_service.sort_service(body.query, search_results)
    # generate the response using LLM model
    response = llm_service.generate_response(body.query, sorted_result)

    return response