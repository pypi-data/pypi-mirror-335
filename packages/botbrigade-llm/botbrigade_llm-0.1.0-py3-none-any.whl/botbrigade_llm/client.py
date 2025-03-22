import os
import httpx
import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator, Generator, Union, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("botbrigade-llm")


class Responses:
    """Handles synchronous and asynchronous LLM responses."""
    
    def __init__(self, client: "LLMClient"):
        self.client = client
    
    def create(self, model: str, messages: List[Dict[str, Any]], **kwargs) -> Union[Dict[str, Any], Generator[str, None, None]]:
        """Synchronous response generation."""
        url = f"{self.client.base_url}/completion"
        headers = {"Authorization": f"Bearer {self.client.api_key}"}
        payload = {"model": model, "messages": messages, **kwargs}

        logger.info(f"Sending sync request to {url} with payload: {payload}")

        if kwargs.get("stream", False):
            def stream_response():
                try:
                    with self.client.sync_client.stream("POST", url, json=payload, headers=headers, timeout=60.0) as response:
                        response.raise_for_status()
                        for line in response.iter_lines():
                            if line and line.startswith("data: "):  # Ensure it's an SSE event
                                chunk = line[6:].strip()
                                logger.debug(f"Streaming response chunk: {chunk}")
                                yield chunk
                except httpx.HTTPStatusError as e:
                    logger.error(f"Streaming API request failed: {e.response.text}")
                    yield {"error": e.response.text}
                except Exception as e:
                    logger.error(f"Unexpected streaming error: {str(e)}")
                    yield {"error": str(e)}
                    
            return stream_response()

        try:
            response = self.client.sync_client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received sync response: {data}")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Sync API request failed: {e.response.text}")
            return {"error": e.response.text}
        except Exception as e:
            logger.error(f"Unexpected sync error: {str(e)}")
            return {"error": str(e)}

    async def acreate(self, model: str, messages: List[Dict[str, Any]], **kwargs) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
        """Asynchronous response generation."""
        url = f"{self.client.base_url}/completion"
        headers = {"Authorization": f"Bearer {self.client.api_key}"}
        payload = {"model": model, "messages": messages, **kwargs}

        logger.info(f"Sending async request to {url} with payload: {payload}")

        if kwargs.get("stream", False):
            async def stream_response():
                try:
                    async with self.client.async_client.stream("POST", url, json=payload, headers=headers, timeout=60.0) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line and line.startswith("data: "):  # Ensure it's an SSE event
                                chunk = line[6:].strip()
                                logger.debug(f"Streaming response chunk: {chunk}")
                                yield chunk
                except httpx.HTTPStatusError as e:
                    logger.error(f"Streaming API request failed: {e.response.text}")
                    yield {"error": e.response.text}
                except Exception as e:
                    logger.error(f"Unexpected streaming error: {str(e)}")
                    yield {"error": str(e)}

            return stream_response()

        try:
            response = await self.client.async_client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received async response: {data}")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Async API request failed: {e.response.text}")
            return {"error": e.response.text}
        except Exception as e:
            logger.error(f"Unexpected async error: {str(e)}")
            return {"error": str(e)}


class LLMClient:
    """Main client to interact with the LLM API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://llm.botbrigade.id/api/v1/"):
        self.api_key = api_key or os.getenv("BBS_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.sync_client = httpx.Client()
        self.async_client = httpx.AsyncClient()
        self.responses = Responses(self)  # Attach Responses handler

    def list_models(self) -> Union[Dict[str, Any], None]:
        """List all available models (synchronous)."""
        url = f"{self.base_url}/list_models"
        headers = {"Authorization": f"Bearer {self.api_key}", "accept": "application/json"}

        try:
            response = self.sync_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch models: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    async def alist_models(self) -> Union[Dict[str, Any], None]:
        """List all available models (asynchronous)."""
        url = f"{self.base_url}/list_models"
        headers = {"X-Api-Key": self.api_key, "accept": "application/json"}

        try:
            response = await self.async_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch models: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

    def close(self):
        """Close the sync client session."""
        self.sync_client.close()

    async def aclose(self):
        """Close the async client session."""
        await self.async_client.aclose()
