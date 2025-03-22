import requests
import json
import asyncio
import websockets
import os
import threading
from typing import Dict, Any, Callable, List, Union, BinaryIO

class Agent:
    """
    A simple client for interacting with the Agent API.
    
    Similar to OpenAI's API, this provides a very simple interface 
    to send messages and stream responses.
    """
    
    def __init__(
        self, 
        agent_id: str, 
        api_key: str, 
        base_url: str = "http://localhost:6665",
        stream_callback: Callable = None
    ):
        """
        Initialize an Agent client.
        
        Args:
            agent_id: The ID of the agent to interact with
            api_key: The API key for authentication
            base_url: Base URL for the API (default: http://localhost:6665)
            stream_callback: Optional callback function for streaming responses
        """
        self.agent_id = agent_id
        self.api_key = api_key
        self.base_url = base_url
        self.stream_callback = stream_callback
        self._websocket_thread = None
        self._is_streaming = False
    
    def message(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Send a message to the agent.
        
        Args:
            text: The text message to send
            **kwargs: Additional parameters to include
            
        Returns:
            The API response
        """
        url = f"{self.base_url}/operation"
        payload = {
            "operation": "message",
            "params": {"text": text, **kwargs},
            "api_key": self.api_key,
            "agent_id": self.agent_id,
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, file_path: str, file_obj: BinaryIO) -> Dict[str, Any]:
        """
        Upload a file to the agent.
        
        Args:
            file_path: The destination path for the file
            file_obj: The file object to upload
            
        Returns:
            The API response
        """
        url = f"{self.base_url}/upload_file"
        data = {
            "api_key": self.api_key,
            "agent_id": self.agent_id,
            "file_path": file_path,
        }
        files = {"file": file_obj}
        
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        return response.json()
    
    def start_streaming(self, callback: Callable = None) -> None:
        """
        Start streaming responses from the agent in a background thread.
        
        Args:
            callback: Function to call with each response message
                     If None, uses the callback provided at initialization
        """
        if self._is_streaming:
            return  # Already streaming
        
        callback = callback or self.stream_callback
        if not callback:
            raise ValueError("Callback function must be provided either at initialization or when calling start_streaming")
        
        self._is_streaming = True
        self._websocket_thread = threading.Thread(
            target=self._run_websocket_stream,
            args=(callback,),
            daemon=True
        )
        self._websocket_thread.start()
    
    def _run_websocket_stream(self, callback: Callable) -> None:
        """Internal method to run the websocket stream in a background thread."""
        asyncio.run(self._stream_messages(callback))
    
    async def _stream_messages(self, callback: Callable) -> None:
        """Internal async method to stream messages from the websocket."""
        ws_url = f"ws://{self.base_url.split('://')[-1]}/ws/{self.agent_id}/{self.api_key}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                while self._is_streaming:
                    message = await websocket.recv()
                    data = json.loads(message)
                    callback(data)
        except Exception as e:
            print(f"Websocket error: {e}")
        finally:
            self._is_streaming = False
    
    def stop_streaming(self) -> None:
        """Stop streaming responses."""
        self._is_streaming = False
        if self._websocket_thread and self._websocket_thread.is_alive():
            self._websocket_thread.join(timeout=1.0)
            
    def stop_agent(self, message: str = "User requested stop", reason: str = "User initiated stop request") -> Dict[str, Any]:
        """
        Send a stop signal to the agent.
        
        Args:
            message: Short message displayed to the agent
            reason: Detailed reason for the stop request
            
        Returns:
            The API response
        """
        url = f"{self.base_url}/operation"
        payload = {
            "operation": "stop_agent",
            "params": {
                "message": message,
                "reason": reason
            },
            "api_key": self.api_key,
            "agent_id": self.agent_id,
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()


# End of Agent class
