"""
Tripo 3D Generation API Client.

This module provides a client for the Tripo 3D Generation API.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple, cast
from urllib.parse import urljoin

# Import aiohttp - it's now a project dependency managed by uv
import aiohttp

from .models import Task, Balance, TaskStatus
from .exceptions import TripoAPIError, TripoRequestError


class TripoClient:
    """Client for the Tripo 3D Generation API."""
    
    # The base URL for the Tripo API as specified in the OpenAPI schema
    BASE_URL = "https://api.tripo3d.ai/v2/openapi"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Tripo API client.
        
        Args:
            api_key: The API key for authentication. If not provided, it will be read from the
                     TRIPO_API_KEY environment variable.
        
        Raises:
            ValueError: If no API key is provided and the TRIPO_API_KEY environment variable is not set.
        """
        self.api_key = api_key or os.environ.get("TRIPO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as an argument or set the TRIPO_API_KEY environment variable."
            )
        
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure that an aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self._session
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self) -> 'TripoClient':
        """Enter the async context manager."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context manager."""
        await self.close()
    
    def _url(self, path: str) -> str:
        """
        Construct a full URL from a path.
        
        Args:
            path: The path to append to the base URL.
            
        Returns:
            The full URL.
        """
        # Remove leading slash if present
        path = path.lstrip('/')
        
        # Construct the full URL
        return f"{self.BASE_URL}/{path}"
    
    async def _request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: The HTTP method to use.
            path: The path to request.
            params: Query parameters.
            json_data: JSON data to send in the request body.
            data: Form data to send in the request body.
            headers: Additional headers to send with the request.
            
        Returns:
            The parsed JSON response.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
        """
        session = await self._ensure_session()
        url = self._url(path)
        
        try:
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                headers=headers
            ) as response:
                # Check if the response status is an error
                if response.status >= 400:
                    error_text = await response.text()
                    try:
                        error_data = await response.json()
                        if "code" in error_data and "message" in error_data:
                            raise TripoAPIError(
                                code=error_data["code"],
                                message=error_data["message"],
                                suggestion=error_data.get("suggestion")
                            )
                    except:
                        # If we can't parse the error as JSON, use the raw text
                        raise TripoRequestError(
                            status_code=response.status,
                            message=f"Request failed: {response.reason}. Response: {error_text}"
                        )
                
                # Try to parse the response as JSON
                try:
                    response_data = await response.json()
                except aiohttp.ContentTypeError as e:
                    # If the response is not JSON, raise an error with details
                    response_text = await response.text()
                    raise TripoRequestError(
                        status_code=response.status,
                        message=f"Failed to parse response as JSON. URL: {url}, Status: {response.status}, Content-Type: {response.headers.get('Content-Type')}, Response: {response_text[:200]}..."
                    )
                
                return response_data
        except aiohttp.ClientError as e:
            raise TripoRequestError(status_code=0, message=f"Request error for {url}: {str(e)}")
    
    async def get_task(self, task_id: str) -> Task:
        """
        Get the status of a task.
        
        Args:
            task_id: The ID of the task to get.
            
        Returns:
            The task data.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
        """
        response = await self._request("GET", f"/task/{task_id}")
        return Task.from_dict(response["data"])
    
    async def upload_file(self, file_path: str) -> str:
        """
        Upload a file to the API.
        
        Args:
            file_path: The path to the file to upload.
            
        Returns:
            The image token for the uploaded file.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        session = await self._ensure_session()
        url = self._url("/upload")
        
        try:
            with open(file_path, "rb") as f:
                form_data = aiohttp.FormData()
                form_data.add_field("file", f, filename=os.path.basename(file_path))
                
                async with session.post(url, data=form_data) as response:
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        if "code" in response_data and "message" in response_data:
                            raise TripoAPIError(
                                code=response_data["code"],
                                message=response_data["message"],
                                suggestion=response_data.get("suggestion")
                            )
                        else:
                            raise TripoRequestError(
                                status_code=response.status,
                                message=f"Request failed: {response.reason}"
                            )
                    
                    return response_data["data"]["image_token"]
        except aiohttp.ClientError as e:
            raise TripoRequestError(status_code=0, message=str(e))
    
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        Create a new task.
        
        Args:
            task_data: The task data to send to the API.
            
        Returns:
            The ID of the created task.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
        """
        response = await self._request("POST", "/task", json_data=task_data)
        return response["data"]["task_id"]
    
    async def get_balance(self) -> Balance:
        """
        Get the user's balance.
        
        Returns:
            The user's balance data.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
        """
        response = await self._request("GET", "/user/balance")
        return Balance.from_dict(response["data"])
    
    # Convenience methods for different task types
    
    async def text_to_model(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model_version: Optional[str] = "v2.5-20250123",
        face_limit: Optional[int] = None,
        texture: Optional[bool] = True,
        pbr: Optional[bool] = True,
        text_seed: Optional[int] = None,
        model_seed: Optional[int] = None,
        texture_seed: Optional[int] = None,
        texture_quality: str = "standard",
        style: Optional[str] = None,
        auto_size: bool = False,
        quad: bool = False
    ) -> str:
        """
        Create a text-to-model task.
        
        Args:
            prompt: The text prompt to generate a model from.
            negative_prompt: Negative prompt to guide the generation.
            model_version: The model version to use.
            face_limit: The maximum number of faces in the model.
            texture: Whether to generate a texture.
            pbr: Whether to generate PBR maps.
            text_seed: Seed for text generation.
            model_seed: Seed for model generation.
            texture_seed: Seed for texture generation.
            texture_quality: The quality of the texture.
            style: The style to apply to the model.
            auto_size: Whether to automatically size the model.
            quad: Whether to use quad topology.
            
        Returns:
            The ID of the created task.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
        """
        task_data: Dict[str, Any] = {
            "type": "text_to_model",
            "prompt": prompt
        }
        
        if negative_prompt:
            task_data["negative_prompt"] = negative_prompt
        if model_version:
            task_data["model_version"] = model_version
        if face_limit is not None:
            task_data["face_limit"] = face_limit
        if texture is not None:
            task_data["texture"] = texture
        if pbr is not None:
            task_data["pbr"] = pbr
        if text_seed is not None:
            task_data["text_seed"] = text_seed
        if model_seed is not None:
            task_data["model_seed"] = model_seed
        if texture_seed is not None:
            task_data["texture_seed"] = texture_seed
        if texture_quality:
            task_data["texture_quality"] = texture_quality
        if style:
            task_data["style"] = style
        if auto_size is not None:
            task_data["auto_size"] = auto_size
        if quad is not None:
            task_data["quad"] = quad
        
        return await self.create_task(task_data)
    
    async def image_to_model(
        self,
        image_path: str,
        model_version: Optional[str] = "v2.5-20250123",
        face_limit: Optional[int] = None,
        texture: Optional[bool] = True,
        pbr: Optional[bool] = True,
        model_seed: Optional[int] = None,
        texture_seed: Optional[int] = None,
        texture_quality: str = "standard",
        texture_alignment: str = "original_image",
        style: Optional[str] = None,
        auto_size: bool = False,
        orientation: str = "default",
        quad: bool = False
    ) -> str:
        """
        Create an image-to-model task.
        
        Args:
            image_path: The path to the image file.
            model_version: The model version to use.
            face_limit: The maximum number of faces in the model.
            texture: Whether to generate a texture.
            pbr: Whether to generate PBR maps.
            model_seed: Seed for model generation.
            texture_seed: Seed for texture generation.
            texture_quality: The quality of the texture.
            texture_alignment: The alignment of the texture.
            style: The style to apply to the model.
            auto_size: Whether to automatically size the model.
            orientation: The orientation of the model.
            quad: Whether to use quad topology.
            
        Returns:
            The ID of the created task.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
            FileNotFoundError: If the image file does not exist.
        """
        image_token = await self.upload_file(image_path)
        
        task_data: Dict[str, Any] = {
            "type": "image_to_model",
            "file": {
                "type": "image",
                "file_token": image_token
            }
        }
        
        if model_version:
            task_data["model_version"] = model_version
        if face_limit is not None:
            task_data["face_limit"] = face_limit
        if texture is not None:
            task_data["texture"] = texture
        if pbr is not None:
            task_data["pbr"] = pbr
        if model_seed is not None:
            task_data["model_seed"] = model_seed
        if texture_seed is not None:
            task_data["texture_seed"] = texture_seed
        if texture_quality:
            task_data["texture_quality"] = texture_quality
        if texture_alignment:
            task_data["texture_alignment"] = texture_alignment
        if style:
            task_data["style"] = style
        if auto_size is not None:
            task_data["auto_size"] = auto_size
        if orientation:
            task_data["orientation"] = orientation
        if quad is not None:
            task_data["quad"] = quad
        
        return await self.create_task(task_data)
    
    async def wait_for_task(
        self, 
        task_id: str, 
        polling_interval: float = 2.0,
        timeout: Optional[float] = None
    ) -> Task:
        """
        Wait for a task to complete.
        
        Args:
            task_id: The ID of the task to wait for.
            polling_interval: The interval in seconds between polling requests.
            timeout: The maximum time in seconds to wait for the task to complete.
                    If None, wait indefinitely.
            
        Returns:
            The completed task data.
            
        Raises:
            TripoRequestError: If the request fails.
            TripoAPIError: If the API returns an error.
            asyncio.TimeoutError: If the task does not complete within the timeout.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            task = await self.get_task(task_id)
            
            if task.status in (
                TaskStatus.SUCCESS, 
                TaskStatus.FAILED, 
                TaskStatus.CANCELLED, 
                TaskStatus.BANNED, 
                TaskStatus.EXPIRED
            ):
                return task
            
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    raise asyncio.TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            await asyncio.sleep(polling_interval) 