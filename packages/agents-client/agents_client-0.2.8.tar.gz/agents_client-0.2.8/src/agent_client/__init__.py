# Core client package
from .client import Agent
import requests
import json
import asyncio
import websockets
from typing import Dict, Any, BinaryIO, AsyncGenerator


# Standalone functions for backward compatibility
def send_operation(
    operation: str,
    params: Dict[str, Any],
    api_key: str,
    agent_id: str,
    base_url: str = "http://localhost:6665",
) -> Dict[str, Any]:
    """Send an operation to the agent."""
    url = f"{base_url}/operation"
    payload = {
        "operation": operation,
        "params": params,
        "api_key": api_key,
        "agent_id": agent_id,
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def upload_file(
    api_key: str,
    agent_id: str,
    file_path: str,
    file_obj: BinaryIO,
    base_url: str = "http://localhost:6665",
) -> Dict[str, Any]:
    """Upload a file to the agent."""
    url = f"{base_url}/upload_file"
    data = {
        "api_key": api_key,
        "agent_id": agent_id,
        "file_path": file_path,
    }
    files = {"file": file_obj}

    response = requests.post(url, data=data, files=files)
    response.raise_for_status()
    return response.json()


async def connect_websocket(
    agent_id: str, api_key: str, base_url: str = "http://localhost:6665"
) -> AsyncGenerator[Dict[str, Any], None]:
    """Connect to the WebSocket endpoint to stream agent responses."""
    ws_url = f"ws://{base_url.split('://')[-1]}/ws/{agent_id}/{api_key}"

    async with websockets.connect(ws_url) as websocket:
        while True:
            message = await websocket.recv()
            yield json.loads(message)
