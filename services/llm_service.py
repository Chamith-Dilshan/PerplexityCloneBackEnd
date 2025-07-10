from httpx import stream
from config import Settings
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from typing import List

settings = Settings()

class LLMService:
    def __init__(self) -> None:
        self.llm = ChatOllama(
            model=settings.MODEL_NAME,
            temperature=0.6,
        )
        self.output_parser = StrOutputParser()

    def _format_context(self, search_results: List[dict]) -> str:
        return "\n\n".join(
            [f"Source {i+1}: ({r['url']}):\n{r['content']}" for i, r in enumerate(search_results)]
        )

    # streaming version of the chain
    # this is used to stream the response from the LLM model
    def _create_chain_stream(self):
        prompt = ChatPromptTemplate.from_template(
            """Context from web search:
            {context}

            Query: {query}

            Please provide a comprehensive, detailed, well-cited accurate response using ONLY the above context. 
            Include references (e.g., Source 1) as appropriate. Avoid using your own knowledge unless strictly necessary."""
        )
        return (
            # {"context": lambda x: x["context"], "query": lambda x: x["query"]}
            prompt
            | self.llm
        )

    def generate_response_stream(self, query: str, search_results: List[dict]):
        context_text = self._format_context(search_results)
        chain = self._create_chain_stream()

        print("LLM response stream started...")

        for chunk in chain.stream({"query": query, "context": context_text}):
            # when using ChatOllama, chunk is usually a ChatMessage
            print("LLM response chunk received:", chunk)

            if isinstance(chunk, BaseMessage):
                print("Chunk is a BaseMessage instance.")
                yield chunk.content  # For LangChain 0.1.14+ style ChatMessage chunks
            elif hasattr(chunk, "text"):
                print("Chunk has a 'text' attribute.")
                yield chunk.text     # For generic string-based chunks
            else:
                print("Chunk is a string or has no specific attributes.")
                yield str(chunk)

    # non-streaming version of the chain
    # this is used to get the response from the LLM model in one go
    def _create_chain(self):
        prompt = ChatPromptTemplate.from_template(
            """Context from web search:
            {context}

            Query: {query}

            Please provide a comprehensive, detailed, well-cited accurate response using ONLY the above context. 
            Include references (e.g., Source 1) as appropriate. Avoid using your own knowledge unless strictly necessary."""
        )
        return (
            # {"context": lambda x: x["context"], "query": lambda x: x["query"]}
            prompt
            | self.llm
            | self.output_parser
        )

    def generate_response(self, query: str, search_results: List[dict]):
        context_text = self._format_context(search_results)
        chain = self._create_chain()

        print("LLM response started...")

        response  = chain.invoke({"query": query, "context": context_text})
        # when using ChatOllama, chunk is usually a ChatMessage
        return response
