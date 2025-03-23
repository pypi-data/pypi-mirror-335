from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union
import threading
import asyncio
import logging
import json
import time
import uuid
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to process")
    tool_params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters for tool execution")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")

class ToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    input_data: Dict[str, Any] = Field(..., description="Input data for the tool")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections.values():
            await connection.send_json(message)

class APIGenerator:
    def __init__(self, assistant):
        """
        Initialize the APIGenerator with the given assistant.

        Args:
            assistant: The assistant instance for which the API is being created.
        """
        self.assistant = assistant
        self.app = self._create_fastapi_app()
        self._background_tasks = {}
        self.connection_manager = ConnectionManager()
        
    def _create_fastapi_app(self) -> FastAPI:
        """
        Create a FastAPI app with enhanced endpoints for the assistant and its tools.
        """
        app = FastAPI(title=f"{self.assistant.name or 'Assistant'} API", 
                    description=self.assistant.description or "API for interacting with the assistant")

        # Default CORS settings (allow all)
        cors_config = {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

        # Override default CORS settings with user-provided settings
        if self.assistant.api_config and "cors" in self.assistant.api_config:
            cors_config.update(self.assistant.api_config["cors"])

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config["allow_origins"],
            allow_credentials=cors_config["allow_credentials"],
            allow_methods=cors_config["allow_methods"],
            allow_headers=cors_config["allow_headers"],
        )
        
        # Mount static files for screenshots
        try:
            screenshots_dir = os.path.abspath("./screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            app.mount("/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")
            logger.info(f"Mounted screenshots directory at {screenshots_dir}")
        except Exception as e:
            logger.error(f"Failed to mount screenshots directory: {e}")

        @app.post("/chat")
        async def chat(
            request: Optional[ChatRequest] = None, 
            message: Optional[str] = None
        ):
            """
            Endpoint to interact with the assistant.
            
            Supports both:
            - Query parameter: /chat?message=your_message
            - JSON body: {"message": "your_message"}
            """
            try:
                # Get message from either body or query param
                actual_message = None
                stream = False
                tool_params = None
                
                if request:
                    actual_message = request.message
                    stream = request.stream
                    tool_params = request.tool_params
                elif message:
                    actual_message = message
                
                if not actual_message:
                    raise HTTPException(status_code=400, detail="Message is required")
                    
                if stream:
                    task_id = self._start_streaming_task(actual_message, tool_params)
                    return {"task_id": task_id, "status": "streaming"}
                else:
                    response = self.assistant.print_response(message=actual_message)
                    if self.assistant.json_output:
                        return response
                    else:
                        return {"response": response}
            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/stream/{task_id}")
        async def get_stream_status(task_id: str):
            """
            Get the status of a streaming task.
            """
            if task_id not in self._background_tasks:
                raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found")
            
            task_info = self._background_tasks[task_id]
            if task_info["status"] == "completed":
                # Clean up completed task
                result = task_info["result"]
                del self._background_tasks[task_id]
                return {"status": "completed", "response": result}
            elif task_info["status"] == "error":
                error = task_info["error"]
                del self._background_tasks[task_id]
                return {"status": "error", "error": str(error)}
            else:
                return {"status": "processing"}

        @app.get("/tools")
        async def get_tools():
            """
            Endpoint to get the list of tools available to the assistant.
            """
            if not self.assistant.tools:
                return {"tools": []}
                
            tools_info = []
            for tool in self.assistant.tools:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description
                }
                # Add additional tool fields that might be useful
                for field_name, field in tool.__fields__.items():
                    if field_name not in ["name", "description", "llm"] and hasattr(tool, field_name):
                        value = getattr(tool, field_name)
                        if not callable(value):
                            tool_info[field_name] = value
                tools_info.append(tool_info)
            
            return {"tools": tools_info}

        # Add endpoint to execute tools directly
        @app.post("/tools/{tool_name}")
        async def execute_tool(
            tool_name: str, 
            background_tasks: BackgroundTasks,
            input_data: Dict[str, Any] = Body(...),
            async_execution: bool = True  # Set default to True
        ):
            """
            Execute a specific tool directly.
            """
            # Find the requested tool
            tool = next((t for t in self.assistant.tools if t.name.lower() == tool_name.lower()), None)
            if not tool:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
            # Check if the tool needs to run asynchronously (like WebBrowser)
            if async_execution or tool.name == "WebBrowserAsync" or tool.name == "WebBrowser":
                task_id = f"tool_{tool_name}_{uuid.uuid4()}"
                self._background_tasks[task_id] = {"status": "processing"}
                
                background_tasks.add_task(
                    self._execute_tool_in_background,
                    task_id=task_id,
                    tool=tool,
                    input_data=input_data
                )
                
                # For WebBrowserAsync tools, we need to remember the API task_id
                # so we can map it to the actual tool-generated task_id later
                if tool.name == "WebBrowserAsync":
                    logger.info(f"API task_id for WebBrowserAsync: {task_id}")
                    return {"task_id": task_id, "status": "processing"}
                else:
                    return {"task_id": task_id, "status": "processing"}
            else:
                try:
                    # Set the LLM instance if not already set
                    if not tool.llm and self.assistant.llm_instance:
                        tool.llm = self.assistant.llm_instance
                    
                    # Execute the tool
                    result = tool.execute(input_data)
                    return {"status": "success", "result": result}
                except Exception as e:
                    logger.error(f"Error executing tool '{tool_name}': {e}")
                    raise HTTPException(status_code=500, detail=str(e))

        @app.get("/tools/status/{task_id}")
        async def get_tool_status(task_id: str):
            """
            Get the status of an asynchronous tool execution.
            """
            if task_id not in self._background_tasks:
                raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found")
            
            task_info = self._background_tasks[task_id]
            
            # Special handling for WebBrowserAsync tool
            if task_id.startswith("tool_WebBrowserAsync_") and hasattr(self.assistant, "tools"):
                # Find the WebBrowserAsync tool
                tool = next((t for t in self.assistant.tools if t.name == "WebBrowserAsync"), None)
                if tool and hasattr(tool, "get_task_status"):
                    # Extract the UUID part from the task_id
                    uuid_part = task_id.replace("tool_WebBrowserAsync_", "")
                    
                    # Get detailed status from the tool
                    detailed_status = tool.get_task_status(uuid_part)
                    if detailed_status:
                        return detailed_status
            
            # Standard status handling for other tools
            if task_info["status"] == "completed":
                # Clean up completed task
                result = task_info["result"]
                del self._background_tasks[task_id]
                return {"status": "completed", "result": result}
            elif task_info["status"] == "error":
                error = task_info["error"]
                del self._background_tasks[task_id]
                return {"status": "error", "error": str(error)}
            else:
                return {"status": "processing"}
                
        @app.get("/live-screenshot/{task_id}")
        async def get_live_screenshot(task_id: str):
            """
            Get a real-time screenshot from the running browser automation.
            """
            # Verify the task ID format and extract the UUID part
            if not task_id.startswith("tool_WebBrowserAsync_"):
                task_id_parts = task_id.split("_")
                if len(task_id_parts) >= 3 and task_id_parts[1] == "WebBrowserAsync":
                    uuid_part = task_id_parts[2]
                else:
                    raise HTTPException(status_code=400, detail="Invalid task ID format")
            else:
                uuid_part = task_id.replace("tool_WebBrowserAsync_", "")
            
            # Find the WebBrowserAsync tool
            tool = next((t for t in self.assistant.tools if t.name == "WebBrowserAsync"), None)
            if not tool:
                raise HTTPException(status_code=404, detail="WebBrowserAsync tool not found")
            
            # Check if the task exists
            try:
                task_status = tool.get_task_status(uuid_part)
                if task_status.get("status") == "error":
                    raise HTTPException(status_code=400, detail="Task has error status")
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Task {uuid_part} not found: {str(e)}")
            
            # Take a live screenshot
            if hasattr(tool, "take_live_screenshot"):
                try:
                    screenshot_filename = tool.take_live_screenshot(uuid_part)
                    if screenshot_filename:
                        # Return the filename
                        return {"screenshot": screenshot_filename}
                    else:
                        raise HTTPException(status_code=500, detail="Failed to take screenshot")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error taking screenshot: {str(e)}")
            else:
                raise HTTPException(status_code=501, detail="Live screenshot not supported by this tool")
                
        @app.get("/screenshots/{task_id}/latest")
        async def get_latest_screenshot(task_id: str):
            """
            Get the latest screenshot for a task.
            """
            # Verify the task ID format and extract the UUID part
            if not task_id.startswith("tool_WebBrowserAsync_"):
                task_id_parts = task_id.split("_")
                if len(task_id_parts) >= 3 and task_id_parts[1] == "WebBrowserAsync":
                    uuid_part = task_id_parts[2]
                else:
                    raise HTTPException(status_code=400, detail="Invalid task ID format")
            else:
                uuid_part = task_id.replace("tool_WebBrowserAsync_", "")
            
            # Find the WebBrowserAsync tool
            tool = next((t for t in self.assistant.tools if t.name == "WebBrowserAsync"), None)
            if not tool:
                raise HTTPException(status_code=404, detail="WebBrowserAsync tool not found")
            
            # Get task status to access screenshots
            try:
                task_status = tool.get_task_status(uuid_part)
                if not task_status:
                    raise HTTPException(status_code=404, detail=f"Task {uuid_part} not found")
                
                screenshots = task_status.get("screenshots", [])
                if not screenshots:
                    raise HTTPException(status_code=404, detail="No screenshots available for this task")
                
                # Return the latest screenshot filename
                latest_screenshot = screenshots[-1]
                return {"screenshot": latest_screenshot}
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=500, detail=f"Error getting latest screenshot: {str(e)}")
        @app.get("/screenshots/file/{filename}")
        async def get_screenshot_file(filename: str):
            """
            Get a screenshot file directly by filename with enhanced error handling and debugging.
            """
            # Build the absolute path to the screenshots directory
            screenshots_dir = os.path.abspath("./screenshots")
            screenshot_path = os.path.join(screenshots_dir, filename)
            
            # Log the requested path for debugging
            logger.info(f"Screenshot requested: {filename}, full path: {screenshot_path}")
            
            if not os.path.exists(screenshot_path):
                logger.warning(f"Screenshot not found at exact path: {screenshot_path}")
                
                # Try to find the file with case-insensitive matching
                found = False
                try:
                    for file in os.listdir(screenshots_dir):
                        if file.lower() == filename.lower():
                            screenshot_path = os.path.join(screenshots_dir, file)
                            logger.info(f"Found screenshot with case-insensitive match: {file}")
                            found = True
                            break
                        
                        # Also try matching the end of the filename
                        if file.endswith(filename.split("_")[-1]):
                            screenshot_path = os.path.join(screenshots_dir, file)
                            logger.info(f"Found screenshot by matching suffix: {file}")
                            found = True
                            break
                except Exception as e:
                    logger.error(f"Error while trying to find screenshot with alternative methods: {e}")
                
                if not found:
                    # List available screenshots for debugging
                    try:
                        available_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
                        logger.error(f"Screenshot not found. Available screenshots: {available_files[:10]}")
                    except Exception:
                        pass
                        
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Screenshot {filename} not found in directory {screenshots_dir}"
                    )
            
            # Check file permissions
            if not os.access(screenshot_path, os.R_OK):
                logger.error(f"Permission denied: Cannot read screenshot file {screenshot_path}")
                raise HTTPException(status_code=403, detail="Permission denied for screenshot file")
            
            # Check file size to ensure it's a valid image
            try:
                file_size = os.path.getsize(screenshot_path)
                if file_size == 0:
                    logger.error(f"Screenshot file is empty: {screenshot_path}")
                    raise HTTPException(status_code=500, detail="Screenshot file is empty")
            except OSError as e:
                logger.error(f"Error checking screenshot file: {e}")
                raise HTTPException(status_code=500, detail=f"Error accessing screenshot file: {str(e)}")
            
            # Explicitly set the content type to image/png and disable caching
            return FileResponse(
                screenshot_path, 
                media_type="image/png",
                headers={
                    "Content-Type": "image/png",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        @app.get("/debug/screenshots")
        async def debug_screenshots():
            """
            Debug endpoint to list all available screenshots and provide diagnostic information.
            """
            try:
                screenshots_dir = os.path.abspath("./screenshots")
                
                if not os.path.exists(screenshots_dir):
                    return {
                        "error": f"Screenshots directory does not exist: {screenshots_dir}",
                        "current_working_directory": os.getcwd()
                    }
                    
                # List all files in the screenshots directory
                files = []
                for file in os.listdir(screenshots_dir):
                    if file.endswith(".png"):
                        file_path = os.path.join(screenshots_dir, file)
                        try:
                            files.append({
                                "filename": file,
                                "size_bytes": os.path.getsize(file_path),
                                "last_modified": os.path.getmtime(file_path),
                                "is_readable": os.access(file_path, os.R_OK),
                                "url": f"/screenshots/file/{file}"
                            })
                        except Exception as e:
                            files.append({
                                "filename": file,
                                "error": str(e)
                            })
                            
                # Also provide server environment information
                env_info = {
                    "current_working_directory": os.getcwd(),
                    "screenshots_absolute_path": screenshots_dir,
                    "python_version": os.sys.version,
                    "platform": os.sys.platform
                }
                
                return {
                    "screenshots_dir": screenshots_dir,
                    "file_count": len(files),
                    "files": files,
                    "environment": env_info
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "current_working_directory": os.getcwd()
                }
        @app.websocket("/ws/tools/{task_id}")
        async def websocket_tool_status(websocket: WebSocket, task_id: str):
            """
            WebSocket endpoint for real-time updates on tool execution status.
            """
            client_id = f"client_{uuid.uuid4()}"
            await self.connection_manager.connect(websocket, client_id)
            
            try:
                # First check if the task exists
                if not task_id.startswith("tool_"):
                    await websocket.send_json({
                        "status": "error", 
                        "message": "Invalid task ID format",
                        "progress": 0,
                        "steps": [],
                        "screenshots": []
                    })
                    return
                
                # If task_id is for WebBrowserAsync, get the UUID part
                tool_name = "unknown"
                uuid_part = ""
                
                if "_" in task_id:
                    parts = task_id.split("_", 2)
                    if len(parts) >= 3:
                        tool_name = parts[1]
                        uuid_part = parts[2]
                
                if tool_name == "WebBrowserAsync":
                    # Check if we have a mapping for this task_id
                    mapped_task_id = None
                    
                    # Look in background_tasks for the mapping
                    for bg_task_id, bg_task_info in self._background_tasks.items():
                        if bg_task_id == task_id:
                            # Found the task, check if it has an actual_task_id mapped
                            mapped_task_id = bg_task_info.get("actual_task_id")
                            break
                    
                    # Extract the UUID part from the mapped task_id if found
                    mapped_uuid = None
                    if mapped_task_id and mapped_task_id.startswith("tool_WebBrowserAsync_"):
                        mapped_uuid = mapped_task_id.split("_", 2)[2]
                        logger.info(f"Found mapped UUID: {mapped_uuid} for task_id: {task_id}")
                    
                    # Find the WebBrowserAsync tool
                    tool = next((t for t in self.assistant.tools if t.name == "WebBrowserAsync"), None)
                    if not tool:
                        await websocket.send_json({
                            "status": "error", 
                            "message": "WebBrowserAsync tool not found",
                            "progress": 0,
                            "steps": [],
                            "screenshots": []
                        })
                        return
                    
                    # Log debug info for the WebSocket connection
                    logger.info(f"WebSocket connected for task: {task_id}, UUID: {uuid_part}, Mapped UUID: {mapped_uuid}")
                    
                    # Try to get status - first try the mapped UUID if available
                    try:
                        if mapped_uuid:
                            # Try with the mapped UUID first
                            status = tool.get_task_status(mapped_uuid)
                        else:
                            # Try with the original UUID
                            status = tool.get_task_status(uuid_part)
                        
                        # If status indicates error with "not found", try to get the task by examining the available tasks
                        if status.get("status") == "error" and "not found" in status.get("message", ""):
                            # Log all available tasks for debugging
                            from hashai.tools.web_browser_async import WebBrowserAsyncAdapter
                            available_tasks = list(WebBrowserAsyncAdapter._all_tasks.keys())
                            logger.info(f"Available tasks: {available_tasks}")
                            
                            if available_tasks:
                                # Try the latest task (assuming the tasks are stored in order)
                                latest_task_id = available_tasks[-1]
                                logger.info(f"Task {uuid_part} not found, trying latest task: {latest_task_id}")
                                status = tool.get_task_status(latest_task_id)
                        
                        # Ensure all required fields exist in the status
                        if "progress" not in status:
                            status["progress"] = 0
                        if "steps" not in status:
                            status["steps"] = []
                        if "screenshots" not in status:
                            status["screenshots"] = []
                            
                        logger.info(f"Initial status: {status['status']}, Steps: {len(status['steps'])}, Screenshots: {len(status['screenshots'])}")
                        
                        await websocket.send_json(status)
                        
                        # Poll for updates
                        poll_interval = 0.5  # seconds
                        last_steps_count = len(status.get("steps", []))
                        last_screenshots_count = len(status.get("screenshots", []))
                        
                        # Use the task_id that worked for initial status
                        effective_task_id = mapped_uuid if mapped_uuid else (
                            latest_task_id if status.get("status") != "error" and "not found" in status.get("message", "") else uuid_part
                        )
                        
                        while True:
                            # Give some time between polls
                            await asyncio.sleep(poll_interval)
                            
                            # Get updated status
                            try:
                                current_status = tool.get_task_status(effective_task_id)
                                
                                # Ensure all required fields exist in the current status
                                if "progress" not in current_status:
                                    current_status["progress"] = status.get("progress", 0)
                                if "steps" not in current_status:
                                    current_status["steps"] = []
                                if "screenshots" not in current_status:
                                    current_status["screenshots"] = []
                                
                                # Check if status changed or there are new steps or screenshots
                                current_steps_count = len(current_status.get("steps", []))
                                current_screenshots_count = len(current_status.get("screenshots", []))
                                
                                if (current_status["status"] != status["status"] or 
                                    current_status["progress"] != status["progress"] or
                                    current_steps_count != last_steps_count or
                                    current_screenshots_count != last_screenshots_count):
                                    
                                    # Send update to client
                                    await websocket.send_json(current_status)
                                    status = current_status
                                    last_steps_count = current_steps_count
                                    last_screenshots_count = current_screenshots_count
                                
                                # If task is completed or failed, break the loop
                                if current_status["status"] in ["completed", "error"]:
                                    logger.info(f"Task {effective_task_id} completed with status: {current_status['status']}")
                                    break
                            except Exception as e:
                                logger.error(f"Error getting task status: {e}")
                                await websocket.send_json({
                                    "status": "error",
                                    "message": f"Error updating task status: {str(e)}",
                                    "progress": status.get("progress", 0),
                                    "steps": status.get("steps", []),
                                    "screenshots": status.get("screenshots", [])
                                })
                                break
                    except Exception as e:
                        logger.error(f"Error in websocket initial status: {e}")
                        await websocket.send_json({
                            "status": "error",
                            "message": str(e),
                            "progress": 0,
                            "steps": [],
                            "screenshots": []
                        })
                else:
                    # For other tools, use standard status checking
                    while True:
                        if task_id not in self._background_tasks:
                            await websocket.send_json({
                                "status": "error", 
                                "message": f"Task ID {task_id} not found",
                                "progress": 0,
                                "steps": [],
                                "screenshots": []
                            })
                            break
                        
                        task_info = self._background_tasks[task_id]
                        
                        # Ensure task_info has the necessary fields for the frontend
                        if "status" not in task_info:
                            task_info["status"] = "processing"
                        if "progress" not in task_info:
                            task_info["progress"] = 0
                        if "steps" not in task_info:
                            task_info["steps"] = []
                        if "screenshots" not in task_info:
                            task_info["screenshots"] = []
                        
                        await websocket.send_json(task_info)
                        
                        if task_info["status"] in ["completed", "error"]:
                            # Clean up task data
                            if task_id in self._background_tasks:
                                del self._background_tasks[task_id]
                            break
                        
                        await asyncio.sleep(1)
            except WebSocketDisconnect:
                self.connection_manager.disconnect(client_id)
            except Exception as e:
                logger.error(f"Error in websocket_tool_status: {e}")
                try:
                    await websocket.send_json({
                        "status": "error", 
                        "message": str(e),
                        "progress": 0,
                        "steps": [],
                        "screenshots": []
                    })
                except:
                    pass
                self.connection_manager.disconnect(client_id)
                
        @app.get("/debug/tasks")
        async def debug_tasks():
            """Debug endpoint to see all tasks"""
            tools = []
            browser_tool = None
            
            if hasattr(self.assistant, "tools") and self.assistant.tools:
                tools = self.assistant.tools
                browser_tool = next((t for t in tools if t.name == "WebBrowserAsync"), None)
            
            if browser_tool:
                # Try to access the tasks using various methods
                try:
                    from hashai.tools.web_browser_async import WebBrowserAsyncAdapter
                    
                    # Get class-level tasks
                    class_tasks = {}
                    if hasattr(WebBrowserAsyncAdapter, "_all_tasks"):
                        class_tasks = {k: v.get("status", "unknown") for k, v in WebBrowserAsyncAdapter._all_tasks.items()}
                    
                    return {
                        "background_tasks": list(self._background_tasks.keys()),
                        "class_tasks": class_tasks,
                        "available_tools": [t.name for t in tools],
                        "browser_tool_attributes": dir(browser_tool)
                    }
                except Exception as e:
                    return {"error": str(e)}
            
            return {
                "background_tasks": list(self._background_tasks.keys()),
                "error": "WebBrowserAsync tool not found or not properly initialized",
                "available_tools": [t.name for t in (tools or [])]
            }
                
        # Add endpoint for health check
        @app.get("/health")
        async def health_check():
            """
            Simple health check endpoint.
            """
            return {"status": "ok", "assistant": self.assistant.name or "Assistant"}

        # Add metadata endpoint with assistant info
        @app.get("/info")
        async def agent_info():
            """
            Get information about the assistant.
            """
            info = {
                "name": self.assistant.name,
                "description": self.assistant.description,
                "llm_provider": self.assistant.llm,
                "llm_model": self.assistant.llm_model,
                "has_tools": len(self.assistant.tools or []) > 0,
                "has_memory": bool(self.assistant.memory),
                "has_rag": bool(self.assistant.rag and self.assistant.rag != "None")
            }
            return info

        # Add endpoint for memory management
        if hasattr(self.assistant, "memory") and self.assistant.memory:
            @app.post("/memory/clear")
            async def clear_memory():
                """
                Clear the assistant's conversation memory.
                """
                self.assistant.memory.clear()
                return {"status": "success", "message": "Memory cleared"}

            @app.get("/memory")
            async def get_memory():
                """
                Get the assistant's conversation memory.
                """
                if hasattr(self.assistant.memory, "storage") and self.assistant.memory.storage:
                    entries = self.assistant.memory.storage.retrieve()
                    memory_entries = [{"role": e.role, "content": e.content, "timestamp": e.timestamp} for e in entries]
                    return {"memory": memory_entries}
                return {"memory": []}

        # Implement image processing if the LLM supports it
        if hasattr(self.assistant.llm_instance, "supports_vision") and self.assistant.llm_instance.supports_vision:
            @app.post("/process_image")
            async def process_image(background_tasks: BackgroundTasks, request: Request):
                """
                Process an image with the assistant.
                """
                form = await request.form()
                
                # Get the prompt
                prompt = form.get("prompt", "")
                
                # Get the image file
                image_file = form.get("image")
                if not image_file:
                    raise HTTPException(status_code=400, detail="No image provided")
                
                try:
                    # Read image data
                    image_data = await image_file.read()
                    
                    # Check if streaming is requested
                    stream = form.get("stream", "").lower() == "true"
                    
                    if stream:
                        task_id = f"image_{uuid.uuid4()}"
                        self._background_tasks[task_id] = {"status": "processing"}
                        
                        background_tasks.add_task(
                            self._process_image_in_background,
                            task_id=task_id,
                            prompt=prompt,
                            image_data=image_data
                        )
                        
                        return {"task_id": task_id, "status": "processing"}
                    else:
                        # Process the image
                        from io import BytesIO
                        from PIL import Image
                        
                        # Convert bytes to PIL Image
                        image = Image.open(BytesIO(image_data))
                        
                        # Generate response
                        response = self.assistant._generate_response_from_image(prompt, image)
                        
                        return {"status": "success", "response": response}
                except Exception as e:
                    logger.error(f"Error processing image: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

        return app

    def _start_streaming_task(self, message: str, tool_params: Optional[Dict[str, Any]] = None) -> str:
        """Start a background task for streaming responses"""
        task_id = f"stream_{uuid.uuid4()}"
        self._background_tasks[task_id] = {"status": "processing"}
        
        # Start the task in a separate thread
        threading.Thread(
            target=self._execute_agent_in_background,
            args=(task_id, message, tool_params),
            daemon=True
        ).start()
        
        return task_id
        
    def _execute_agent_in_background(self, task_id: str, message: str, tool_params: Optional[Dict[str, Any]] = None):
        """Execute the assistant in a background thread"""
        try:
            kwargs = {}
            if tool_params:
                kwargs.update(tool_params)
                
            response = self.assistant._generate_response(message=message, **kwargs)
            self._background_tasks[task_id] = {
                "status": "completed",
                "result": response
            }
        except Exception as e:
            logger.error(f"Error in background task: {e}")
            self._background_tasks[task_id] = {
                "status": "error",
                "error": str(e)
            }
            
    def _execute_tool_in_background(self, task_id: str, tool, input_data: Dict[str, Any]):
        """Execute a tool in a background thread"""
        try:
            # Set the LLM instance if not already set
            if not tool.llm and self.assistant.llm_instance:
                tool.llm = self.assistant.llm_instance
                
            # Special handling for WebBrowserAsync
            if tool.name == "WebBrowserAsync":
                # The tool itself will manage its own task status
                result = tool.execute(input_data)
                
                # IMPORTANT: Store the task_id that was actually generated by the tool
                # Extract the UUID part from the returned task_id
                tool_task_id = result.get("task_id", "")
                
                # Store this mapping in background_tasks
                self._background_tasks[task_id] = {
                    "status": "processing",
                    "task_details": result,
                    "actual_task_id": tool_task_id  # Store the actual task_id
                }
                
                # Log the mapping for debugging
                logger.info(f"Mapping API task_id {task_id} to tool task_id {tool_task_id}")
            else:
                # Execute the tool
                result = tool.execute(input_data)
                self._background_tasks[task_id] = {
                    "status": "completed",
                    "result": result
                }
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            self._background_tasks[task_id] = {
                "status": "error",
                "error": str(e)
            }
            
    def _process_image_in_background(self, task_id: str, prompt: str, image_data: bytes):
        """Process an image in a background thread"""
        try:
            from io import BytesIO
            from PIL import Image
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            
            # Generate response
            response = self.assistant._generate_response_from_image(prompt, image)
            
            self._background_tasks[task_id] = {
                "status": "completed",
                "result": response
            }
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self._background_tasks[task_id] = {
                "status": "error",
                "error": str(e)
            }

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the FastAPI app.

        Args:
            host (str): The host address to run the API server on. Default is "0.0.0.0".
            port (int): The port to run the API server on. Default is 8000.
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)