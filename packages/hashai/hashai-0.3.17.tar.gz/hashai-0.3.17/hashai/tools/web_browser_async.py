from .base_tool import BaseTool
from typing import Dict, Any, Optional, List, ClassVar
from pydantic import Field, PrivateAttr
import threading
import logging
import time
import uuid
import json
import re
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class WebBrowserAsyncAdapter(BaseTool):
    """
    Async adapter for the WebBrowser tool that allows it to be used in an async context.
    This wrapper runs the WebBrowser tool in a separate thread and provides detailed progress updates.
    """
    name: str = Field("WebBrowserAsync", description="Async version of WebBrowser tool")
    description: str = Field(
        "Asynchronous web automation tool with multi-strategy element identification, self-healing selectors, and real-time progress reporting.",
        description="Tool description"
    )
    
    # Use PrivateAttr for instance-level attributes that shouldn't be part of the model
    _web_browser_tool: Any = PrivateAttr(default=None)
    _tasks: Dict[str, Dict[str, Any]] = PrivateAttr(default_factory=dict)
    _log_handler: Any = PrivateAttr(default=None)
    _logger: Any = PrivateAttr(default=None)
    
    # Screenshot directory
    screenshot_dir: str = Field("./screenshots", description="Directory to store screenshots")
    
    # Class-level static variable to store all tasks (outside the Pydantic model)
    _all_tasks: ClassVar[Dict[str, Dict[str, Any]]] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize private attributes
        self._tasks = {}
        self._logger = logging.getLogger(__name__)
        
        # Dynamically import the WebBrowser tool
        try:
            from .web_browser import WebBrowserTool
            # Create a custom logger for the WebBrowser tool
            web_browser_logger = self._create_custom_logger()
            
            # Pass any parameters to the WebBrowser tool
            self._web_browser_tool = WebBrowserTool(*args, **kwargs)
            
            # Attach our custom logger to capture logs
            object.__setattr__(self._web_browser_tool, "logger", web_browser_logger)
        except ImportError:
            raise ImportError("WebBrowserTool not found. Make sure it's properly installed.")
        
        # Create screenshot directory
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Log initialization
        self._logger.info("WebBrowserAsyncAdapter initialized")
    
    def _create_custom_logger(self):
        """Create a custom logger that will capture logs for progress updates"""
        logger = logging.getLogger(f"webbrowser_async_{uuid.uuid4()}")
        logger.setLevel(logging.INFO)
        
        # Create a handler that will store logs in memory
        class TaskProgressHandler(logging.Handler):
            def __init__(self, task_id=None):
                super().__init__()
                self.logs = []
                self.task_id = task_id
                self.parent = None  # Reference to the adapter
                
            def emit(self, record):
                log_entry = {
                    "timestamp": time.time(),
                    "level": record.levelname,
                    "message": self.format(record)
                }
                
                self.logs.append(log_entry)
                
                # If parent and task_id are set, update the task's progress
                if self.parent and self.task_id and self.task_id in WebBrowserAsyncAdapter._all_tasks:
                    # Parse the message to determine task progress
                    task_info = self._parse_log_message(record.message)
                    if task_info:
                        WebBrowserAsyncAdapter._all_tasks[self.task_id]["steps"].append(task_info)
                        
                        # Update progress percentage based on completed tasks
                        if "Executing task:" in record.message:
                            # Extract the task number if it's in the format "Task X of Y"
                            match = re.search(r"task (\d+) of (\d+)", record.message.lower())
                            if match:
                                current = int(match.group(1))
                                total = int(match.group(2))
                                progress = min(int((current / total) * 100), 95)  # Cap at 95% until fully done
                                WebBrowserAsyncAdapter._all_tasks[self.task_id]["progress"] = progress
                            elif "plan contains" in record.message.lower():
                                # Extract the total number of tasks
                                match = re.search(r"plan contains (\d+) tasks", record.message.lower())
                                if match:
                                    WebBrowserAsyncAdapter._all_tasks[self.task_id]["total_tasks"] = int(match.group(1))
                                    WebBrowserAsyncAdapter._all_tasks[self.task_id]["current_task"] = 0
                            else:
                                # Increment the current task
                                current = WebBrowserAsyncAdapter._all_tasks[self.task_id].get("current_task", 0) + 1
                                total = WebBrowserAsyncAdapter._all_tasks[self.task_id].get("total_tasks", 0)
                                if total > 0:
                                    progress = min(int((current / total) * 100), 95)
                                    WebBrowserAsyncAdapter._all_tasks[self.task_id]["progress"] = progress
                                    WebBrowserAsyncAdapter._all_tasks[self.task_id]["current_task"] = current
                                    
                            # Take a screenshot at the beginning of each task
                            try:
                                self.parent._take_screenshot(self.task_id, f"task_{current}")
                            except Exception as e:
                                logger.error(f"Error taking screenshot: {e}")
                        
                        # Check for failure screenshot capture message
                        if "Failure captured: Screenshot at " in record.message:
                            match = re.search(r"Screenshot at ([^\s,]+)", record.message)
                            if match:
                                screenshot_file = match.group(1)
                                # File might be in the current directory rather than screenshots directory
                                if os.path.exists(screenshot_file):
                                    # Move it to the screenshots directory
                                    import shutil
                                    dest_path = os.path.join(self.parent.screenshot_dir, os.path.basename(screenshot_file))
                                    shutil.move(screenshot_file, dest_path)
                                    self.parent._add_screenshot_to_task(self.task_id, os.path.basename(screenshot_file))
                                    
                        # Check for action completion to take a screenshot
                        if "completed in" in record.message and "Action" in record.message:
                            try:
                                self.parent._take_screenshot(self.task_id, f"action_{int(time.time())}")
                            except Exception as e:
                                logger.error(f"Error taking screenshot after action: {e}")
                        
                        # Set final progress to 100% when complete
                        if "Total execution time:" in record.message:
                            WebBrowserAsyncAdapter._all_tasks[self.task_id]["progress"] = 100
                            
                            # Take final screenshot
                            try:
                                self.parent._take_screenshot(self.task_id, "final")
                            except Exception as e:
                                logger.error(f"Error taking final screenshot: {e}")
            
            def _parse_log_message(self, message: str) -> Optional[Dict[str, Any]]:
                """Parse log messages to extract task info"""
                # Check for task execution
                if "Executing task:" in message:
                    task_description = message.replace("Executing task:", "").strip()
                    return {
                        "type": "task_start",
                        "description": task_description,
                        "status": "running"
                    }
                # Check for action completion
                elif "completed in" in message and "Action" in message:
                    match = re.search(r"Action '([^']+)' completed in ([0-9.]+) seconds", message)
                    if match:
                        action = match.group(1)
                        duration = float(match.group(2))
                        return {
                            "type": "task_complete",
                            "action": action,
                            "duration": duration,
                            "status": "success"
                        }
                # Check for errors
                elif "failed:" in message or "error:" in message.lower():
                    return {
                        "type": "error",
                        "message": message,
                        "status": "error"
                    }
                # Check for plan generation
                elif "Plan contains" in message:
                    match = re.search(r"Plan contains (\d+) tasks", message)
                    if match:
                        total_tasks = int(match.group(1))
                        return {
                            "type": "plan",
                            "total_tasks": total_tasks,
                            "status": "planning"
                        }
                # Default progress update
                elif any(keyword in message.lower() for keyword in ["waiting", "navigating", "typing", "clicking"]):
                    return {
                        "type": "progress",
                        "message": message,
                        "status": "running"
                    }
                return None
        
        # Create our handler instance
        handler = TaskProgressHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Store the handler for later use
        self._log_handler = handler
        
        return logger
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the WebBrowser tool asynchronously by running it in a background thread.
        
        Args:
            input_data (Dict[str, Any]): Input parameters for the WebBrowser tool
            
        Returns:
            Dict[str, Any]: A task ID that can be used to poll for results
        """
        if not self._web_browser_tool:
            return {
                "status": "error",
                "message": "WebBrowserTool not initialized"
            }
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Debug logging
        self._logger.info(f"Creating new task with ID: {task_id}")
        self._logger.info(f"Current tasks: {list(WebBrowserAsyncAdapter._all_tasks.keys())}")
        
        # Store task information in class-level dictionary
        WebBrowserAsyncAdapter._all_tasks[task_id] = {
            "status": "initializing",
            "start_time": time.time(),
            "result": None,
            "error": None,
            "progress": 0,
            "steps": [],
            "current_task": 0,
            "total_tasks": 0,
            "screenshots": []  # To track screenshots
        }
        
        # Also store in instance-level dictionary for reference
        self._tasks[task_id] = WebBrowserAsyncAdapter._all_tasks[task_id]
        
        # Make sure the tool has access to the LLM
        if not self._web_browser_tool.llm and self.llm:
            self._web_browser_tool.llm = self.llm
        
        # Update the log handler with task ID and parent reference
        if hasattr(self, "_log_handler") and self._log_handler:
            self._log_handler.task_id = task_id
            self._log_handler.parent = self
        
        # Start the tool execution in a background thread
        thread = threading.Thread(
            target=self._run_browser_in_thread,
            args=(task_id, input_data),
            daemon=True
        )
        thread.start()
        
        # Update status to running
        WebBrowserAsyncAdapter._all_tasks[task_id]["status"] = "running"
        
        return {
            "status": "running",
            "task_id": f"tool_WebBrowserAsync_{task_id}",
            "message": "Browser automation started in background thread"
        }
    
    def _run_browser_in_thread(self, task_id: str, input_data: Dict[str, Any]) -> None:
        """
        Run the WebBrowser tool in a background thread.
        
        Args:
            task_id (str): The unique task ID
            input_data (Dict[str, Any]): Input parameters for the WebBrowser tool
        """
        try:
            # Ensure we have a query parameter
            if "query" not in input_data and "message" in input_data:
                input_data["query"] = input_data["message"]
                del input_data["message"]
            
            # Take initial screenshot (might be blank/startup screen)
            # Only attempt if the page is available
            if hasattr(self._web_browser_tool, "page") and self._web_browser_tool.page:
                try:
                    self._take_screenshot(task_id, "initial")
                except Exception as e:
                    self._logger.warning(f"Error taking initial screenshot: {e}")
            
            # Execute the WebBrowser tool
            result = self._web_browser_tool.execute(input_data)
            
            # Take final screenshot if the browser is still running
            if hasattr(self._web_browser_tool, "page") and self._web_browser_tool.page:
                try:
                    self._take_screenshot(task_id, "final")
                except Exception as e:
                    self._logger.warning(f"Error taking final screenshot: {e}")
            
            # Update task status
            WebBrowserAsyncAdapter._all_tasks[task_id].update({
                "status": "completed",
                "result": result,
                "progress": 100,
                "end_time": time.time()
            })
        except Exception as e:
            # Log the error
            self._logger.error(f"Error running WebBrowser tool: {e}")
            
            # Update task status
            WebBrowserAsyncAdapter._all_tasks[task_id].update({
                "status": "error",
                "error": str(e),
                "progress": 100,
                "end_time": time.time()
            })
    
    def _take_screenshot(self, task_id: str, name_prefix: str) -> Optional[str]:
        """
        Take a screenshot of the current browser state.
        
        Args:
            task_id (str): The task ID
            name_prefix (str): Prefix for the screenshot filename
            
        Returns:
            Optional[str]: The screenshot filename or None if failed
        """
        if not hasattr(self._web_browser_tool, "page") or not self._web_browser_tool.page:
            logger.warning("No page object available for screenshot")
            return None
        
        try:
            # Create a filename with task_id and timestamp
            filename = f"{name_prefix}_{task_id}_{int(time.time())}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Take screenshot
            self._web_browser_tool.page.screenshot(path=filepath)
            
            # Add to task's screenshots
            self._add_screenshot_to_task(task_id, filename)
            
            return filename
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def _add_screenshot_to_task(self, task_id: str, screenshot_filename: str) -> None:
        """Add a screenshot to the task's list of screenshots"""
        if task_id in WebBrowserAsyncAdapter._all_tasks:
            if "screenshots" not in WebBrowserAsyncAdapter._all_tasks[task_id]:
                WebBrowserAsyncAdapter._all_tasks[task_id]["screenshots"] = []
            
            # Add if not already in the list
            if screenshot_filename not in WebBrowserAsyncAdapter._all_tasks[task_id]["screenshots"]:
                WebBrowserAsyncAdapter._all_tasks[task_id]["screenshots"].append(screenshot_filename)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a background task with detailed progress information.
        
        Args:
            task_id (str): The unique task ID or UUID part
            
        Returns:
            Dict[str, Any]: The current status of the task with step-by-step progress
        """
        # Debug logging
        self._logger.info(f"Getting status for task: {task_id}")
        self._logger.info(f"Available tasks: {list(WebBrowserAsyncAdapter._all_tasks.keys())}")
        
        # Check for direct match
        if task_id in WebBrowserAsyncAdapter._all_tasks:
            task_info = WebBrowserAsyncAdapter._all_tasks[task_id]
        else:
            # Check if this is the UUID part from a full task ID
            # First, check if any existing task ID ends with this UUID
            matching_id = None
            for tid in WebBrowserAsyncAdapter._all_tasks.keys():
                if tid.endswith(task_id):
                    matching_id = tid
                    break
            
            # Next, check if it's a full task ID with the format tool_WebBrowserAsync_UUID
            if task_id.startswith("tool_WebBrowserAsync_"):
                uuid_part = task_id.split("_", 2)[2]
                if uuid_part in WebBrowserAsyncAdapter._all_tasks:
                    matching_id = uuid_part
            
            if matching_id:
                task_info = WebBrowserAsyncAdapter._all_tasks[matching_id]
                # Log that we found a match
                self._logger.info(f"Found matching task ID: {matching_id}")
            else:
                # No match found
                self._logger.warning(f"Task {task_id} not found")
                return {
                    "status": "error",
                    "message": f"Task {task_id} not found",
                    "progress": 0,
                    "steps": [],
                    "screenshots": []
                }
        
        # Calculate task duration
        duration = (task_info.get("end_time") or time.time()) - task_info["start_time"]
        
        # Create response with task information
        response = {
            "status": task_info["status"],
            "progress": task_info.get("progress", 0),
            "duration": round(duration, 2),
            "steps": task_info.get("steps", []),
            "current_task": task_info.get("current_task", 0),
            "total_tasks": task_info.get("total_tasks", 0),
            "screenshots": task_info.get("screenshots", [])
        }
        
        # Add result or error if available
        if task_info["status"] == "completed":
            response["result"] = task_info.get("result")
            
            # Clean up completed tasks after retrieval, but not too soon
            # Only clean up if it's been at least 5 minutes since completion
            if duration > 300:
                WebBrowserAsyncAdapter._all_tasks.pop(task_id, None)
                
        elif task_info["status"] == "error":
            response["error"] = task_info.get("error")
        
        return response
    
    def take_live_screenshot(self, task_id: str) -> Optional[str]:
        """
        Take a live screenshot of the current browser state.
        
        Args:
            task_id (str): The task ID
            
        Returns:
            Optional[str]: The screenshot filename or None if failed
        """
        # Check if this is a full task ID
        if task_id.startswith("tool_WebBrowserAsync_"):
            task_id = task_id.split("_", 2)[2]
            
        return self._take_screenshot(task_id, "live")