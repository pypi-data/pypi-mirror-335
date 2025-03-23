# web_browser.py
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from pydantic import Field, BaseModel
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError, BrowserContext, Locator
import json, time, re, logging, os, difflib, base64
from io import BytesIO
from PIL import Image
import numpy as np
from .base_tool import BaseTool

# Global logger
logger = logging.getLogger(__name__)

class BrowserPlan(BaseModel):
    tasks: List[Dict[str, Any]] = Field(
        ...,
        description="List of automation tasks to execute"
    )

class WebBrowserTool(BaseTool):
    name: str = Field("WebBrowser", description="Name of the tool")
    description: str = Field(
        "Advanced web automation tool with multi-strategy element identification, self-healing selectors, visual verification, automated testing, smart waiting, and robust error recovery.",
        description="Tool description"
    )
    default_timeout: int = 15000  # 15 seconds in milliseconds
    max_retries: int = 3
    element_detection_strategies: List[str] = Field(
        ["css", "xpath", "text", "aria", "vision", "fuzzy", "proximity"],
        description="Prioritized list of element detection strategies"
    )
    class Config:
        extra = "allow"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bypass Pydantic's restrictions for extra attributes
        object.__setattr__(self, "logger", logging.getLogger(__name__))
        object.__setattr__(self, "browser_context", None)
        object.__setattr__(self, "browser", None)
        object.__setattr__(self, "page", None)
        object.__setattr__(self, "_known_elements", {})  # Cache of successfully located elements
        object.__setattr__(self, "_selector_alternatives", {})  # Map of failed selectors to successful alternatives
        object.__setattr__(self, "_previous_states", [])  # Store previous page states for comparison

    def execute(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the browser automation workflow.
        Maintains a context string of executed tasks and passes it to fallback routines.
        DOES NOT close the browser after successful execution.
        """
        overall_start = time.time()
        results = []  # to hold summaries of executed tasks (for context)
        current_url = ""
        
        try:
            headless = input.get("headless", False)
            self.default_timeout = int(input.get("timeout", 15)) * 1000
            self.max_retries = int(input.get("max_retries", self.max_retries))
            
            # Check if a browser session is already active
            if not self.browser or not self.browser_context or not self.page:
                # Start Playwright without a "with" block so we can leave the browser open
                p = sync_playwright().start()
                self.browser = p.chromium.launch(
                    headless=headless,
                    args=['--disable-features=site-per-process', '--disable-web-security']  # Better iframe handling
                )
                self.browser_context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    ignore_https_errors=True,
                    has_touch=True,
                    locale='en-US'
                )
                
                # Set up event handlers for network monitoring
                self.browser_context.on("request", self._handle_request)
                self.browser_context.on("response", self._handle_response)
                
                # Create a new page
                self.page = self.browser_context.new_page()
                
                # Enable smart navigation
                self.page.set_default_timeout(self.default_timeout)
                
                # Inject utility scripts for better element detection
                self._inject_helper_scripts()
            
            plan = self._generate_plan(input.get("query", ""), current_url)
            if not plan.tasks:
                raise ValueError("No valid tasks in the generated plan.")

            # Map actions to handlers
            action_map: Dict[str, Callable[[Page, Dict[str, Any]], Dict[str, Any]]] = {
                "navigate": lambda p, task: self._handle_navigation(p, task.get("value", "")),
                "click": lambda p, task: self._handle_click(p, task.get("selector", "")),
                "type": lambda p, task: self._handle_typing(p, task.get("selector", ""), task.get("value", ""), task),
                "wait": lambda p, task: self._handle_wait(task.get("value", "")),
                "wait_for_ajax": lambda p, task: self._handle_wait_for_ajax(p, task.get("value", "")),
                "wait_for_navigation": lambda p, task: self._handle_wait_for_navigation(p, task.get("value", "")),
                "wait_for_selector": lambda p, task: self._handle_wait_for_selector(p, task.get("selector", ""), task.get("value", "")),
                "wait_for_function": lambda p, task: self._handle_wait_for_function(p, task.get("value", "")),
                "scroll": lambda p, task: self._handle_scroll(p, task.get("selector", "")),
                "hover": lambda p, task: self._handle_hover(p, task.get("selector", "")),
                "screenshot": lambda p, task: self._handle_screenshot(p, task.get("value", "screenshot.png")),
                "switch_tab": lambda p, task: self._handle_switch_tab(self.browser_context, task.get("value", "0")),
                "execute_script": lambda p, task: self._handle_execute_script(p, task.get("value", "")),
                "drag_and_drop": lambda p, task: self._handle_drag_and_drop(p, task.get("selector", ""), task.get("value", "")),
                "select_option": lambda p, task: self._handle_select_option(p, task.get("selector", ""), task.get("value", "")),
                "check": lambda p, task: self._handle_checkbox(p, task.get("selector", ""), True),
                "uncheck": lambda p, task: self._handle_checkbox(p, task.get("selector", ""), False),
                "press_key": lambda p, task: self._handle_press_key(p, task.get("value", "")),
                "file_upload": lambda p, task: self._handle_file_upload(p, task.get("selector", ""), task.get("value", "")),
                "verify_text": lambda p, task: self._handle_verify_text(p, task.get("value", "")),
                "verify_element": lambda p, task: self._handle_verify_element(p, task.get("selector", "")),
                "handle_dialog": lambda p, task: self._handle_dialog(p, task.get("value", "accept")),
                "switch_frame": lambda p, task: self._handle_switch_frame(p, task.get("selector", "")),
                "retry_with_delay": lambda p, task: self._handle_retry_with_delay(p, task.get("value", "")),
                "refresh": lambda p, task: self._handle_refresh(p),
                "back": lambda p, task: self._handle_back(p),
                "forward": lambda p, task: self._handle_forward(p),
                "close_tab": lambda p, task: self._handle_close_tab(p),
            }
            
            for task in plan.tasks:
                # Take a snapshot of the current page state for comparison/healing
                self._capture_page_state()
                
                # Handle pop-ups, dialogs, modals automatically
                self._handle_interruptions(task.get("description", ""))
                
                action = task.get("action", "").lower()
                task_description = task.get("description", action)
                self.logger.info(f"Executing task: {task_description}")
                start_time = time.time()

                # Build a context string from previously executed tasks
                executed_context = "\n".join([f"{r['action']}: {r['message']}" for r in results])
                handler = action_map.get(action)
                if not handler:
                    results.append({
                        "action": action,
                        "success": False,
                        "message": f"Unsupported action: {action}"
                    })
                    continue

                result = self._execute_with_retries(self.page, task, handler, executed_context)
                elapsed = time.time() - start_time
                result["elapsed"] = elapsed
                self.logger.info(f"Action '{action}' completed in {elapsed:.2f} seconds.")
                results.append(result)

                if not result.get("success", False):
                    self.logger.error(f"Task failed: {result.get('message')}")
                    self._capture_failure_screenshot(self.page, action)
                    
                    # Try a high-level recovery strategy if possible
                    if self._attempt_recovery(task, executed_context):
                        self.logger.info("Recovery was successful, continuing with next task")
                    else:
                        self.logger.error("Recovery failed, stopping execution")
                        break

                current_url = self.page.url

            overall_elapsed = time.time() - overall_start
            self.logger.info(f"Total execution time: {overall_elapsed:.2f} seconds.")
            
            # Return results but keep the browser open
            return {"status": "success", "results": results, "total_time": overall_elapsed}
        except Exception as e:
            self.logger.exception("Execution error:")
            return {"status": "error", "message": str(e)}

    def _capture_page_state(self):
        """Capture the current page state for comparison and self-healing"""
        try:
            # Limit the history to last 5 states to avoid memory bloat
            if len(self._previous_states) >= 5:
                self._previous_states.pop(0)
            
            # Capture visible elements with attributes for later comparison
            elements = self.page.evaluate("""
                () => {
                    const visibleElements = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"]'))
                        .filter(el => {
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0 && 
                                   window.getComputedStyle(el).display !== 'none' &&
                                   window.getComputedStyle(el).visibility !== 'hidden';
                        });
                    
                    return visibleElements.map(el => {
                        return {
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            classList: Array.from(el.classList),
                            text: el.innerText,
                            attributes: {
                                type: el.getAttribute('type'),
                                name: el.getAttribute('name'),
                                placeholder: el.getAttribute('placeholder'),
                                'aria-label': el.getAttribute('aria-label'),
                                role: el.getAttribute('role'),
                                title: el.getAttribute('title')
                            },
                            position: el.getBoundingClientRect()
                        };
                    });
                }
            """)
            
            self._previous_states.append({
                "url": self.page.url,
                "elements": elements,
                "timestamp": time.time()
            })
        except Exception as e:
            self.logger.warning(f"Failed to capture page state: {e}")

    def _inject_helper_scripts(self):
        """Inject helper scripts for enhanced element detection and interaction"""
        try:
            self.page.evaluate("""
                window.browserAutomationHelpers = {
                    findElementByTextContent: function(text, fuzzy = false) {
                        text = text.toLowerCase();
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            const content = el.textContent || '';
                            if (fuzzy) {
                                if (content.toLowerCase().includes(text)) return el;
                            } else {
                                if (content.toLowerCase() === text) return el;
                            }
                        }
                        return null;
                    },
                    
                    waitForNetworkIdle: function(maxTimeout = 5000) {
                        return new Promise((resolve) => {
                            let networkRequestsInFlight = 0;
                            let timeoutId = null;
                            
                            const originalFetch = window.fetch;
                            const originalXHR = window.XMLHttpRequest.prototype.open;
                            
                            const startTimeout = () => {
                                if (timeoutId) clearTimeout(timeoutId);
                                timeoutId = setTimeout(() => {
                                    resolve('timeout');
                                }, maxTimeout);
                            };
                            
                            window.fetch = function() {
                                networkRequestsInFlight++;
                                return originalFetch.apply(this, arguments)
                                    .finally(() => {
                                        networkRequestsInFlight--;
                                        if (networkRequestsInFlight === 0) {
                                            setTimeout(resolve, 500);
                                        }
                                    });
                            };
                            
                            window.XMLHttpRequest.prototype.open = function() {
                                networkRequestsInFlight++;
                                this.addEventListener('loadend', () => {
                                    networkRequestsInFlight--;
                                    if (networkRequestsInFlight === 0) {
                                        setTimeout(resolve, 500);
                                    }
                                });
                                return originalXHR.apply(this, arguments);
                            };
                            
                            startTimeout();
                            
                            // If no requests are currently in flight, wait a bit and resolve
                            if (networkRequestsInFlight === 0) {
                                setTimeout(resolve, 1000);
                            }
                        });
                    },
                    
                    getAccessibleName: function(element) {
                        // Implementation follows ARIA algorithm for determining accessible name
                        if (element.getAttribute('aria-labelledby')) {
                            const ids = element.getAttribute('aria-labelledby').split(/\\s+/);
                            return ids.map(id => {
                                const labelElement = document.getElementById(id);
                                return labelElement ? labelElement.textContent : '';
                            }).join(' ');
                        }
                        
                        if (element.getAttribute('aria-label')) {
                            return element.getAttribute('aria-label');
                        }
                        
                        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') {
                            const labels = Array.from(document.querySelectorAll(`label[for="${element.id}"]`));
                            if (labels.length > 0) {
                                return labels.map(label => label.textContent).join(' ');
                            }
                            
                            let parent = element.parentElement;
                            while (parent) {
                                if (parent.tagName === 'LABEL') {
                                    return parent.textContent;
                                }
                                parent = parent.parentElement;
                            }
                        }
                        
                        return element.textContent || element.getAttribute('title') || '';
                    },
                    
                    findElementByAccessibleName: function(name) {
                        const allElements = Array.from(document.querySelectorAll('*'));
                        name = name.toLowerCase();
                        
                        return allElements.find(el => {
                            const accessibleName = this.getAccessibleName(el).toLowerCase();
                            return accessibleName.includes(name);
                        });
                    },
                    
                    findElementNearText: function(text, elementType = null) {
                        const textElements = Array.from(document.querySelectorAll('*')).filter(el => 
                            el.textContent && el.textContent.toLowerCase().includes(text.toLowerCase())
                        );
                        
                        if (textElements.length === 0) return null;
                        
                        // Helper to find the nearest element of given type
                        const findNearestOfType = (sourceEl, type) => {
                            // Look at siblings first
                            let sibling = sourceEl.nextElementSibling;
                            while (sibling) {
                                if (!type || sibling.tagName.toLowerCase() === type) return sibling;
                                sibling = sibling.nextElementSibling;
                            }
                            
                            // Look at parent's children
                            if (sourceEl.parentElement) {
                                const children = Array.from(sourceEl.parentElement.children);
                                for (const child of children) {
                                    if (child !== sourceEl && (!type || child.tagName.toLowerCase() === type)) {
                                        return child;
                                    }
                                }
                            }
                            
                            return null;
                        };
                        
                        // Try each text element and find nearest match
                        for (const el of textElements) {
                            const nearest = findNearestOfType(el, elementType);
                            if (nearest) return nearest;
                        }
                        
                        return null;
                    }
                };
            """)
            self.logger.info("Helper scripts injected successfully")
        except Exception as e:
            self.logger.error(f"Failed to inject helper scripts: {e}")

    def _handle_request(self, request):
        """Track network requests for better AJAX waiting"""
        try:
            if request.resource_type in ['xhr', 'fetch']:
                self.logger.debug(f"Network request: {request.method} {request.url}")
        except Exception as e:
            self.logger.error(f"Error in request handler: {e}")

    def _handle_response(self, response):
        """Track network responses for better AJAX waiting"""
        try:
            if response.request.resource_type in ['xhr', 'fetch']:
                self.logger.debug(f"Network response: {response.status} {response.url}")
        except Exception as e:
            self.logger.error(f"Error in response handler: {e}")

    def _handle_interruptions(self, task_context: str):
        """
        Proactively detect and handle various interruptions like modals, popups,
        cookie banners, and permission dialogs
        """
        try:
            # Handle dialogs (alerts, confirms, prompts)
            self.page.once("dialog", lambda dialog: self._auto_handle_dialog(dialog, task_context))
            
            # Handle cookie banners
            self._dismiss_cookie_banners()
            
            # Handle modals/popups
            self._dismiss_modals(task_context)
            
            # Handle blocked navigation (new tab/window)
            self._handle_blocked_navigation()
        except Exception as e:
            self.logger.warning(f"Error handling interruptions: {e}")

    def _auto_handle_dialog(self, dialog, task_context: str):
        """Automatically handle browser dialogs based on context"""
        dialog_text = dialog.message.lower()
        
        # If dialog is asking for confirmation to leave the page and that's not in our task
        if ("leave" in dialog_text or "exit" in dialog_text) and "navigate" not in task_context.lower():
            self.logger.info(f"Dismissing 'leave page' dialog: {dialog.message}")
            dialog.dismiss()
            return
        
        # Accept by default
        self.logger.info(f"Auto-accepting dialog: {dialog.message}")
        dialog.accept()

    def _dismiss_cookie_banners(self):
        """Identify and dismiss common cookie consent banners"""
        try:
            # Common cookie banner selectors and keywords
            cookie_selectors = [
                '[aria-label*="cookie" i]',
                '[class*="cookie" i]',
                '[id*="cookie" i]',
                '.cc-window',
                '.cookie-banner',
                '#cookie-notice',
                '[data-testid="cookie-policy-banner"]'
            ]
            
            cookie_button_keywords = ["accept", "agree", "allow", "consent", "got it", "ok", "continue"]
            
            # Try each selector
            for selector in cookie_selectors:
                elements = self.page.query_selector_all(selector)
                for element in elements:
                    if element.is_visible():
                        # Look for buttons within the cookie banner
                        buttons = element.query_selector_all("button, a.button, [role='button'], input[type='button']")
                        for button in buttons:
                            button_text = button.inner_text().lower()
                            if any(keyword in button_text for keyword in cookie_button_keywords):
                                self.logger.info(f"Dismissing cookie banner with button: {button_text}")
                                button.click()
                                return
                        
                        # If no specific button found, try a generic click on the first button
                        first_button = element.query_selector("button, a.button, [role='button']")
                        if first_button:
                            self.logger.info("Dismissing cookie banner with generic button")
                            first_button.click()
                            return
        except Exception as e:
            self.logger.warning(f"Error dismissing cookie banners: {e}")

    def _dismiss_modals(self, task_context: str):
        """Identify and handle modal dialogs"""
        modal_selectors = [
            ".modal", 
            "[role='dialog']", 
            ".popup", 
            ".overlay", 
            ".lightbox",
            "[class*='modal']",
            "[class*='popup']",
            "[class*='overlay']",
            "[aria-modal='true']"
        ]
        
        try:
            for selector in modal_selectors:
                elements = self.page.query_selector_all(selector)
                for modal in elements:
                    if modal.is_visible():
                        self._handle_modal(self.page, modal, task_context)
        except Exception as e:
            self.logger.warning(f"Error dismissing modals: {e}")

    # def _handle_modal(self, page: Page, modal_element, task_context: str):
    #     """Handle a modal dialog with LLM guidance"""
    #     try:
    #         # First, take a screenshot of the modal
    #         modal_screenshot = modal_element.screenshot()
            
    #         # Extract modal text for better context
    #         modal_text = page.evaluate("(el) => el.innerText", modal_element)
            
    #         prompt = (
    #             f"A modal is displayed on the page with the following text:\n\n{modal_text}\n\n"
    #             f"The current task context is: \"{task_context}\". "
    #             "Based on the content of the modal and the task context, decide whether to dismiss the modal. "
    #             "Return a JSON response in the format: { \"action\": \"dismiss\" } to dismiss, "
    #             "{ \"action\": \"interact\", \"element\": \"button text\" } to interact with a specific element, or "
    #             "{ \"action\": \"ignore\" } to leave it. "
    #             "Return only the JSON."
    #         )
            
    #         # If the LLM supports vision, use it
    #         if hasattr(self.llm, "supports_vision") and self.llm.supports_vision:
    #             response_text = self.llm.generate_from_image(prompt, image_bytes=modal_screenshot)
    #         else:
    #             response_text = self.llm.generate(prompt=prompt)
                
    #         self.logger.info(f"LLM response for modal analysis: {response_text}")
            
    #         # Extract JSON from the response
    #         json_match = re.search(r'```json\n?(.+?)\n?```', response_text, re.DOTALL)
    #         json_text = json_match.group(1).strip() if json_match else response_text.strip()
            
    #         try:
    #             decision = json.loads(json_text)
    #         except json.JSONDecodeError:
    #             # Try to extract just the JSON object
    #             json_pattern = r'\{.*\}'
    #             json_match = re.search(json_pattern, response_text, re.DOTALL)
    #             if json_match:
    #                 json_text = json_match.group(0)
    #                 decision = json.loads(json_text)
    #             else:
    #                 self.logger.warning("Could not parse LLM response as JSON")
    #                 decision = {"action": "ignore"}
            
    #         if decision.get("action") == "dismiss":
    #             # Try multiple strategies to dismiss the modal
    #             self._try_dismiss_strategies(modal_element)
    #         elif decision.get("action") == "interact" and decision.get("element"):
    #             # Try to find and click the specified element
    #             target_text = decision.get("element")
    #             self._click_element_by_text(modal_element, target_text)
    #         else:
    #             self.logger.info("Modal left intact according to LLM analysis.")
    #     except Exception as e:
    #         self.logger.error(f"Modal handling error: {e}")

    # def _try_dismiss_strategies(self, modal_element):
    #     """Try multiple strategies to dismiss a modal"""
    #     try:
    #         # Strategy 1: Look for close buttons by common selectors
    #         close_selectors = [
    #             ".close", 
    #             ".btn-close", 
    #             "[aria-label='Close']", 
    #             "[data-dismiss='modal']",
    #             "button.dismiss",
    #             ".modal-close",
    #             "button.close",
    #             "[title='Close']",
    #             ".dismiss-button"
    #         ]
            
    #         for selector in close_selectors:
    #             close_btns = modal_element.query_selector_all(selector)
    #             for btn in close_btns:
    #                 if btn.is_visible():
    #                     btn.click()
    #                     self.logger.info(f"Modal dismissed using close button: {selector}")
    #                     time.sleep(0.5)
    #                     return
            
    #         # Strategy 2: Look for buttons with X/close text or icon
    #         x_buttons = modal_element.query_selector_all("button, a")
    #         for btn in x_buttons:
    #             text = btn.inner_text().strip()
    #             if text in ["×", "X", "x", "Close", "CLOSE", "Dismiss", "DISMISS", "Cancel", "CANCEL", "No thanks"]:
    #                 btn.click()
    #                 self.logger.info(f"Modal dismissed using X button with text: {text}")
    #                 time.sleep(0.5)
    #                 return
            
    #         # Strategy 3: Try to use JavaScript to remove the modal
    #         self.page.evaluate("(modal) => modal.remove()", modal_element)
    #         self.logger.info("Modal dismissed by removal.")
    #         time.sleep(0.5)
    #     except Exception as e:
    #         self.logger.error(f"Error dismissing modal: {e}")

    def _click_element_by_text(self, container, text):
        """Click an element that contains the specified text"""
        try:
            # Try exact match first
            elements = container.query_selector_all(f"*:has-text('{text}')")
            for element in elements:
                if element.is_visible():
                    element.click()
                    self.logger.info(f"Clicked element with text: {text}")
                    return True
            
            # Try case-insensitive contains match
            script = f"""
                (container) => {{
                    const allElements = container.querySelectorAll('*');
                    const targetText = '{text}'.toLowerCase();
                    for (const el of allElements) {{
                        if (el.innerText && el.innerText.toLowerCase().includes(targetText) && 
                            getComputedStyle(el).display !== 'none') {{
                            return el;
                        }}
                    }}
                    return null;
                }}
            """
            element = self.page.evaluate(script, container)
            if element:
                container.evaluate("(el) => el.click()")
                self.logger.info(f"Clicked element containing text: {text}")
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Error clicking element by text: {e}")
            return False

    def _handle_blocked_navigation(self):
        """Handle cases where popups or new windows are blocked"""
        try:
            # Add an event listener for popups
            self.page.evaluate("""
                window.addEventListener('click', function(e) {
                    // Find closest anchor or button element
                    let target = e.target;
                    while (target && target !== document.body) {
                        if (target.tagName === 'A' || target.tagName === 'BUTTON') {
                            break;
                        }
                        target = target.parentElement;
                    }
                    
                    if (target && target.tagName === 'A') {
                        // Check if it's trying to open in a new tab/window
                        if (target.getAttribute('target') === '_blank') {
                            // Modify it to open in the same tab
                            e.preventDefault();
                            target.setAttribute('target', '_self');
                            target.click();
                        }
                    }
                }, true);
            """)
        except Exception as e:
            self.logger.warning(f"Error setting up popup handler: {e}")

    def _generate_plan(self, query: str, current_url: str) -> BrowserPlan:
        """Generate an automation plan from the query using the LLM"""
        current_date = time.strftime("%Y-%m-%d")
        current_time = time.strftime("%H:%M:%S")
        
        # Get page metadata if already navigated to a URL
        page_metadata = {}
        if current_url and self.page:
            try:
                # Extract page title
                page_metadata["title"] = self.page.title()
                
                # Count interactive elements to help with context
                page_metadata["interactive_elements"] = self.page.evaluate("""
                    () => {
                        const counts = {
                            buttons: document.querySelectorAll('button, [role="button"]').length,
                            links: document.querySelectorAll('a').length,
                            inputs: document.querySelectorAll('input, textarea, select').length,
                            forms: document.querySelectorAll('form').length
                        };
                        return counts;
                    }
                """)
                
                # Check if page is a form
                page_metadata["has_login_form"] = self.page.evaluate("""
                    () => {
                        const passwordInputs = document.querySelectorAll('input[type="password"]');
                        const loginKeywords = ['login', 'sign in', 'signin', 'log in', 'username', 'email'];
                        const formTexts = Array.from(document.querySelectorAll('form, form *')).map(el => el.innerText.toLowerCase());
                        
                        return passwordInputs.length > 0 || 
                            loginKeywords.some(keyword => document.body.innerText.toLowerCase().includes(keyword));
                    }
                """)
                
                # Check if page is a search page
                page_metadata["has_search"] = self.page.evaluate("""
                    () => {
                        const searchInputs = document.querySelectorAll('input[type="search"], input[name*="search" i], input[placeholder*="search" i]');
                        return searchInputs.length > 0;
                    }
                """)
            except Exception as e:
                self.logger.error(f"Error extracting page metadata: {e}")
        
        # Build the prompt with page context
        metadata_str = ""
        if page_metadata:
            metadata_str = "Current page metadata:\n"
            for key, value in page_metadata.items():
                metadata_str += f"- {key}: {value}\n"
        
        prompt = f"""Generate a detailed browser automation plan for: {query}

    Current URL: {current_url or 'No page loaded yet'}
    Current date: {current_date}
    Current time: {current_time}
    {metadata_str}

    Available actions:
    1. navigate - Go to a URL
    2. click - Click on an element
    3. type - Enter text into a form field
    4. wait - Wait for a specific time
    5. wait_for_ajax - Wait for network activity to complete
    6. wait_for_navigation - Wait for page navigation to complete
    7. wait_for_selector - Wait for a specific element to appear
    8. wait_for_function - Wait for a custom JavaScript condition
    9. scroll - Scroll to an element or page position
    10. hover - Move mouse over an element
    11. screenshot - Take a screenshot of the page
    12. switch_tab - Change to a different browser tab
    13. execute_script - Run custom JavaScript code
    14. drag_and_drop - Perform drag-and-drop action
    15. select_option - Choose an option from a select/dropdown
    16. check/uncheck - Check or uncheck a checkbox
    17. press_key - Press a keyboard key
    18. file_upload - Upload a file
    19. verify_text - Verify text appears on the page
    20. verify_element - Verify an element exists on the page
    21. handle_dialog - Handle JavaScript alerts/confirms/prompts
    22. switch_frame - Switch to an iframe
    23. retry_with_delay - Retry an action with a delay
    24. refresh - Refresh the current page
    25. back - Go back to the previous page
    26. forward - Go forward in history
    27. close_tab - Close the current tab

    Required JSON format:
    {{
        "tasks": [
            {{
                "action": "action_name",
                "selector": "CSS selector (where applicable)",
                "value": "value parameter (e.g., URL, text, duration)",
                "description": "human-readable description of the step"
            }}
        ]
    }}

    Guidelines:
    1. Always include wait steps after navigation and form submissions
    2. Use multiple selector strategies for robust element identification
    3. Add explicit wait_for_navigation after clicks that cause page loads
    4. For critical tasks, add verification steps to confirm success
    5. Include descriptive task descriptions for better context
    6. Break complex operations into smaller, more precise steps
    7. Add error handling with retry_with_delay for unstable operations
    8. Use wait_for_ajax when dealing with dynamic content
    9. Include scrolling before interacting with elements that might be out of view
    10. Use smart waiting strategies instead of fixed delays when possible

    Specific element identification strategies:
    - For buttons, try: button[type="submit"], .btn-primary, #submit-button, or button:has-text("Submit")
    - For inputs, try: input[name="search"], input[placeholder="Email"], #email-field
    - For login forms, use: input[type="email"], input[type="password"], button[type="submit"]
    - For clickable elements, provide multiple selector options separated by comma for better resilience

    For complex automations, include appropriate verification and error recovery steps.
    """

        # Get response from LLM
        try:
            response = self.llm.generate(prompt=prompt)
            self.logger.info("Generated automation plan from LLM")
            
            # Parse the plan
            plan = self._parse_plan(response)
            
            # Log the number of tasks
            self.logger.info(f"Plan contains {len(plan.tasks)} tasks")
            
            # Analyze plan quality
            if len(plan.tasks) == 0:
                self.logger.warning("Empty plan generated, using fallback plan")
                plan = self._generate_fallback_plan(query, current_url)
            
            # Ensure the plan starts with navigation if we're not already on a page
            if not current_url and len(plan.tasks) > 0 and plan.tasks[0].get("action") != "navigate":
                # Extract URL from query or use a search engine
                self.logger.info("Adding navigation step to the beginning of the plan")
                url = self._extract_url_from_query(query)
                navigate_task = {
                    "action": "navigate",
                    "value": url,
                    "selector": "",
                    "description": f"Navigate to {url}"
                }
                plan.tasks.insert(0, navigate_task)
            
            return plan
        except Exception as e:
            self.logger.error(f"Failed to generate plan: {e}")
            # Return a minimal fallback plan
            return self._generate_fallback_plan(query, current_url)

    def _generate_fallback_plan(self, query: str, current_url: str) -> BrowserPlan:
        """Generate a simple fallback plan when the LLM fails"""
        tasks = []
        
        # If we don't have a current URL, start with navigation
        if not current_url:
            url = self._extract_url_from_query(query)
            tasks.append({
                "action": "navigate",
                "value": url,
                "selector": "",
                "description": f"Navigate to {url}"
            })
        
        # Add basic tasks based on query keywords
        query_lower = query.lower()
        
        # Check for login intent
        if any(kw in query_lower for kw in ["login", "sign in", "log in", "signin"]):
            tasks.extend([
                {
                    "action": "type",
                    "selector": "input[type='email'], input[type='text'], input[name='username'], input[name='email']",
                    "value": "test@example.com",
                    "description": "Enter email/username"
                },
                {
                    "action": "type",
                    "selector": "input[type='password']",
                    "value": "password123",
                    "description": "Enter password"
                },
                {
                    "action": "click",
                    "selector": "button[type='submit'], input[type='submit'], button:has-text('Sign In'), button:has-text('Log In')",
                    "value": "",
                    "description": "Click login button"
                }
            ])
        # Check for search intent
        elif any(kw in query_lower for kw in ["search", "find", "look for"]):
            search_term = re.sub(r'search\s+for\s+|find\s+|look\s+for\s+', '', query_lower)
            tasks.extend([
                {
                    "action": "type",
                    "selector": "input[type='search'], input[name*='search' i], input[placeholder*='search' i]",
                    "value": search_term,
                    "description": f"Enter search term: {search_term}"
                },
                {
                    "action": "press_key",
                    "value": "Enter",
                    "description": "Press Enter to submit search"
                },
                {
                    "action": "wait_for_navigation",
                    "value": "5000",
                    "description": "Wait for search results to load"
                }
            ])
        # Default exploration tasks
        else:
            tasks.extend([
                {
                    "action": "screenshot",
                    "value": "initial_page.png",
                    "description": "Take screenshot of initial page"
                },
                {
                    "action": "scroll",
                    "value": "",
                    "description": "Scroll down the page"
                },
                {
                    "action": "wait",
                    "value": "2",
                    "description": "Wait for 2 seconds"
                },
                {
                    "action": "screenshot",
                    "value": "scrolled_page.png",
                    "description": "Take screenshot after scrolling"
                }
            ])
        
        return BrowserPlan(tasks=tasks)

    def _extract_url_from_query(self, query: str) -> str:
        """Extract a URL from the query or generate a search URL"""
        # Try to find a URL pattern
        url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
        url_match = url_pattern.search(query)
        
        if url_match:
            url = url_match.group(0)
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            return url
        
        # Check for common website names without http://
        domain_pattern = re.compile(r'\b([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
        domain_match = domain_pattern.search(query)
        
        if domain_match:
            return 'https://' + domain_match.group(0)
        
        # If no URL found, search on Google
        search_query = query.replace(' ', '+')
        return f'https://www.google.com/search?q={search_query}'
    
    # These methods should be added to the WebBrowserTool class

    def _handle_select_option(self, page: Page, selector: str, value: str) -> Dict[str, Any]:
        """Handle selecting an option from a dropdown menu"""
        if isinstance(selector, dict):
            selector = selector.get("selector", "")
            
        if isinstance(value, dict):
            value = value.get("value", "")
            
        try:
            # First wait for the dropdown to be attached to the DOM
            dropdown = page.wait_for_selector(selector, state="attached", timeout=self.default_timeout)
            if not dropdown:
                return {"action": "select_option", "success": False, "message": f"Dropdown not found: {selector}"}
            
            # Make sure dropdown is visible and enabled
            is_enabled = page.evaluate("""
                (element) => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                        style.visibility !== 'hidden' && 
                        !element.disabled;
                }
            """, dropdown)
            
            if not is_enabled:
                return {"action": "select_option", "success": False, "message": f"Dropdown is not enabled: {selector}"}
            
            # Scroll to the dropdown
            dropdown.scroll_into_view_if_needed()
            
            # Check if it's a native select element or a custom dropdown
            is_select = page.evaluate("(el) => el.tagName.toLowerCase() === 'select'", dropdown)
            
            if is_select:
                # For native select elements, use select_option
                dropdown.select_option(value=value)
            else:
                # For custom dropdowns, first click to open it
                dropdown.click()
                time.sleep(0.5)  # Wait for dropdown to open
                
                # Try to find the option by text
                option_selector = f"{selector} option, {selector} li, [role='option']"
                option = page.wait_for_selector(f"{option_selector}:has-text('{value}')", timeout=5000)
                
                if not option:
                    # Try fuzzy matching options
                    options = page.query_selector_all(option_selector)
                    best_match = None
                    best_score = 0
                    
                    for opt in options:
                        opt_text = opt.inner_text().strip()
                        score = difflib.SequenceMatcher(None, opt_text.lower(), value.lower()).ratio()
                        if score > best_score:
                            best_score = score
                            best_match = opt
                    
                    if best_match and best_score > 0.7:  # Use a threshold for fuzzy matching
                        option = best_match
                    else:
                        # If still not found, try using JavaScript to find it
                        option_element = page.evaluate(f"""
                            () => {{
                                const options = document.querySelectorAll("{option_selector}");
                                for (const opt of options) {{
                                    if (opt.innerText.toLowerCase().includes("{value.lower()}")) {{
                                        return opt;
                                    }}
                                }}
                                return null;
                            }}
                        """)
                        
                        if option_element:
                            # Click the option using JavaScript
                            page.evaluate("(el) => el.click()", option_element)
                            return {"action": "select_option", "success": True, "message": f"Selected option '{value}' using JavaScript"}
                        
                        return {"action": "select_option", "success": False, "message": f"Option '{value}' not found in dropdown"}
                
                # Click the option
                option.click()
            
            return {"action": "select_option", "success": True, "message": f"Selected option '{value}' from dropdown"}
        except Exception as e:
            self.logger.error(f"Select option action failed for selector {selector}: {e}")
            return {"action": "select_option", "success": False, "message": f"Select option failed: {str(e)}"}

    def _handle_checkbox(self, page: Page, selector: str, check: bool) -> Dict[str, Any]:
        """Handle checking or unchecking a checkbox"""
        if isinstance(selector, dict):
            selector = selector.get("selector", "")
            
        action = "check" if check else "uncheck"
        
        try:
            # Wait for the checkbox to be attached to the DOM
            checkbox = page.wait_for_selector(selector, state="attached", timeout=self.default_timeout)
            if not checkbox:
                return {"action": action, "success": False, "message": f"Checkbox not found: {selector}"}
            
            # Make sure checkbox is visible and enabled
            is_enabled = page.evaluate("""
                (element) => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                        style.visibility !== 'hidden' && 
                        !element.disabled;
                }
            """, checkbox)
            
            if not is_enabled:
                return {"action": action, "success": False, "message": f"Checkbox is not enabled: {selector}"}
            
            # Scroll to the checkbox
            checkbox.scroll_into_view_if_needed()
            
            # Get current state of the checkbox
            is_checked = page.evaluate("(el) => el.checked", checkbox)
            
            # Only change state if needed
            if (check and not is_checked) or (not check and is_checked):
                checkbox.click()
                
                # Verify the action was successful
                time.sleep(0.2)  # Short wait for state to update
                new_state = page.evaluate("(el) => el.checked", checkbox)
                
                if new_state == check:
                    return {"action": action, "success": True, "message": f"Successfully {'checked' if check else 'unchecked'} checkbox"}
                else:
                    # Try an alternative approach with JavaScript
                    page.evaluate(f"(el) => el.checked = {str(check).lower()}", checkbox)
                    return {"action": action, "success": True, "message": f"{'Checked' if check else 'Unchecked'} checkbox using JavaScript"}
            else:
                # Checkbox was already in the desired state
                return {"action": action, "success": True, "message": f"Checkbox was already {'checked' if check else 'unchecked'}"}
        except Exception as e:
            self.logger.error(f"{action.capitalize()} action failed for selector {selector}: {e}")
            return {"action": action, "success": False, "message": f"{action.capitalize()} failed: {str(e)}"}

    def _handle_press_key(self, page: Page, key: str) -> Dict[str, Any]:
        """Handle pressing a keyboard key"""
        if isinstance(key, dict):
            key = key.get("value", "")
            
        try:
            # Map some common key names to Playwright's key names
            key_map = {
                "enter": "Enter",
                "return": "Enter",
                "tab": "Tab",
                "escape": "Escape",
                "esc": "Escape",
                "arrowup": "ArrowUp",
                "arrowdown": "ArrowDown",
                "arrowleft": "ArrowLeft",
                "arrowright": "ArrowRight",
                "backspace": "Backspace",
                "delete": "Delete",
                "space": " "
            }
            
            # Normalize key name
            normalized_key = key_map.get(key.lower(), key)
            
            # Special handling for key combinations (e.g., "Control+A")
            if "+" in normalized_key:
                key_parts = normalized_key.split("+")
                modifiers = key_parts[:-1]
                key_to_press = key_parts[-1]
                
                # Press the key with modifiers
                for modifier in modifiers:
                    page.keyboard.down(modifier)
                page.keyboard.press(key_to_press)
                for modifier in modifiers:
                    page.keyboard.up(modifier)
            else:
                # Press a single key
                page.keyboard.press(normalized_key)
                
            return {"action": "press_key", "success": True, "message": f"Pressed key: {key}"}
        except Exception as e:
            self.logger.error(f"Press key action failed for key {key}: {e}")
            return {"action": "press_key", "success": False, "message": f"Press key failed: {str(e)}"}

    def _handle_file_upload(self, page: Page, selector: str, file_path: str) -> Dict[str, Any]:
        """Handle file upload operation"""
        if isinstance(selector, dict):
            selector = selector.get("selector", "")
            
        if isinstance(file_path, dict):
            file_path = file_path.get("value", "")
            
        try:
            # Ensure the file exists
            if not os.path.exists(file_path):
                return {"action": "file_upload", "success": False, "message": f"File not found: {file_path}"}
            
            # Wait for the file input element to be attached to the DOM
            file_input = page.wait_for_selector(selector, state="attached", timeout=self.default_timeout)
            if not file_input:
                return {"action": "file_upload", "success": False, "message": f"File input not found: {selector}"}
            
            # Some file inputs might be hidden by CSS, so we don't check visibility
            
            # Set the file
            file_input.set_input_files(file_path)
            
            # Wait a moment for any upload processing to start
            time.sleep(0.5)
            
            return {"action": "file_upload", "success": True, "message": f"Uploaded file: {file_path}"}
        except Exception as e:
            self.logger.error(f"File upload action failed for selector {selector}: {e}")
            return {"action": "file_upload", "success": False, "message": f"File upload failed: {str(e)}"}

    def _handle_verify_text(self, page: Page, text: str) -> Dict[str, Any]:
        """Verify that specific text appears on the page"""
        if isinstance(text, dict):
            text = text.get("value", "")
            
        try:
            # Search for the text in the page content
            try:
                # First try the Playwright built-in text search
                element = page.wait_for_selector(f"text='{text}'", timeout=5000)
                if element:
                    return {"action": "verify_text", "success": True, "message": f"Text '{text}' found on page"}
            except Exception:
                # If Playwright search fails, try JavaScript
                found = page.evaluate(f"""
                    () => {{
                        const pageText = document.body.innerText;
                        return pageText.includes("{text}");
                    }}
                """)
                
                if found:
                    return {"action": "verify_text", "success": True, "message": f"Text '{text}' found on page using JavaScript"}
                else:
                    # Try one more approach with fuzzy matching
                    highest_match = page.evaluate(f"""
                        () => {{
                            const targetText = "{text}".toLowerCase();
                            const allTextElements = Array.from(document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div, a, button, li'));
                            let highestSimilarity = 0;
                            let bestMatchText = '';
                            
                            for (const el of allTextElements) {{
                                const currentText = el.innerText.toLowerCase();
                                if (!currentText) continue;
                                
                                // Simple similarity check
                                for (let i = 0; i < targetText.length - 2; i++) {{
                                    const chunk = targetText.substring(i, i+3);
                                    if (currentText.includes(chunk)) {{
                                        const similarity = chunk.length / targetText.length;
                                        if (similarity > highestSimilarity) {{
                                            highestSimilarity = similarity;
                                            bestMatchText = el.innerText;
                                        }}
                                    }}
                                }}
                            }}
                            
                            return {{ similarity: highestSimilarity, text: bestMatchText }};
                        }}
                    """)
                    
                    if highest_match.get("similarity", 0) > 0.7:  # Threshold for similarity
                        return {"action": "verify_text", "success": True, 
                                "message": f"Text similar to '{text}' found: '{highest_match.get('text')}'"}
                    
                    return {"action": "verify_text", "success": False, "message": f"Text '{text}' not found on page"}
        except Exception as e:
            self.logger.error(f"Verify text action failed for text {text}: {e}")
            return {"action": "verify_text", "success": False, "message": f"Verify text failed: {str(e)}"}

    def _handle_verify_element(self, page: Page, selector: str) -> Dict[str, Any]:
        """Verify that a specific element exists on the page"""
        if isinstance(selector, dict):
            selector = selector.get("selector", "")
            
        try:
            # Try to find the element
            element = page.wait_for_selector(selector, state="attached", timeout=5000)
            if element:
                # Also check if the element is visible
                is_visible = page.evaluate("""
                    (element) => {
                        const rect = element.getBoundingClientRect();
                        const style = window.getComputedStyle(element);
                        return rect.width > 0 && rect.height > 0 && 
                            style.display !== 'none' && 
                            style.visibility !== 'hidden' &&
                            style.opacity !== '0';
                    }
                """, element)
                
                if is_visible:
                    return {"action": "verify_element", "success": True, "message": f"Element '{selector}' found and visible"}
                else:
                    return {"action": "verify_element", "success": True, "message": f"Element '{selector}' found but not visible"}
            else:
                return {"action": "verify_element", "success": False, "message": f"Element '{selector}' not found"}
        except Exception as e:
            self.logger.error(f"Verify element action failed for selector {selector}: {e}")
            return {"action": "verify_element", "success": False, "message": f"Verify element failed: {str(e)}"}

    def _handle_dialog(self, page: Page, action: str) -> Dict[str, Any]:
        """Handle JavaScript dialogs (alert, confirm, prompt)"""
        if isinstance(action, dict):
            action = action.get("value", "accept")
            
        try:
            # Set up a dialog handler
            dialog_result = {"handled": False, "message": ""}
            
            def dialog_handler(dialog):
                dialog_text = dialog.message
                dialog_result["message"] = dialog_text
                
                if action.lower() == "accept":
                    dialog.accept()
                elif action.lower() == "dismiss":
                    dialog.dismiss()
                elif action.lower().startswith("text:"):
                    # For prompts, enter text and accept
                    text_to_enter = action[5:]  # Remove "text:" prefix
                    dialog.accept(text_to_enter)
                else:
                    # Default to accept
                    dialog.accept()
                    
                dialog_result["handled"] = True
            
            # Register the handler
            page.once("dialog", dialog_handler)
            
            # Return success immediately - the handler will be called when a dialog appears
            return {"action": "handle_dialog", "success": True, "message": f"Dialog handler set to '{action}'"}
        except Exception as e:
            self.logger.error(f"Set dialog handler failed: {e}")
            return {"action": "handle_dialog", "success": False, "message": f"Set dialog handler failed: {str(e)}"}

    def _handle_switch_frame(self, page: Page, selector: str) -> Dict[str, Any]:
        """Switch to an iframe for subsequent actions"""
        if isinstance(selector, dict):
            selector = selector.get("selector", "")
            
        try:
            # Special case for main frame
            if selector.lower() in ["main", "top", "parent", "default"]:
                page.frame_locator("body").first.wait_for(timeout=1000)  # Just to confirm we're in the main frame
                return {"action": "switch_frame", "success": True, "message": "Switched to main frame"}
            
            # Wait for the iframe to be attached to the DOM
            iframe = page.wait_for_selector(selector, state="attached", timeout=self.default_timeout)
            if not iframe:
                return {"action": "switch_frame", "success": False, "message": f"Iframe not found: {selector}"}
            
            # Create a frame locator
            frame_locator = page.frame_locator(selector)
            
            # Wait for the frame to load by checking for body
            frame_locator.locator("body").wait_for(timeout=5000)
            
            # Store the current frame locator for future actions
            self._current_frame = frame_locator
            
            return {"action": "switch_frame", "success": True, "message": f"Switched to iframe: {selector}"}
        except Exception as e:
            self.logger.error(f"Switch frame action failed for selector {selector}: {e}")
            return {"action": "switch_frame", "success": False, "message": f"Switch frame failed: {str(e)}"}

    def _handle_retry_with_delay(self, page: Page, options: str) -> Dict[str, Any]:
        """Handle retrying a flaky action with delay"""
        if isinstance(options, dict):
            retry_params = options
        else:
            # Parse options string (format: "action:selector:value:delay:max_retries")
            try:
                parts = options.split(":")
                if len(parts) >= 3:
                    retry_action = parts[0]
                    retry_selector = parts[1] if len(parts) > 1 else ""
                    retry_value = parts[2] if len(parts) > 2 else ""
                    retry_delay = float(parts[3]) if len(parts) > 3 else 1.0
                    retry_max = int(parts[4]) if len(parts) > 4 else 3
                    
                    retry_params = {
                        "action": retry_action,
                        "selector": retry_selector,
                        "value": retry_value,
                        "delay": retry_delay,
                        "max_retries": retry_max
                    }
                else:
                    return {"action": "retry_with_delay", "success": False, 
                            "message": "Invalid retry format. Expected: action:selector:value:delay:max_retries"}
            except Exception as e:
                return {"action": "retry_with_delay", "success": False, 
                        "message": f"Failed to parse retry parameters: {str(e)}"}
        
        # Execute the action with retries
        action_name = retry_params.get("action", "")
        handler = {
            "click": self._handle_click,
            "type": lambda p, s, v, t: self._handle_typing(p, s, v, t),
            "wait_for_selector": lambda p, s, v: self._handle_wait_for_selector(p, s, v),
            "navigate": self._handle_navigation,
            "select_option": lambda p, s, v: self._handle_select_option(p, s, v)
        }.get(action_name)
        
        if not handler:
            return {"action": "retry_with_delay", "success": False, 
                    "message": f"Unsupported action for retry: {action_name}"}
        
        # Prepare task for retry
        task = {
            "action": action_name,
            "selector": retry_params.get("selector", ""),
            "value": retry_params.get("value", "")
        }
        
        # Execute retries
        delay = retry_params.get("delay", 1.0)
        max_retries = retry_params.get("max_retries", 3)
        
        for attempt in range(max_retries):
            if action_name == "type":
                result = handler(page, task.get("selector"), task.get("value"), task)
            elif action_name == "wait_for_selector":
                result = handler(page, task.get("selector"), "5000")  # 5 second timeout
            else:
                result = handler(page, task)
                
            if result.get("success", False):
                result["message"] = f"Retry succeeded on attempt {attempt + 1}: {result.get('message', '')}"
                return result
                
            if attempt < max_retries - 1:
                self.logger.info(f"Retry attempt {attempt + 1} failed, waiting {delay}s before next attempt")
                time.sleep(delay)
        
        return {"action": "retry_with_delay", "success": False, 
                "message": f"All {max_retries} retry attempts failed for {action_name}"}

    def _handle_refresh(self, page: Page) -> Dict[str, Any]:
        """Refresh the current page"""
        try:
            page.reload(timeout=self.default_timeout)
            
            # Wait for the page to stabilize
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                # It's okay if this times out
                pass
                
            return {"action": "refresh", "success": True, "message": "Page refreshed successfully"}
        except Exception as e:
            self.logger.error(f"Refresh action failed: {e}")
            return {"action": "refresh", "success": False, "message": f"Refresh failed: {str(e)}"}

    def _handle_back(self, page: Page) -> Dict[str, Any]:
        """Navigate back in browser history"""
        try:
            page.go_back(timeout=self.default_timeout)
            
            # Wait for the page to stabilize
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                # It's okay if this times out
                pass
                
            return {"action": "back", "success": True, "message": "Navigated back successfully"}
        except Exception as e:
            self.logger.error(f"Back navigation failed: {e}")
            return {"action": "back", "success": False, "message": f"Back navigation failed: {str(e)}"}

    def _handle_forward(self, page: Page) -> Dict[str, Any]:
        """Navigate forward in browser history"""
        try:
            page.go_forward(timeout=self.default_timeout)
            
            # Wait for the page to stabilize
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                # It's okay if this times out
                pass
                
            return {"action": "forward", "success": True, "message": "Navigated forward successfully"}
        except Exception as e:
            self.logger.error(f"Forward navigation failed: {e}")
            return {"action": "forward", "success": False, "message": f"Forward navigation failed: {str(e)}"}

    def _handle_close_tab(self, page: Page) -> Dict[str, Any]:
        """Close the current tab"""
        try:
            # Get total number of pages (tabs)
            pages = self.browser_context.pages
            
            if len(pages) <= 1:
                return {"action": "close_tab", "success": False, "message": "Cannot close the last tab"}
            
            # Identify current page index
            current_index = pages.index(page)
            
            # Close the current page
            page.close()
            
            # Switch to another tab (previous one or first available)
            new_index = max(0, current_index - 1)
            self.page = pages[new_index] if new_index < len(pages) else pages[0]
            
            return {"action": "close_tab", "success": True, "message": "Tab closed successfully"}
        except Exception as e:
            self.logger.error(f"Close tab action failed: {e}")
            return {"action": "close_tab", "success": False, "message": f"Close tab failed: {str(e)}"}

    def _handle_switch_tab(self, context: BrowserContext, index_or_new: str) -> Dict[str, Any]:
        """Switch to a different browser tab or open a new one"""
        if isinstance(index_or_new, dict):
            index_or_new = index_or_new.get("value", "0")
            
        try:
            # Get all pages (tabs)
            pages = context.pages
            
            if index_or_new.lower() == "new":
                # Open a new tab
                new_page = context.new_page()
                self.page = new_page
                return {"action": "switch_tab", "success": True, "message": "Opened and switched to new tab"}
            else:
                try:
                    # Try to convert to integer index
                    idx = int(index_or_new)
                    
                    if idx < 0 or idx >= len(pages):
                        return {"action": "switch_tab", "success": False, "message": f"Tab index {idx} out of range (0-{len(pages)-1})"}
                        
                    self.page = pages[idx]
                    return {"action": "switch_tab", "success": True, "message": f"Switched to tab {idx}"}
                except ValueError:
                    # It's not an integer, try to match by title or URL
                    target = index_or_new.lower()
                    
                    for idx, p in enumerate(pages):
                        # Check page title and URL
                        title = p.title().lower()
                        url = p.url.lower()
                        
                        if target in title or target in url:
                            self.page = p
                            return {"action": "switch_tab", "success": True, 
                                    "message": f"Switched to tab with matching title/URL: {index_or_new}"}
                    
                    return {"action": "switch_tab", "success": False, 
                            "message": f"No tab found matching: {index_or_new}"}
        except Exception as e:
            self.logger.error(f"Switch tab action failed: {e}")
            return {"action": "switch_tab", "success": False, "message": f"Switch tab failed: {str(e)}"}

    def _handle_execute_script(self, page: Page, script: str) -> Dict[str, Any]:
        """Execute JavaScript code on the page"""
        if isinstance(script, dict):
            script = script.get("value", "")
            
        try:
            # Safety check for script
            if not script.strip():
                return {"action": "execute_script", "success": False, "message": "Empty script provided"}
                
            # Execute the script
            result = page.evaluate(script)
            
            # Format result for return
            if result is None:
                result_str = "null"
            elif isinstance(result, (dict, list)):
                result_str = json.dumps(result, default=str)
            else:
                result_str = str(result)
                
            # Truncate very long results
            if len(result_str) > 1000:
                result_str = result_str[:997] + "..."
                
            return {"action": "execute_script", "success": True, 
                    "message": f"Script executed successfully. Result: {result_str}"}
        except Exception as e:
            self.logger.error(f"Execute script action failed: {e}")
            return {"action": "execute_script", "success": False, "message": f"Execute script failed: {str(e)}"}
    def _handle_drag_and_drop(self, page: Page, source_selector: str, target_selector: str) -> Dict[str, Any]:
        """Perform drag and drop operation with multiple fallback mechanisms"""
        if isinstance(source_selector, dict):
            source_selector = source_selector.get("selector", "")
            
        if isinstance(target_selector, dict):
            target_selector = target_selector.get("value", "")
            
        try:
            # Wait for source and target elements
            source = page.wait_for_selector(source_selector, state="visible", timeout=self.default_timeout)
            if not source:
                return {"action": "drag_and_drop", "success": False, "message": f"Source element not found: {source_selector}"}
                
            target = page.wait_for_selector(target_selector, state="visible", timeout=self.default_timeout)
            if not target:
                return {"action": "drag_and_drop", "success": False, "message": f"Target element not found: {target_selector}"}
                
            # Get source element position
            source_box = source.bounding_box()
            if not source_box:
                return {"action": "drag_and_drop", "success": False, "message": "Source element has no position"}
                
            # Get target element position
            target_box = target.bounding_box()
            if not target_box:
                return {"action": "drag_and_drop", "success": False, "message": "Target element has no position"}
                
            # Calculate source center
            source_x = source_box["x"] + source_box["width"] / 2
            source_y = source_box["y"] + source_box["height"] / 2
            
            # Calculate target center
            target_x = target_box["x"] + target_box["width"] / 2
            target_y = target_box["y"] + target_box["height"] / 2
            
            # Approach 1: Try using Playwright's drag_to method first (most reliable)
            try:
                source.drag_to(target)
                # Verify the drag was successful by checking for changes
                time.sleep(0.5)  # Allow time for any UI updates
                
                # Check if any element has changed position by comparing page states
                if self._previous_states and len(self._previous_states) > 1:
                    previous_state = self._previous_states[-1]
                    current_state = self._capture_page_state_snapshot()
                    if self._detect_state_changes(previous_state, current_state):
                        return {"action": "drag_and_drop", "success": True, 
                                "message": f"Dragged element from {source_selector} to {target_selector} using drag_to"}
                else:
                    # If we can't verify with states, assume success for now
                    return {"action": "drag_and_drop", "success": True, 
                            "message": f"Dragged element from {source_selector} to {target_selector} using drag_to"}
            except Exception as e:
                self.logger.warning(f"First drag method failed: {e}. Trying alternative methods...")
            
            # Approach 2: Perform drag using mouse actions with small steps
            try:
                page.mouse.move(source_x, source_y)
                page.mouse.down()
                
                # Move in small steps for more reliable drag
                steps = 10
                for i in range(1, steps + 1):
                    curr_x = source_x + (target_x - source_x) * (i / steps)
                    curr_y = source_y + (target_y - source_y) * (i / steps)
                    page.mouse.move(curr_x, curr_y)
                    time.sleep(0.05)  # Small delay between moves
                    
                page.mouse.up()
                time.sleep(0.5)  # Allow time for any UI updates
                
                # Check if any element has changed position
                if self._previous_states and len(self._previous_states) > 1:
                    previous_state = self._previous_states[-1]
                    current_state = self._capture_page_state_snapshot()
                    if self._detect_state_changes(previous_state, current_state):
                        return {"action": "drag_and_drop", "success": True, 
                                "message": f"Dragged element from {source_selector} to {target_selector} using mouse actions"}
                else:
                    # If we can't verify with states, assume success for now
                    return {"action": "drag_and_drop", "success": True, 
                            "message": f"Dragged element from {source_selector} to {target_selector} using mouse actions"}
            except Exception as e:
                self.logger.warning(f"Second drag method failed: {e}. Trying JavaScript approach...")
            
            # Approach 3: JavaScript-based drag and drop for cases where the above methods fail
            js_result = page.evaluate(f"""
                (() => {{
                    try {{
                        const source = document.querySelector('{source_selector}');
                        const target = document.querySelector('{target_selector}');
                        
                        if (!source || !target) return false;
                        
                        // Create a custom dragstart event
                        const dragStartEvent = new MouseEvent('dragstart', {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        
                        // Create dataTransfer object
                        Object.defineProperty(dragStartEvent, 'dataTransfer', {{
                            value: new DataTransfer(),
                        }});
                        
                        // Dispatch dragstart
                        source.dispatchEvent(dragStartEvent);
                        
                        // Create and dispatch dragover event on target
                        const dragOverEvent = new MouseEvent('dragover', {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        
                        Object.defineProperty(dragOverEvent, 'dataTransfer', {{
                            value: dragStartEvent.dataTransfer,
                        }});
                        
                        target.dispatchEvent(dragOverEvent);
                        
                        // Create and dispatch drop event on target
                        const dropEvent = new MouseEvent('drop', {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        
                        Object.defineProperty(dropEvent, 'dataTransfer', {{
                            value: dragStartEvent.dataTransfer,
                        }});
                        
                        target.dispatchEvent(dropEvent);
                        
                        // Dispatch dragend on source
                        const dragEndEvent = new MouseEvent('dragend', {{
                            bubbles: true,
                            cancelable: true,
                            view: window
                        }});
                        
                        Object.defineProperty(dragEndEvent, 'dataTransfer', {{
                            value: dragStartEvent.dataTransfer,
                        }});
                        
                        source.dispatchEvent(dragEndEvent);
                        
                        return true;
                    }} catch (e) {{
                        console.error('JavaScript drag and drop failed:', e);
                        return false;
                    }}
                }})();
            """)
            
            if js_result:
                return {"action": "drag_and_drop", "success": True, 
                        "message": f"Dragged element from {source_selector} to {target_selector} using JavaScript events"}
                        
            # Approach 4: HTML5 Drag and Drop API
            js_result = page.evaluate(f"""
                (() => {{
                    try {{
                        const source = document.querySelector('{source_selector}');
                        const target = document.querySelector('{target_selector}');
                        
                        if (!source || !target) return false;
                        
                        // Simulate dragging programmatically using the HTML5 Drag and Drop API
                        const rect = target.getBoundingClientRect();
                        const x = rect.left + (rect.width / 2);
                        const y = rect.top + (rect.height / 2);
                        
                        // Set draggable attribute temporarily if needed
                        const wasDraggable = source.getAttribute('draggable');
                        if (!wasDraggable) source.setAttribute('draggable', 'true');
                        
                        // Trigger dragstart
                        const dragStart = new DragEvent('dragstart', {{
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        }});
                        
                        // We need to create a dataTransfer object
                        Object.defineProperty(dragStart, 'dataTransfer', {{
                            value: new DataTransfer()
                        }});
                        
                        source.dispatchEvent(dragStart);
                        
                        // Perform the drop on the target
                        const drop = new DragEvent('drop', {{
                            bubbles: true,
                            cancelable: true,
                            clientX: x,
                            clientY: y
                        }});
                        
                        Object.defineProperty(drop, 'dataTransfer', {{
                            value: dragStart.dataTransfer
                        }});
                        
                        target.dispatchEvent(drop);
                        
                        // Clean up
                        if (!wasDraggable) source.removeAttribute('draggable');
                        
                        return true;
                    }} catch (e) {{
                        console.error('HTML5 Drag and Drop failed:', e);
                        return false;
                    }}
                }})();
            """)
            
            if js_result:
                return {"action": "drag_and_drop", "success": True, 
                        "message": f"Dragged element from {source_selector} to {target_selector} using HTML5 Drag and Drop API"}
                        
            # If all approaches failed
            return {"action": "drag_and_drop", "success": False, 
                    "message": f"All drag and drop methods failed for {source_selector} to {target_selector}"}
                    
        except Exception as e:
            self.logger.error(f"Drag and drop action failed: {e}")
            return {"action": "drag_and_drop", "success": False, "message": f"Drag and drop failed: {str(e)}"}

    def _capture_page_state_snapshot(self) -> Dict[str, Any]:
        """Capture the current state of the page for comparison without storing in history"""
        try:
            # Capture visible elements with attributes for comparison
            elements = self.page.evaluate("""
                () => {
                    const visibleElements = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"], div, img'))
                        .filter(el => {
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0 && 
                                window.getComputedStyle(el).display !== 'none' &&
                                window.getComputedStyle(el).visibility !== 'hidden';
                        });
                    
                    return visibleElements.map(el => {
                        return {
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            classList: Array.from(el.classList),
                            text: el.innerText,
                            attributes: {
                                type: el.getAttribute('type'),
                                name: el.getAttribute('name'),
                                placeholder: el.getAttribute('placeholder'),
                                'aria-label': el.getAttribute('aria-label'),
                                role: el.getAttribute('role'),
                                title: el.getAttribute('title')
                            },
                            position: el.getBoundingClientRect()
                        };
                    });
                }
            """)
            
            return {
                "url": self.page.url,
                "elements": elements,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.warning(f"Failed to capture page state snapshot: {e}")
            return {}

    def _detect_state_changes(self, previous_state: Dict[str, Any], current_state: Dict[str, Any]) -> bool:
        """Detect changes between two page states to verify if an action had an effect"""
        try:
            if not previous_state or not current_state:
                return False
                
            # Check URL changes
            if previous_state.get("url") != current_state.get("url"):
                return True
                
            prev_elements = previous_state.get("elements", [])
            curr_elements = current_state.get("elements", [])
            
            # Check for changes in element count
            if len(prev_elements) != len(curr_elements):
                return True
                
            # Check for position changes of elements with the same ID or class
            for prev_el in prev_elements:
                prev_id = prev_el.get("id")
                prev_classes = prev_el.get("classList", [])
                
                # Find matching element in current state
                for curr_el in curr_elements:
                    curr_id = curr_el.get("id")
                    curr_classes = curr_el.get("classList", [])
                    
                    # Match by ID if available
                    if prev_id and curr_id and prev_id == curr_id:
                        # Compare positions
                        prev_pos = prev_el.get("position", {})
                        curr_pos = curr_el.get("position", {})
                        
                        # Check if position has changed significantly
                        if (abs(prev_pos.get("x", 0) - curr_pos.get("x", 0)) > 5 or 
                            abs(prev_pos.get("y", 0) - curr_pos.get("y", 0)) > 5):
                            return True
                    # Match by class combination if ID not available
                    elif not prev_id and not curr_id and prev_classes and curr_classes:
                        if set(prev_classes) == set(curr_classes):
                            # Compare positions
                            prev_pos = prev_el.get("position", {})
                            curr_pos = curr_el.get("position", {})
                            
                            # Check if position has changed significantly
                            if (abs(prev_pos.get("x", 0) - curr_pos.get("x", 0)) > 5 or 
                                abs(prev_pos.get("y", 0) - curr_pos.get("y", 0)) > 5):
                                return True
            
            return False
        except Exception as e:
            self.logger.warning(f"Failed to detect state changes: {e}")
            return False

    def _handle_shadow_dom(self, page: Page, selector: str, action: str, value: str = "") -> Dict[str, Any]:
        """Handle interactions with elements inside Shadow DOM"""
        try:
            # Parse the shadow DOM path (format: "host1 => shadowSelector1 => host2 => shadowSelector2")
            shadow_path = selector.split(" => ")
            if len(shadow_path) < 2:
                return {"action": action, "success": False, 
                        "message": "Invalid shadow DOM selector format. Use 'host => shadowSelector'"}
                        
            # Find the root host element
            host = page.wait_for_selector(shadow_path[0], state="attached", timeout=self.default_timeout)
            if not host:
                return {"action": action, "success": False, 
                        "message": f"Shadow host element not found: {shadow_path[0]}"}
                        
            # Navigate through the shadow DOM using JavaScript
            js_shadow_query = """
                (host, path) => {
                    let element = host;
                    
                    // Skip the first item (host), start from index 1
                    for (let i = 1; i < path.length; i++) {
                        if (!element) return null;
                        
                        // If this is a shadow host, get its shadow root
                        if (i % 2 === 1) {
                            element = element.shadowRoot;
                            if (!element) return null;
                        }
                        // Otherwise use querySelector on the current element
                        else {
                            element = element.querySelector(path[i]);
                            if (!element) return null;
                        }
                    }
                    
                    return element;
                }
            """
            
            shadow_element = page.evaluate(js_shadow_query, host, shadow_path)
            if not shadow_element:
                return {"action": action, "success": False, 
                        "message": f"Element not found in shadow DOM: {selector}"}
                        
            # Perform the requested action
            if action == "click":
                page.evaluate("(el) => el.click()", shadow_element)
                return {"action": "click", "success": True, 
                        "message": f"Clicked element in shadow DOM: {selector}"}
                        
            elif action == "type":
                page.evaluate(f"(el) => {{ el.value = ''; el.value = '{value}'; }}", shadow_element)
                # Trigger input event
                page.evaluate("(el) => el.dispatchEvent(new Event('input', {bubbles: true}))", shadow_element)
                # Trigger change event
                page.evaluate("(el) => el.dispatchEvent(new Event('change', {bubbles: true}))", shadow_element)
                
                return {"action": "type", "success": True, 
                        "message": f"Typed '{value}' into element in shadow DOM: {selector}"}
                        
            elif action == "select_option":
                # Find the option by value or text
                js_select_option = f"""
                    (el, value) => {{
                        if (el.tagName.toLowerCase() !== 'select') return false;
                        
                        // Try to find option by value first
                        let option = Array.from(el.options).find(opt => opt.value === value);
                        
                        // If not found, try to find by text
                        if (!option) {{
                            option = Array.from(el.options).find(opt => opt.text === value);
                        }}
                        
                        if (option) {{
                            el.value = option.value;
                            el.dispatchEvent(new Event('change', {{bubbles: true}}));
                            return true;
                        }}
                        
                        return false;
                    }}
                """
                
                success = page.evaluate(js_select_option, shadow_element, value)
                if success:
                    return {"action": "select_option", "success": True, 
                            "message": f"Selected option '{value}' in shadow DOM: {selector}"}
                else:
                    return {"action": "select_option", "success": False, 
                            "message": f"Failed to select option '{value}' in shadow DOM"}
                            
            else:
                return {"action": action, "success": False, 
                        "message": f"Unsupported action for shadow DOM: {action}"}
                        
        except Exception as e:
            self.logger.error(f"Shadow DOM interaction failed: {e}")
            return {"action": action, "success": False, 
                    "message": f"Shadow DOM interaction failed: {str(e)}"}

    def _handle_react_component(self, page: Page, component_selector: str, action: str, props: Dict = None) -> Dict[str, Any]:
        """
        Handle interactions with React components by simulating events at the React component level
        """
        try:
            if not component_selector:
                return {"action": action, "success": False, "message": "No component selector provided"}
                
            # Find the React component DOM element
            component = page.wait_for_selector(component_selector, state="attached", timeout=self.default_timeout)
            if not component:
                return {"action": action, "success": False, 
                        "message": f"React component not found: {component_selector}"}
                        
            # Inject React DevTools-like helpers if not already injected
            react_helpers_injected = page.evaluate("""
                () => {
                    return !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
                }
            """)
            
            if not react_helpers_injected:
                page.evaluate("""
                    () => {
                        // Minimal React DevTools hook for component introspection
                        window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = {
                            _renderers: {},
                            helpers: {},
                            
                            // Store fiber nodes and their DOM nodes
                            _fibers: new Map(),
                            _domToFiber: new WeakMap(),
                            
                            // Register renderer (React will call this)
                            inject: function(renderer) {
                                const id = Object.keys(this._renderers).length + 1;
                                this._renderers[id] = renderer;
                                
                                // Patch the renderer to track fiber nodes
                                const originalMount = renderer.Mount;
                                if (originalMount) {
                                    renderer.Mount = (...args) => {
                                        const fiber = originalMount.apply(this, args);
                                        if (fiber && fiber.stateNode && fiber.stateNode.nodeType === 1) {
                                            this._fibers.set(fiber, true);
                                            this._domToFiber.set(fiber.stateNode, fiber);
                                        }
                                        return fiber;
                                    };
                                }
                                
                                return id;
                            },
                            
                            // Find React fiber from DOM node
                            getFiberForDOMNode: function(node) {
                                return this._domToFiber.get(node) || null;
                            },
                            
                            // Get component props
                            getProps: function(fiber) {
                                return fiber && fiber.memoizedProps ? {...fiber.memoizedProps} : null;
                            },
                            
                            // Set component props (simplified)
                            setProps: function(fiber, newProps) {
                                if (!fiber || !fiber.stateNode || typeof fiber.stateNode.setState !== 'function') {
                                    return false;
                                }
                                
                                try {
                                    // Apply new props by triggering a re-render
                                    fiber.pendingProps = {...fiber.pendingProps, ...newProps};
                                    fiber.stateNode.forceUpdate();
                                    return true;
                                } catch (e) {
                                    console.error('Error setting props:', e);
                                    return false;
                                }
                            }
                        };
                    }
                """)
                
            # Get the React fiber for the DOM element
            fiber_exists = page.evaluate("""
                (node) => {
                    if (!window.__REACT_DEVTOOLS_GLOBAL_HOOK__) return false;
                    const fiber = window.__REACT_DEVTOOLS_GLOBAL_HOOK__.getFiberForDOMNode(node);
                    return !!fiber;
                }
            """, component)
            
            if not fiber_exists:
                self.logger.warning("DOM element found but no React fiber attached")
                # Fall back to regular DOM interactions
                if action == "click":
                    component.click()
                    return {"action": "click", "success": True, 
                            "message": f"Clicked element (React component not detected): {component_selector}"}
                elif action == "type" and props and "value" in props:
                    component.fill(props["value"])
                    return {"action": "type", "success": True, 
                            "message": f"Typed into element (React component not detected): {component_selector}"}
                else:
                    return {"action": action, "success": False, 
                            "message": f"Unsupported action for non-React element: {action}"}
            
            # For React components, use props-based approach
            if props:
                success = page.evaluate("""
                    (node, newProps) => {
                        const hook = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
                        if (!hook) return false;
                        
                        const fiber = hook.getFiberForDOMNode(node);
                        if (!fiber) return false;
                        
                        return hook.setProps(fiber, newProps);
                    }
                """, component, props)
                
                if success:
                    return {"action": "update_props", "success": True, 
                            "message": f"Updated React component props for {component_selector}"}
                else:
                    # Fall back to DOM events
                    if action == "click":
                        component.click()
                        return {"action": "click", "success": True, 
                                "message": f"Clicked React component (props update failed): {component_selector}"}
                    elif action == "type" and "value" in props:
                        component.fill(props["value"])
                        return {"action": "type", "success": True, 
                                "message": f"Typed into React component (props update failed): {component_selector}"}
            
            # Default action if no props provided
            if action == "click":
                component.click()
                return {"action": "click", "success": True, 
                        "message": f"Clicked React component: {component_selector}"}
            elif action == "focus":
                component.focus()
                return {"action": "focus", "success": True, 
                        "message": f"Focused React component: {component_selector}"}
            else:
                return {"action": action, "success": False, 
                        "message": f"Unsupported action for React component: {action}"}
        
        except Exception as e:
            self.logger.error(f"React component interaction failed: {e}")
            return {"action": action, "success": False, 
                    "message": f"React component interaction failed: {str(e)}"}

    def _handle_captcha(self, page: Page, selector: str) -> Dict[str, Any]:
        """
        Handle common types of CAPTCHA challenges
        """
        try:
            # First, determine if there's a CAPTCHA on the page
            captcha_detected = page.evaluate("""
                () => {
                    // Check for reCAPTCHA
                    const recaptcha = document.querySelector('.g-recaptcha, iframe[src*="recaptcha"], iframe[src*="captcha"]');
                    if (recaptcha) return { type: 'recaptcha', element: recaptcha };
                    
                    // Check for hCaptcha
                    const hcaptcha = document.querySelector('iframe[src*="hcaptcha"]');
                    if (hcaptcha) return { type: 'hcaptcha', element: hcaptcha };
                    
                    // Check for image-based captchas
                    const imgCaptcha = document.querySelector('img[src*="captcha"]');
                    if (imgCaptcha) return { type: 'image', element: imgCaptcha };
                    
                    // Check for text-based captchas (common pattern: "Enter the characters you see")
                    const textInputs = Array.from(document.querySelectorAll('input[type="text"]'));
                    for (const input of textInputs) {
                        const nearbyText = input.closest('form')?.innerText.toLowerCase() || '';
                        if (nearbyText.includes('captcha') || 
                            nearbyText.includes('characters you see') || 
                            nearbyText.includes('security check')) {
                            return { type: 'text', element: input };
                        }
                    }
                    
                    return null;
                }
            """)
            
            if not captcha_detected:
                return {"action": "handle_captcha", "success": False, 
                        "message": "No CAPTCHA detected on the page"}
                        
            captcha_type = captcha_detected.get("type")
            
            if captcha_type == "recaptcha":
                # Try to handle reCAPTCHA
                # First, see if we can click the "I'm not a robot" checkbox
                checkbox_clicked = page.evaluate("""
                    () => {
                        const checkbox = document.querySelector('.recaptcha-checkbox');
                        if (checkbox) {
                            checkbox.click();
                            return true;
                        }
                        return false;
                    }
                """)
                
                if checkbox_clicked:
                    # Wait a moment to see if it gets approved automatically
                    time.sleep(2)
                    
                    # Check if the CAPTCHA was solved
                    solved = page.evaluate("""
                        () => {
                            const checkbox = document.querySelector('.recaptcha-checkbox');
                            return checkbox && checkbox.getAttribute('aria-checked') === 'true';
                        }
                    """)
                    
                    if solved:
                        return {"action": "handle_captcha", "success": True, 
                                "message": "reCAPTCHA checkbox clicked and solved automatically"}
                
                # If not solved automatically, notify the user that manual intervention is needed
                return {"action": "handle_captcha", "success": False, 
                        "message": "reCAPTCHA detected but requires manual intervention"}
                        
            elif captcha_type == "hcaptcha":
                # Similar approach for hCaptcha
                return {"action": "handle_captcha", "success": False, 
                        "message": "hCaptcha detected but requires manual intervention"}
                        
            elif captcha_type == "image":
                # Image-based CAPTCHA - take a screenshot and notify the user
                captcha_element = page.query_selector('img[src*="captcha"]')
                if captcha_element:
                    captcha_screenshot = captcha_element.screenshot()
                    # Save the screenshot for manual solving
                    with open("captcha.png", "wb") as f:
                        f.write(captcha_screenshot)
                        
                    return {"action": "handle_captcha", "success": False, 
                            "message": "Image CAPTCHA detected. Screenshot saved as 'captcha.png'. Manual solving required."}
                            
            elif captcha_type == "text":
                # Text-based CAPTCHA - these often have simpler challenges
                # Notify that manual intervention is needed
                return {"action": "handle_captcha", "success": False, 
                        "message": "Text-based CAPTCHA detected. Manual solving required."}
            
            return {"action": "handle_captcha", "success": False, 
                    "message": f"Unknown CAPTCHA type: {captcha_type}"}
                    
        except Exception as e:
            self.logger.error(f"CAPTCHA handling failed: {e}")
            return {"action": "handle_captcha", "success": False, 
                    "message": f"CAPTCHA handling failed: {str(e)}"}
    def _capture_failure_screenshot(self, page: Page, action: str):
        """Capture a screenshot when an action fails, with enhanced debugging info"""
        try:
            timestamp = int(time.time())
            filename = f"failure_{action}_{timestamp}.png"
            
            # Take a full page screenshot
            page.screenshot(path=filename, full_page=True)
            
            # Capture HTML source for debugging
            html_filename = f"failure_{action}_{timestamp}.html"
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(page.content())
                
            # Capture DOM structure and properties of key elements
            js_debug_info = page.evaluate("""
                () => {
                    function getElementInfo(element) {
                        if (!element) return null;
                        
                        const rect = element.getBoundingClientRect();
                        return {
                            tag: element.tagName,
                            id: element.id,
                            classList: Array.from(element.classList),
                            attributes: Array.from(element.attributes).map(attr => ({ name: attr.name, value: attr.value })),
                            isVisible: rect.width > 0 && rect.height > 0,
                            position: { x: rect.left, y: rect.top, width: rect.width, height: rect.height }
                        };
                    }
                    
                    return {
                        url: window.location.href,
                        title: document.title,
                        activeElement: getElementInfo(document.activeElement),
                        forms: Array.from(document.forms).map(form => ({
                            id: form.id,
                            name: form.name,
                            elements: Array.from(form.elements).map(getElementInfo)
                        })),
                        focusableElements: Array.from(document.querySelectorAll('button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])')).map(getElementInfo)
                    };
                }
            """)
            
            # Save the debug info to a JSON file
            debug_filename = f"failure_{action}_{timestamp}_debug.json"
            with open(debug_filename, "w", encoding="utf-8") as f:
                json.dump(js_debug_info, f, indent=2, default=str)
            
            self.logger.info(f"Failure captured: Screenshot at {filename}, HTML at {html_filename}, Debug info at {debug_filename}")
            
            # Add to failure log for pattern analysis
            self._record_failure(action, js_debug_info)
            
        except Exception as e:
            self.logger.error(f"Failed to capture failure evidence: {e}")

    def _record_failure(self, action: str, debug_info: Dict[str, Any]):
        """Record failure data for pattern analysis and automated learning"""
        try:
            failures_log = "browser_failures.json"
            
            # Load existing failures if file exists
            failures = []
            if os.path.exists(failures_log):
                try:
                    with open(failures_log, "r", encoding="utf-8") as f:
                        failures = json.load(f)
                except json.JSONDecodeError:
                    # File exists but isn't valid JSON, start fresh
                    failures = []
            
            # Add this failure
            failures.append({
                "action": action,
                "timestamp": time.time(),
                "url": debug_info.get("url", ""),
                "title": debug_info.get("title", ""),
                "browser_dimensions": {
                    "width": self.page.viewport_size()["width"] if self.page else None,
                    "height": self.page.viewport_size()["height"] if self.page else None
                },
                "debug_info": debug_info
            })
            
            # Save back to file (keep last 100 failures to avoid file growing too large)
            with open(failures_log, "w", encoding="utf-8") as f:
                json.dump(failures[-100:], f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to record failure: {e}")

    def _analyze_failures(self):
        """Analyze recorded failures to identify patterns and self-improve"""
        try:
            failures_log = "browser_failures.json"
            if not os.path.exists(failures_log):
                return
                
            with open(failures_log, "r", encoding="utf-8") as f:
                failures = json.load(f)
                
            if not failures:
                return
                
            # Group failures by action
            action_groups = {}
            for failure in failures:
                action = failure.get("action", "unknown")
                if action not in action_groups:
                    action_groups[action] = []
                action_groups[action].append(failure)
                
            # Analyze patterns for each action type
            for action, group in action_groups.items():
                if len(group) < 3:  # Need at least 3 examples to find patterns
                    continue
                    
                # Look for common URLs where failures happen
                urls = [f.get("url", "") for f in group]
                url_counter = {}
                for url in urls:
                    domain = re.search(r'https?://([^/]+)', url)
                    if domain:
                        domain = domain.group(1)
                        url_counter[domain] = url_counter.get(domain, 0) + 1
                        
                # Find domains with high failure rates
                problematic_domains = [domain for domain, count in url_counter.items() 
                                    if count >= len(group) * 0.3]  # 30% threshold
                                    
                # Look for common element patterns in failures
                selector_patterns = self._extract_selector_patterns(group)
                
                # Update automatic strategies based on findings
                if problematic_domains:
                    self.logger.info(f"Identified problematic domains for {action}: {problematic_domains}")
                    self._strategy_adjustments[action] = self._strategy_adjustments.get(action, {})
                    self._strategy_adjustments[action]["domains"] = problematic_domains
                    
                if selector_patterns:
                    self.logger.info(f"Identified selector patterns for {action}: {selector_patterns}")
                    self._strategy_adjustments[action] = self._strategy_adjustments.get(action, {})
                    self._strategy_adjustments[action]["selectors"] = selector_patterns
                    
        except Exception as e:
            self.logger.error(f"Failed to analyze failures: {e}")

    def _extract_selector_patterns(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from failed selectors to improve future attempts"""
        patterns = {}
        
        for failure in failures:
            debug_info = failure.get("debug_info", {})
            
            # Extract active element information
            active_element = debug_info.get("activeElement", {})
            if active_element:
                # Record tag frequencies
                tag = active_element.get("tag", "").lower()
                if tag:
                    patterns["tags"] = patterns.get("tags", {})
                    patterns["tags"][tag] = patterns["tags"].get(tag, 0) + 1
                    
                # Record class patterns
                classes = active_element.get("classList", [])
                for cls in classes:
                    patterns["classes"] = patterns.get("classes", {})
                    patterns["classes"][cls] = patterns["classes"].get(cls, 0) + 1
                    
                # Record attribute patterns
                attributes = active_element.get("attributes", [])
                for attr in attributes:
                    attr_name = attr.get("name", "")
                    if attr_name:
                        patterns["attributes"] = patterns.get("attributes", {})
                        patterns["attributes"][attr_name] = patterns["attributes"].get(attr_name, 0) + 1
        
        # Filter to keep only high-frequency patterns
        total = len(failures)
        threshold = max(2, total * 0.3)  # At least 30% occurrence or 2 occurrences
        
        for category in ["tags", "classes", "attributes"]:
            if category in patterns:
                patterns[category] = {k: v for k, v in patterns[category].items() if v >= threshold}
                
        return patterns

    def _adjust_strategy_for_site(self, url: str, action: str, selector: str) -> str:
        """Adjust element selection strategy based on learning from previous failures"""
        if not hasattr(self, "_strategy_adjustments"):
            self._strategy_adjustments = {}
            # Analyze past failures to initialize strategies
            self._analyze_failures()
            
        if action not in self._strategy_adjustments:
            return selector
            
        # Check if we're on a problematic domain
        domain_match = re.search(r'https?://([^/]+)', url)
        if not domain_match:
            return selector
            
        current_domain = domain_match.group(1)
        problematic_domains = self._strategy_adjustments[action].get("domains", [])
        
        if current_domain not in problematic_domains:
            return selector
            
        # Apply learned selector improvements
        selector_patterns = self._strategy_adjustments[action].get("selectors", {})
        
        # If we have tag patterns, prioritize those tags
        if "tags" in selector_patterns and selector_patterns["tags"]:
            common_tags = sorted(selector_patterns["tags"].items(), key=lambda x: x[1], reverse=True)
            if common_tags:
                # Create a more specific selector using the most common tags and attributes
                tag = common_tags[0][0]
                
                # Add common attributes if available
                attr_selectors = []
                if "attributes" in selector_patterns:
                    for attr_name, freq in selector_patterns["attributes"].items():
                        if attr_name in ["id", "class", "name", "type"]:
                            continue  # Handle these specially
                        attr_selectors.append(f"[{attr_name}]")
                
                # Add class selectors if available
                class_selectors = []
                if "classes" in selector_patterns:
                    for class_name, freq in selector_patterns["classes"].items():
                        class_selectors.append(f".{class_name}")
                
                # Combine selectors, but don't make it too specific
                max_selectors = 2  # Limit number of classes/attributes to avoid over-specificity
                combined_selector = tag + "".join(class_selectors[:max_selectors]) + "".join(attr_selectors[:max_selectors])
                
                # If original selector had :text() or [text=], preserve that
                text_match = re.search(r'(:text\([^)]+\)|\[text[~*^$]?=[^\]]+\])', selector)
                if text_match:
                    combined_selector += text_match.group(0)
                    
                self.logger.info(f"Adjusted selector strategy for {action} on {current_domain}: {combined_selector}")
                return combined_selector
                
        return selector

    def _create_fallback_selector_chain(self, selector: str) -> List[str]:
        """Create a chain of progressively less specific selectors to try"""
        selectors = [selector]
        
        # Step 1: If it has both ID and class, try just the ID
        id_match = re.search(r'#([a-zA-Z0-9_-]+)', selector)
        if id_match:
            selectors.append(f"#{id_match.group(1)}")
        
        # Step 2: If using attribute selectors, try with just the tag and primary attribute
        tag_attr_match = re.match(r'([a-z]+)(\[.+?\])+', selector)
        if tag_attr_match:
            tag = tag_attr_match.group(1)
            # Extract all attributes
            attr_matches = re.findall(r'\[([^\]=]+)(=|\*=|\^=|\$=|~=)[^\]]+\]', selector)
            if attr_matches:
                # Try with just the first attribute
                first_attr = attr_matches[0][0]
                first_op = attr_matches[0][1]
                first_val_match = re.search(rf'\[{first_attr}{first_op}([^\]]+)\]', selector)
                if first_val_match:
                    first_val = first_val_match.group(1)
                    selectors.append(f"{tag}[{first_attr}{first_op}{first_val}]")
        
        # Step 3: If using complex :has() selectors, try without them
        has_match = re.search(r'(.*?)(:has\([^)]+\))(.*)', selector)
        if has_match:
            selectors.append(has_match.group(1) + has_match.group(3))
        
        # Step 4: If text selector is used, try more relaxed text matching
        text_exact_match = re.search(r':text\("([^"]+)"\)', selector)
        if text_exact_match:
            text = text_exact_match.group(1)
            # Add a contains version
            selectors.append(selector.replace(f':text("{text}")', f':text-matches("{text}", "i")'))
        
        # Step 5: Generate completely different approaches
        # If using a complex selector, try a simple wildcard approach
        if len(selector) > 20 and not selector.startswith('#'):
            words = re.findall(r'[a-zA-Z0-9]{4,}', selector)
            for word in words:
                selectors.append(f"[id*='{word}' i]")
                selectors.append(f"[class*='{word}' i]")
                selectors.append(f"[name*='{word}' i]")
        
        return selectors

    def _detect_and_handle_spa_navigation(self, page: Page) -> bool:
        """
        Detect and handle Single Page Application (SPA) navigation which can be missed by standard navigation methods
        Returns True if SPA navigation was detected and handled
        """
        try:
            # Capture current URL and page state
            current_url = page.url
            
            # Monitor for URL changes that don't trigger full page navigation
            changed = page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        // Store initial URL
                        const initialUrl = window.location.href;
                        let navigationDetected = false;
                        
                        // Monitor URL changes
                        const urlObserver = () => {
                            if (window.location.href !== initialUrl) {
                                navigationDetected = true;
                                cleanup();
                                resolve(true);
                            }
                        };
                        
                        // Monitor DOM changes that might indicate SPA navigation
                        const domObserver = new MutationObserver((mutations) => {
                            const significantChanges = mutations.some(mutation => {
                                // Check for significant DOM changes that might indicate navigation
                                return mutation.addedNodes.length > 5 || 
                                    (mutation.target.nodeName === 'TITLE' && mutation.type === 'childList');
                            });
                            
                            if (significantChanges) {
                                cleanup();
                                resolve(true);
                            }
                        });
                        
                        // Start monitoring
                        domObserver.observe(document.body, { 
                            childList: true, 
                            subtree: true 
                        });
                        
                        // Check URL periodically
                        const intervalId = setInterval(urlObserver, 100);
                        
                        // Set timeout to resolve if nothing happens
                        const timeoutId = setTimeout(() => {
                            cleanup();
                            resolve(false);
                        }, 2000);
                        
                        // Cleanup function
                        function cleanup() {
                            clearInterval(intervalId);
                            clearTimeout(timeoutId);
                            domObserver.disconnect();
                        }
                    });
                }
            """)
            
            if changed:
                # Wait for network idle to ensure the page has settled
                try:
                    page.wait_for_load_state("networkidle", timeout=3000)
                except Exception:
                    # Continue even if timeout - the page might still be usable
                    pass
                    
                # Check if URL changed
                new_url = page.url
                if new_url != current_url:
                    self.logger.info(f"SPA navigation detected: {current_url} -> {new_url}")
                else:
                    self.logger.info("SPA content change detected without URL change")
                    
                # Check page title changes
                title = page.title()
                self.logger.info(f"Current page title: {title}")
                
                # Wait for any animations to complete
                time.sleep(0.5)
                
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting SPA navigation: {e}")
            return False

    def _extract_dynamic_validation_rules(self, page: Page, form_selector: str = "form") -> Dict[str, Any]:
        """Extract client-side validation rules from forms to ensure valid submissions"""
        try:
            validation_rules = page.evaluate(f"""
                (formSelector) => {{
                    const form = document.querySelector(formSelector);
                    if (!form) return null;
                    
                    const inputs = form.querySelectorAll('input, select, textarea');
                    const rules = {{}};
                    
                    for (const input of inputs) {{
                        const name = input.name || input.id;
                        if (!name) continue;
                        
                        rules[name] = {{
                            required: input.required,
                            type: input.type,
                            pattern: input.pattern || null,
                            minLength: input.minLength > 0 ? input.minLength : null,
                            maxLength: input.maxLength > 0 ? input.maxLength : null,
                            min: input.min || null,
                            max: input.max || null
                        }};
                        
                        // Extract validation from HTML5 attributes
                        if (input.dataset) {{
                            for (const [key, value] of Object.entries(input.dataset)) {{
                                if (key.startsWith('validate')) {{
                                    rules[name][key] = value;
                                }}
                            }}
                        }}
                        
                        // Extract aria attributes for accessibility-compliant validation
                        if (input.getAttribute('aria-required')) {{
                            rules[name].required = input.getAttribute('aria-required') === 'true';
                        }}
                    }}
                    
                    return rules;
                }}
            """, form_selector)
            
            # Also check for JavaScript-based validation by looking for form event listeners
            js_validation = page.evaluate("""
                () => {
                    // Check for common validation libraries
                    return {
                        hasJquery: typeof jQuery !== 'undefined',
                        hasFormValidation: typeof jQuery !== 'undefined' && typeof jQuery.fn.validate !== 'undefined',
                        hasReactFinalForm: typeof window.ReactFinalForm !== 'undefined',
                        hasFormik: typeof window.Formik !== 'undefined',
                        hasYup: typeof window.yup !== 'undefined'
                    };
                }
            """)
            
            return {
                "input_rules": validation_rules,
                "js_validation": js_validation
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting form validation rules: {e}")
            return {}

    def _parse_plan(self, response: str) -> BrowserPlan:
        """Parse and validate the LLM-generated automation plan"""
        try:
            # Try to extract JSON from code blocks first
            json_match = re.search(r'```(?:json)?\n?(.+?)\n?```', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group(1).strip())
            else:
                # Try to find a JSON object anywhere in the response
                json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
                json_match = re.search(json_pattern, response, re.DOTALL)
                if not json_match:
                    raise ValueError("No JSON object found in the response.")
                plan_data = json.loads(json_match.group(0))
            
            # Validate and normalize tasks
            validated_tasks = []
            for task in plan_data.get("tasks", []):
                # Ensure minimal required fields
                if "action" not in task:
                    self.logger.warning(f"Skipping task without action: {task}")
                    continue
                
                # Clean up and normalize task
                normalized_task = {
                    "action": task["action"].lower().strip(),
                    "selector": task.get("selector", "").strip(),
                    "value": task.get("value", ""),
                    "description": task.get("description", f"Performing {task['action']}")
                }
                
                validated_tasks.append(normalized_task)
                
            return BrowserPlan(tasks=validated_tasks)
        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            self.logger.error(f"Plan parsing failed: {e}")
            return BrowserPlan(tasks=[])

    def _execute_with_retries(self, page: Page, task: Dict[str, Any],
                            handler: Callable[[Page, Dict[str, Any]], Dict[str, Any]],
                            executed_context: str = "") -> Dict[str, Any]:
        """Execute a task with retry logic"""
        attempts = 0
        result = {}
        
        while attempts < self.max_retries:
            result = self._execute_safe_task(page, task, handler)
            if result.get("success", False):
                return result
                
            attempts += 1
            self.logger.info(f"Retrying task '{task.get('action')}' (attempt {attempts + 1}/{self.max_retries})")
            time.sleep(1 * attempts)
            
        # If all retries failed, try with fallback mechanism
        if task.get("action") in ["click", "type"]:
            self.logger.info("All standard approaches failed. Using fallback mechanism.")
            result = self._fallback_with_numbered_elements(page, task, executed_context)
            
        return result

    def _execute_safe_task(self, page: Page, task: Dict[str, Any],
                        handler: Callable[[Page, Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a task with error handling"""
        try:
            return handler(page, task)
        except Exception as e:
            action = task.get("action", "unknown")
            self.logger.exception(f"Error executing task '{action}':")
            return {"action": action, "success": False, "message": f"Error: {str(e)}"}

    def _fallback_with_numbered_elements(self, page: Page, task: Dict[str, Any], executed_context: str = "") -> Dict[str, Any]:
        """Fallback method that numbers elements on the page for easier selection"""
        try:
            # Determine the appropriate elements to target based on the action
            if task.get("action") == "click":
                selector = "button, a, input[type='submit'], input[type='button'], [role='button'], [onclick]"
            elif task.get("action") == "type":
                selector = "input[type='text'], input[type='email'], input[type='password'], textarea"
            else:
                return {"action": task.get("action"), "success": False, 
                        "message": f"No fallback implemented for action: {task.get('action')}"}
                        
            # Add numbered overlays to the page
            page.evaluate(f"""
                () => {{
                    // Clean up any existing overlays
                    document.querySelectorAll('.numbered-overlay').forEach(el => el.remove());
                    
                    // Find elements
                    const elements = Array.from(document.querySelectorAll('{selector}'))
                        .filter(el => {{
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0 && 
                                window.getComputedStyle(el).display !== 'none' &&
                                window.getComputedStyle(el).visibility !== 'hidden';
                        }});
                        
                    // Add numbered overlays
                    elements.forEach((el, index) => {{
                        const rect = el.getBoundingClientRect();
                        const overlay = document.createElement('div');
                        overlay.className = 'numbered-overlay';
                        overlay.textContent = (index + 1).toString();
                        overlay.style.position = 'absolute';
                        overlay.style.left = (rect.left + window.scrollX) + 'px';
                        overlay.style.top = (rect.top + window.scrollY) + 'px';
                        overlay.style.backgroundColor = 'red';
                        overlay.style.color = 'white';
                        overlay.style.padding = '2px 5px';
                        overlay.style.borderRadius = '50%';
                        overlay.style.fontSize = '14px';
                        overlay.style.fontWeight = 'bold';
                        overlay.style.zIndex = '10000';
                        overlay.style.pointerEvents = 'none';
                        document.body.appendChild(overlay);
                    }});
                    
                    return elements.length;
                }}
            """)
            
            # Simple fallback - just click the first element or input text into the first field
            if task.get("action") == "click":
                element = page.query_selector(selector)
                if element:
                    element.click()
                    return {"action": "click", "success": True, 
                            "message": "Clicked the first matching element using fallback mechanism"}
            elif task.get("action") == "type":
                element = page.query_selector(selector)
                if element:
                    element.fill(task.get("value", ""))
                    return {"action": "type", "success": True, 
                            "message": f"Typed '{task.get('value', '')}' into the first matching element using fallback"}
                    
            return {"action": task.get("action"), "success": False, 
                    "message": "Fallback mechanism could not find any suitable elements"}
                    
        except Exception as e:
            self.logger.error(f"Fallback mechanism failed: {e}")
            return {"action": task.get("action"), "success": False, 
                    "message": f"Fallback mechanism error: {str(e)}"}
        
    def _handle_navigation(self, page: Page, url: str) -> Dict[str, Any]:
        """Handle navigation to a URL with robust error handling and retries"""
        if isinstance(url, dict) and "value" in url:
            url = url.get("value", "")
            
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
            
        try:
            # First, wait for any pending network requests to complete
            self.logger.info(f"Navigating to {url}")
            
            # Attempt navigation with timeout and error handling
            page.goto(url, timeout=self.default_timeout, wait_until="domcontentloaded")
            
            # Wait for either load or error
            page.wait_for_selector("body", timeout=self.default_timeout)
            
            # Additional wait for page to stabilize
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                # Network might not fully idle, but we can continue
                pass
                    
            # Check for common error patterns
            error_selectors = [
                "title:has-text('404')",
                "title:has-text('Error')",
                "title:has-text('Not Found')",
                "h1:has-text('404')",
                "h1:has-text('Not Found')",
                "[class*='error-page']",
                "[class*='not-found']"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = page.query_selector(selector)
                    if error_element and error_element.is_visible():
                        return {"action": "navigate", "success": False, "message": f"Navigation error: Page loaded but appears to be an error page ({selector})"}
                except Exception:
                    continue
            
            return {"action": "navigate", "success": True, "message": f"Successfully navigated to {url}"}
            
        except Exception as e:
            self.logger.error(f"Navigation to {url} failed: {e}")
            return {"action": "navigate", "success": False, "message": f"Navigation failed: {str(e)}"}

    def _attempt_recovery(self, task: Dict[str, Any], executed_context: str) -> bool:
        """Attempt to recover from a failed task execution"""
        action = task.get("action", "")
        
        self.logger.info(f"Attempting recovery for failed {action} action")
        
        try:
            # Simple recovery strategy based on the action type
            if action == "navigate":
                url = task.get("value", "")
                if url:
                    # Try alternative navigation approach
                    try:
                        self.page.evaluate(f"window.location.href = '{url}'")
                        time.sleep(2)  # Wait for navigation to complete
                        return True
                    except Exception:
                        # If JavaScript navigation fails, try one more direct approach
                        try:
                            self.page.goto(url, timeout=30000)
                            return True
                        except Exception:
                            return False
            
            elif action == "click":
                selector = task.get("selector", "")
                if selector:
                    # Try alternative clicking methods
                    try:
                        # Try JavaScript click
                        self.page.evaluate(f"""
                            (() => {{
                                const elements = document.querySelectorAll('{selector}');
                                if (elements.length > 0) {{
                                    elements[0].click();
                                    return true;
                                }}
                                return false;
                            }})()
                        """)
                        time.sleep(1)
                        return True
                    except Exception:
                        return False
            
            elif action == "type":
                selector = task.get("selector", "")
                value = task.get("value", "")
                if selector and value:
                    # Try alternative typing methods
                    try:
                        # Try JavaScript value setting
                        self.page.evaluate(f"""
                            (() => {{
                                const elements = document.querySelectorAll('{selector}');
                                if (elements.length > 0) {{
                                    elements[0].value = '{value}';
                                    elements[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    elements[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    return true;
                                }}
                                return false;
                            }})()
                        """)
                        time.sleep(1)
                        return True
                    except Exception:
                        return False
                        
            # For all other actions, return False to indicate recovery failed
            return False
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False

    def _handle_click(self, page: Page, selector: str) -> Dict[str, Any]:
        """Handle clicking on an element with improved reliability"""
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        try:
            # First check if selector exists and is visible
            try:
                element = page.wait_for_selector(selector, state="visible", timeout=self.default_timeout)
                if not element:
                    return {"action": "click", "success": False, "message": f"Element not found or not visible: {selector}"}
            except Exception as e:
                return {"action": "click", "success": False, "message": f"Error waiting for element: {str(e)}"}
            
            # Scroll element into view first
            element.scroll_into_view_if_needed()
            
            # Wait a moment for any animations to complete
            time.sleep(0.5)
            
            # Try to click
            element.click(force=True, timeout=self.default_timeout)
            
            # Check if click caused navigation
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                # It's okay if this times out - not all clicks navigate
                pass
                
            return {"action": "click", "success": True, "message": f"Clicked element: {selector}"}
        except Exception as e:
            self.logger.error(f"Click action failed on selector {selector}: {e}")
            return {"action": "click", "success": False, "message": f"Click failed: {str(e)}"}

    def _handle_typing(self, page: Page, selector: str, text: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle typing into an input field with improved reliability"""
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        if isinstance(text, dict) and "value" in text:
            text = text.get("value", "")
            
        try:
            # Wait for the element to be attached to the DOM
            element = page.wait_for_selector(selector, state="attached", timeout=self.default_timeout)
            if not element:
                return {"action": "type", "success": False, "message": f"Element not found: {selector}"}
                
            # Make sure element is visible and editable
            is_editable = page.evaluate("""
                (element) => {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                        style.visibility !== 'hidden' && 
                        !element.disabled && 
                        !element.readOnly;
                }
            """, element)
            
            if not is_editable:
                return {"action": "type", "success": False, "message": f"Element is not editable: {selector}"}
                
            # Clear the field first
            element.fill("")
            
            # Type the text
            element.fill(text, timeout=self.default_timeout)
            
            return {"action": "type", "success": True, "message": f"Typed '{text}' into element"}
        except Exception as e:
            self.logger.error(f"Typing action failed on selector {selector}: {e}")
            return {"action": "type", "success": False, "message": f"Typing failed: {str(e)}"}

    def _handle_wait(self, seconds: str) -> Dict[str, Any]:
        """Handle explicit waiting for a specific time"""
        if isinstance(seconds, dict) and "value" in seconds:
            seconds = seconds.get("value", "")
            
        try:
            wait_time = float(seconds)
            self.logger.info(f"Waiting for {wait_time} seconds")
            time.sleep(wait_time)
            return {"action": "wait", "success": True, "message": f"Waited {wait_time} seconds"}
        except ValueError as e:
            self.logger.error(f"Invalid wait time provided: {seconds}")
            return {"action": "wait", "success": False, "message": f"Invalid wait time: {str(e)}"}

    def _handle_wait_for_ajax(self, page: Page, seconds: str) -> Dict[str, Any]:
        """Wait for AJAX requests to complete"""
        if isinstance(seconds, dict) and "value" in seconds:
            seconds = seconds.get("value", "")
            
        try:
            timeout_seconds = int(seconds) if seconds.strip() != "" else 10
            self.logger.info(f"Waiting for AJAX/network activity for up to {timeout_seconds} seconds")
            
            # Using our injected helper function
            try:
                page.evaluate(f"""
                    async () => {{
                        try {{
                            await window.browserAutomationHelpers.waitForNetworkIdle({timeout_seconds * 1000});
                            return true;
                        }} catch (e) {{
                            console.error("Error waiting for network idle:", e);
                            return false;
                        }}
                    }}
                """)
            except Exception:
                # Fallback method if helper function fails
                end_time = time.time() + timeout_seconds
                while time.time() < end_time:
                    ajax_complete = page.evaluate("""
                        () => {
                            return (window.jQuery ? jQuery.active === 0 : true) &&
                                (typeof window.fetch === 'function' ? true : true);
                        }
                    """)
                    if ajax_complete:
                        break
                    time.sleep(0.5)
            
            # Wait a bit longer to be sure things have settled
            time.sleep(1)
            
            return {"action": "wait_for_ajax", "success": True, "message": "AJAX/network activity subsided"}
        except Exception as e:
            self.logger.error(f"Wait for AJAX failed: {e}")
            return {"action": "wait_for_ajax", "success": False, "message": f"Wait for AJAX failed: {str(e)}"}

    def _handle_wait_for_navigation(self, page: Page, timeout: str) -> Dict[str, Any]:
        """Wait for page navigation to complete"""
        if isinstance(timeout, dict) and "value" in timeout:
            timeout = timeout.get("value", "")
            
        try:
            timeout_ms = int(timeout) if timeout.strip() != "" else 30000
            self.logger.info(f"Waiting for navigation to complete (timeout: {timeout_ms}ms)")
            
            try:
                # Wait for domcontentloaded at minimum
                page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
                
                # Try waiting for networkidle but don't fail if it times out
                try:
                    page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 5000))
                except Exception:
                    self.logger.info("Network didn't become idle, but page is usable")
                    
                return {"action": "wait_for_navigation", "success": True, "message": "Navigation completed"}
            except Exception:
                # Check if the page is still functional even though load state timed out
                if "body" in page.content():
                    self.logger.info("Navigation didn't fully complete but page is usable")
                    return {"action": "wait_for_navigation", "success": True, "message": "Navigation partially completed"}
                    
                return {"action": "wait_for_navigation", "success": False, "message": "Navigation timed out"}
                
        except Exception as e:
            self.logger.error(f"Wait for navigation failed: {e}")
            return {"action": "wait_for_navigation", "success": False, "message": f"Wait for navigation failed: {str(e)}"}

    def _handle_wait_for_selector(self, page: Page, selector: str, timeout: str) -> Dict[str, Any]:
        """Wait for a specific selector to appear"""
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        if isinstance(timeout, dict) and "value" in timeout:
            timeout = timeout.get("value", "")
            
        try:
            timeout_ms = int(timeout) if timeout.strip() != "" else self.default_timeout
            self.logger.info(f"Waiting for selector: {selector} (timeout: {timeout_ms}ms)")
            
            try:
                element = page.wait_for_selector(selector, state="visible", timeout=timeout_ms)
                if element:
                    return {"action": "wait_for_selector", "success": True, "message": f"Selector appeared: {selector}"}
                else:
                    return {"action": "wait_for_selector", "success": False, "message": f"Selector didn't appear: {selector}"}
            except Exception:
                return {"action": "wait_for_selector", "success": False, "message": f"Timeout waiting for selector: {selector}"}
                
        except Exception as e:
            self.logger.error(f"Wait for selector failed: {e}")
            return {"action": "wait_for_selector", "success": False, "message": f"Wait for selector failed: {str(e)}"}

    def _handle_wait_for_function(self, page: Page, js_condition: str) -> Dict[str, Any]:
        """Wait for a custom JavaScript condition to be true"""
        if isinstance(js_condition, dict) and "value" in js_condition:
            js_condition = js_condition.get("value", "")
            
        try:
            self.logger.info(f"Waiting for JavaScript condition")
            
            # Wrap the condition in a function that returns a boolean
            wrapped_js = f"""
                () => {{
                    try {{
                        return Boolean({js_condition});
                    }} catch (e) {{
                        console.error("Error in wait condition:", e);
                        return false;
                    }}
                }}
            """
            
            page.wait_for_function(wrapped_js, timeout=self.default_timeout)
            return {"action": "wait_for_function", "success": True, "message": "JavaScript condition met"}
        except Exception as e:
            self.logger.error(f"Wait for function failed: {e}")
            return {"action": "wait_for_function", "success": False, "message": f"Wait for function failed: {str(e)}"}

    def _handle_scroll(self, page: Page, selector: str) -> Dict[str, Any]:
        """Handle scrolling to an element or position"""
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        try:
            if selector:
                # Scroll to specific element
                try:
                    element = page.wait_for_selector(selector, timeout=self.default_timeout)
                    if not element:
                        return {"action": "scroll", "success": False, "message": f"Element not found: {selector}"}
                        
                    element.scroll_into_view_if_needed()
                    scroll_target = selector
                except Exception as e:
                    return {"action": "scroll", "success": False, "message": f"Error scrolling to element: {str(e)}"}
            else:
                # Scroll to bottom of page by default
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                scroll_target = "page bottom"
                
            # Wait a moment for any lazy-loaded content to appear
            time.sleep(1)
                
            return {"action": "scroll", "success": True, "message": f"Scrolled to {scroll_target}"}
        except Exception as e:
            self.logger.error(f"Scroll action failed: {e}")
            return {"action": "scroll", "success": False, "message": f"Scroll failed: {str(e)}"}
        
    def _handle_modal(self, page, modal_element, task_context: str):
        """
        Enhanced modal handler that can perform complex interactions within modals,
        not just dismiss them. Treats modals as mini-pages that may require multiple actions.
        """
        try:
            # First, take a screenshot of the modal
            modal_screenshot = modal_element.screenshot()
            
            # Extract modal text and structure for better context
            modal_text = page.evaluate("(el) => el.innerText", modal_element)
            
            # Get detailed information about interactive elements in the modal
            modal_elements = page.evaluate("""
                (modal) => {
                    const interactiveElements = Array.from(modal.querySelectorAll(
                        'button, a, input, select, textarea, [role="button"], [role="checkbox"], [role="radio"]'
                    )).filter(el => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return rect.width > 0 && rect.height > 0 && 
                            style.display !== 'none' && 
                            style.visibility !== 'hidden';
                    });
                    
                    return interactiveElements.map(el => {
                        return {
                            tag: el.tagName.toLowerCase(),
                            type: el.getAttribute('type'),
                            id: el.id,
                            name: el.getAttribute('name'),
                            value: el.value,
                            placeholder: el.getAttribute('placeholder'),
                            text: el.innerText || el.textContent,
                            ariaLabel: el.getAttribute('aria-label'),
                            required: el.required,
                            classes: Array.from(el.classList),
                            attributes: Object.fromEntries(
                                Array.from(el.attributes)
                                    .filter(attr => ['role', 'data-', 'aria-'].some(prefix => 
                                        attr.name === 'role' || attr.name.startsWith(prefix)
                                    ))
                                    .map(attr => [attr.name, attr.value])
                            ),
                            isLikelySubmit: (
                                (el.tagName === 'BUTTON' && el.getAttribute('type') === 'submit') ||
                                (el.tagName === 'INPUT' && el.getAttribute('type') === 'submit') ||
                                (['submit', 'save', 'ok', 'continue', 'next'].some(keyword => 
                                    (el.innerText || '').toLowerCase().includes(keyword) ||
                                    (el.value || '').toLowerCase().includes(keyword)
                                ))
                            ),
                            isLikelyCancel: (
                                ['cancel', 'close', 'dismiss', 'no thanks', 'skip', 'back'].some(keyword => 
                                    (el.innerText || '').toLowerCase().includes(keyword) ||
                                    (el.value || '').toLowerCase().includes(keyword)
                                )
                            )
                        };
                    });
                }
            """, modal_element)
            
            # Determine if this is a form modal that requires input
            has_form_elements = any(el.get('tag') in ['input', 'textarea', 'select'] for el in modal_elements)
            
            # Build a comprehensive prompt for the LLM
            prompt = f"""
    Analyze this modal dialog to determine how to interact with it.

    MODAL TEXT:
    {modal_text}

    TASK CONTEXT:
    {task_context}

    INTERACTIVE ELEMENTS ({len(modal_elements)} found):
    {json.dumps(modal_elements, indent=2)}

    Based on the modal content and task context, determine the best action to take.
    Return a JSON response with the appropriate action type and details:

    1. If the modal should be dismissed/closed without any interaction:
    {{"action": "dismiss"}}

    2. If the modal should be ignored and left open:
    {{"action": "ignore"}}

    3. If the modal requires filling out a form:
    {{"action": "form", "fields": [
        {{"selector": "tag and identifier", "value": "text to input", "description": "what this field is for"}}
    ], "submit": "identifier of submit button"}}

    4. If the modal requires a single action like clicking a specific button:
    {{"action": "interact", "element": "text or identifier of element to click"}}

    5. If the modal requires a sequence of actions:
    {{"action": "sequence", "steps": [
        {{"action": "type", "selector": "identifier", "value": "text to input"}},
        {{"action": "click", "selector": "identifier"}}
    ]}}

    Return only the JSON with your decision based on the modal content and task context.
    """
            
            # If the LLM supports vision, use it
            if hasattr(self.llm, "supports_vision") and self.llm.supports_vision:
                response_text = self.llm.generate_from_image(prompt, image_bytes=modal_screenshot)
            else:
                response_text = self.llm.generate(prompt=prompt)
                
            self.logger.info(f"LLM response for modal analysis: {response_text}")
            
            # Extract JSON from the response
            json_match = re.search(r'```json\n?(.+?)\n?```', response_text, re.DOTALL)
            json_text = json_match.group(1).strip() if json_match else response_text.strip()
            
            try:
                decision = json.loads(json_text)
            except json.JSONDecodeError:
                # Try to extract just the JSON object
                json_pattern = r'\{.*\}'
                json_match = re.search(json_pattern, response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                    decision = json.loads(json_text)
                else:
                    self.logger.warning("Could not parse LLM response as JSON")
                    # Default to a conservative approach - ignore the modal
                    decision = {"action": "ignore"}
            
            # Handle the decision based on the action type
            action_type = decision.get("action", "ignore").lower()
            
            if action_type == "dismiss":
                # Try multiple strategies to dismiss the modal
                self._try_dismiss_strategies(modal_element)
                return True
                
            elif action_type == "ignore":
                self.logger.info("Modal left intact according to LLM analysis.")
                return False
                
            elif action_type == "interact" and decision.get("element"):
                # Find and click the specified element
                target_text = decision.get("element")
                success = self._click_element_by_text(modal_element, target_text)
                return success
                
            elif action_type == "form" and decision.get("fields"):
                # Fill out a form in the modal
                return self._fill_modal_form(modal_element, decision.get("fields", []), decision.get("submit"))
                
            elif action_type == "sequence" and decision.get("steps"):
                # Perform a sequence of actions in the modal
                return self._perform_modal_sequence(modal_element, decision.get("steps", []))
                
            else:
                self.logger.warning(f"Unknown or unsupported modal action type: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Modal handling error: {e}")
            return False

    def _fill_modal_form(self, modal_element, fields, submit_identifier):
        """Fill out a form in a modal with the specified field values and submit it."""
        try:
            success = True
            
            # Process each field
            for field in fields:
                selector = field.get("selector")
                value = field.get("value")
                
                if not selector or value is None:
                    continue
                    
                # Find the field element
                field_element = None
                
                # Try different strategies to find the element
                # 1. Direct CSS selector
                if selector.startswith("#") or selector.startswith(".") or selector.startswith("["):
                    try:
                        field_element = modal_element.query_selector(selector)
                    except:
                        pass
                        
                # 2. By tag and identifier
                if not field_element and ' ' in selector:
                    tag, identifier = selector.split(' ', 1)
                    try:
                        js_query = f"""
                            (modal, tag, identifier) => {{
                                const elements = Array.from(modal.querySelectorAll(tag));
                                return elements.find(el => 
                                    (el.id && el.id.includes(identifier)) || 
                                    (el.name && el.name.includes(identifier)) || 
                                    (el.placeholder && el.placeholder.includes(identifier)) ||
                                    (el.labels && Array.from(el.labels).some(label => label.textContent.includes(identifier))) ||
                                    ((el.previousElementSibling && 
                                    el.previousElementSibling.textContent && 
                                    el.previousElementSibling.textContent.includes(identifier)))
                                );
                            }}
                        """
                        field_element_info = self.page.evaluate(js_query, modal_element, tag, identifier)
                        if field_element_info:
                            # Find this element in the DOM again
                            if 'id' in field_element_info and field_element_info['id']:
                                field_element = modal_element.query_selector(f"#{field_element_info['id']}")
                            elif 'name' in field_element_info and field_element_info['name']:
                                field_element = modal_element.query_selector(f"[name='{field_element_info['name']}']")
                    except:
                        pass
                        
                # 3. By visible text or label near the field
                if not field_element:
                    try:
                        js_query = f"""
                            (modal, identifier) => {{
                                // Find labels with matching text
                                const labels = Array.from(modal.querySelectorAll('label'))
                                    .filter(label => label.textContent.includes(identifier));
                                    
                                // If labels found, get the associated input
                                if (labels.length > 0) {{
                                    // Try by for attribute
                                    const forId = labels[0].getAttribute('for');
                                    if (forId) {{
                                        const input = modal.querySelector(`#${{forId}}`);
                                        if (input) return input;
                                    }}
                                    
                                    // Try by next sibling
                                    const input = labels[0].nextElementSibling;
                                    if (input && (input.tagName === 'INPUT' || input.tagName === 'SELECT' || input.tagName === 'TEXTAREA')) {{
                                        return input;
                                    }}
                                }}
                                
                                // Try finding inputs near text containing the identifier
                                const textNodes = Array.from(modal.querySelectorAll('*'))
                                    .filter(el => el.textContent.includes(identifier) && 
                                        !['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName));
                                        
                                for (const node of textNodes) {{
                                    // Check siblings and nearby elements
                                    const input = node.nextElementSibling || 
                                                (node.parentElement && node.parentElement.querySelector('input, select, textarea'));
                                    if (input && (input.tagName === 'INPUT' || input.tagName === 'SELECT' || input.tagName === 'TEXTAREA')) {{
                                        return input;
                                    }}
                                }}
                                
                                return null;
                            }}
                        """
                        field_element = self.page.evaluate(js_query, modal_element, selector)
                    except:
                        pass
                
                # If we found the field element, fill it
                if field_element:
                    # Handle different types of inputs
                    tag_name = field_element.evaluate("el => el.tagName.toLowerCase()")
                    input_type = field_element.evaluate("el => el.type")
                    
                    if tag_name == 'input' and input_type in ['text', 'email', 'password', 'tel', 'number', 'url']:
                        # Text input fields
                        field_element.fill(value)
                        self.logger.info(f"Filled text field '{selector}' with '{value}'")
                        
                    elif tag_name == 'textarea':
                        # Textarea
                        field_element.fill(value)
                        self.logger.info(f"Filled textarea '{selector}' with '{value}'")
                        
                    elif tag_name == 'select':
                        # Select dropdown
                        field_element.select_option(value=value)
                        self.logger.info(f"Selected option '{value}' in select '{selector}'")
                        
                    elif input_type == 'checkbox' or input_type == 'radio':
                        # Checkbox or radio button
                        if value.lower() in ['true', 'yes', 'on', '1']:
                            if not field_element.is_checked():
                                field_element.check()
                                self.logger.info(f"Checked '{selector}'")
                        else:
                            if field_element.is_checked():
                                field_element.uncheck()
                                self.logger.info(f"Unchecked '{selector}'")
                    else:
                        self.logger.warning(f"Unsupported field type: {tag_name} ({input_type}) for '{selector}'")
                        success = False
                else:
                    self.logger.warning(f"Could not find field element: {selector}")
                    success = False
            
            # Submit the form if specified
            if submit_identifier and success:
                submit_element = None
                
                # Try to find the submit button
                # 1. Direct selector
                if submit_identifier.startswith("#") or submit_identifier.startswith("."):
                    try:
                        submit_element = modal_element.query_selector(submit_identifier)
                    except:
                        pass
                
                # 2. By text content
                if not submit_element:
                    try:
                        js_query = f"""
                            (modal, text) => {{
                                const buttons = Array.from(modal.querySelectorAll('button, input[type="submit"], input[type="button"], a'));
                                return buttons.find(btn => 
                                    (btn.innerText && btn.innerText.includes(text)) || 
                                    (btn.value && btn.value.includes(text))
                                );
                            }}
                        """
                        submit_element = self.page.evaluate(js_query, modal_element, submit_identifier)
                    except:
                        pass
                
                # 3. Find any submit button if a specific one wasn't found
                if not submit_element:
                    submit_element = modal_element.query_selector('button[type="submit"], input[type="submit"]')
                
                # 4. Find a button that looks like a submit button
                if not submit_element:
                    js_query = """
                        (modal) => {
                            const buttons = Array.from(modal.querySelectorAll('button, input[type="button"], a.button, [role="button"]'));
                            const submitKeywords = ['submit', 'save', 'ok', 'continue', 'next', 'confirm'];
                            return buttons.find(btn => 
                                submitKeywords.some(keyword => 
                                    (btn.innerText && btn.innerText.toLowerCase().includes(keyword)) ||
                                    (btn.value && btn.value.toLowerCase().includes(keyword))
                                )
                            );
                        }
                    """
                    submit_element = self.page.evaluate(js_query, modal_element)
                
                if submit_element:
                    submit_element.click()
                    self.logger.info(f"Submitted form by clicking '{submit_identifier}'")
                    # Wait a moment for the form submission to be processed
                    time.sleep(1)
                    return True
                else:
                    self.logger.warning(f"Could not find submit button: {submit_identifier}")
                    return False
            
            return success
        except Exception as e:
            self.logger.error(f"Error filling modal form: {e}")
            return False

    def _perform_modal_sequence(self, modal_element, steps):
        """Perform a sequence of actions in a modal."""
        try:
            for i, step in enumerate(steps):
                action = step.get("action", "").lower()
                selector = step.get("selector", "")
                value = step.get("value", "")
                
                self.logger.info(f"Performing modal sequence step {i+1}/{len(steps)}: {action} on {selector}")
                
                if action == "click":
                    # Find and click the element
                    element = modal_element.query_selector(selector)
                    if element:
                        element.click()
                        self.logger.info(f"Clicked element: {selector}")
                    else:
                        # Try by text if selector doesn't work
                        success = self._click_element_by_text(modal_element, selector)
                        if not success:
                            self.logger.warning(f"Could not find element to click: {selector}")
                            return False
                            
                elif action == "type":
                    # Find and fill the element
                    element = modal_element.query_selector(selector)
                    if element:
                        element.fill(value)
                        self.logger.info(f"Typed '{value}' into element: {selector}")
                    else:
                        self.logger.warning(f"Could not find element to type into: {selector}")
                        return False
                        
                elif action == "select":
                    # Find and select from dropdown
                    element = modal_element.query_selector(selector)
                    if element:
                        element.select_option(value=value)
                        self.logger.info(f"Selected option '{value}' in element: {selector}")
                    else:
                        self.logger.warning(f"Could not find dropdown to select from: {selector}")
                        return False
                        
                elif action == "check" or action == "uncheck":
                    # Handle checkboxes
                    element = modal_element.query_selector(selector)
                    if element:
                        if action == "check":
                            element.check()
                            self.logger.info(f"Checked element: {selector}")
                        else:
                            element.uncheck()
                            self.logger.info(f"Unchecked element: {selector}")
                    else:
                        self.logger.warning(f"Could not find checkbox: {selector}")
                        return False
                        
                elif action == "wait":
                    # Wait for a specified time
                    wait_time = float(value) if value else 1.0
                    time.sleep(wait_time)
                    self.logger.info(f"Waited for {wait_time} seconds")
                    
                else:
                    self.logger.warning(f"Unsupported action in modal sequence: {action}")
                    return False
                    
                # Small delay between actions for stability
                time.sleep(0.3)
                
            return True
        except Exception as e:
            self.logger.error(f"Error performing modal sequence: {e}")
            return False

    def _try_dismiss_strategies(self, modal_element):
        """Try multiple strategies to dismiss a modal."""
        try:
            # Strategy 1: Look for close buttons by common selectors
            close_selectors = [
                ".close", 
                ".btn-close", 
                "[aria-label='Close']", 
                "[data-dismiss='modal']",
                "button.dismiss",
                ".modal-close",
                "button.close",
                "[title='Close']",
                ".dismiss-button",
                "button:has-text('Close')",
                "button:has-text('Cancel')",
                "button:has-text('No thanks')",
                "button:has-text('Skip')"
            ]
            
            for selector in close_selectors:
                try:
                    close_btns = modal_element.query_selector_all(selector)
                    for btn in close_btns:
                        if btn.is_visible():
                            btn.click()
                            self.logger.info(f"Modal dismissed using close button: {selector}")
                            time.sleep(0.5)
                            return True
                except:
                    continue
            
            # Strategy 2: Look for buttons with X/close text or icon
            try:
                x_buttons = modal_element.query_selector_all("button, a, [role='button']")
                for btn in x_buttons:
                    try:
                        text = btn.inner_text().strip().lower()
                        if text in ["×", "x", "close", "dismiss", "cancel", "no thanks", "skip", "back"]:
                            btn.click()
                            self.logger.info(f"Modal dismissed using text match button: {text}")
                            time.sleep(0.5)
                            return True
                            
                        # Check for X icon (common close button pattern)
                        contains_x_icon = btn.evaluate("""
                            (el) => {
                                const icons = el.querySelectorAll('i, span, svg');
                                return Array.from(icons).some(icon => 
                                    icon.className.includes('close') || 
                                    icon.className.includes('times') ||
                                    (icon.getAttribute('aria-label') && 
                                    icon.getAttribute('aria-label').toLowerCase().includes('close'))
                                );
                            }
                        """)
                        
                        if contains_x_icon:
                            btn.click()
                            self.logger.info("Modal dismissed using button with X icon")
                            time.sleep(0.5)
                            return True
                    except:
                        continue
            except:
                pass
            
            # Strategy 3: Look for elements outside the modal to click (overlay/backdrop)
            try:
                # Find the modal's parent that might be an overlay
                overlay = modal_element.evaluate("""
                    (modal) => {
                        let parent = modal.parentElement;
                        while (parent && parent !== document.body) {
                            const style = window.getComputedStyle(parent);
                            // Check if this element appears to be an overlay
                            if (style.position === 'fixed' && 
                                (style.backgroundColor.includes('rgba') || 
                                parent.className.includes('overlay') || 
                                parent.className.includes('backdrop'))) {
                                return parent;
                            }
                            parent = parent.parentElement;
                        }
                        return null;
                    }
                """)
                
                if overlay:
                    # Click outside the modal but on the overlay
                    overlay_dimensions = overlay.bounding_box()
                    modal_dimensions = modal_element.bounding_box()
                    
                    # Find a point on the overlay but outside the modal
                    click_x = overlay_dimensions["x"] + 10
                    click_y = overlay_dimensions["y"] + 10
                    
                    # Make sure the point is outside the modal
                    if (click_x >= modal_dimensions["x"] and 
                        click_x <= modal_dimensions["x"] + modal_dimensions["width"] and
                        click_y >= modal_dimensions["y"] and 
                        click_y <= modal_dimensions["y"] + modal_dimensions["height"]):
                        # Try a different point
                        click_x = overlay_dimensions["x"] + overlay_dimensions["width"] - 10
                        click_y = overlay_dimensions["y"] + 10
                    
                    # Click the point on the overlay
                    self.page.mouse.click(click_x, click_y)
                    self.logger.info(f"Clicked outside modal on overlay at ({click_x}, {click_y})")
                    time.sleep(0.5)
                    
                    # Check if the modal is still visible
                    is_visible = modal_element.is_visible()
                    if not is_visible:
                        return True
            except:
                pass
            
            # Strategy 4: Press Escape key to close modal
            try:
                self.page.keyboard.press("Escape")
                self.logger.info("Pressed Escape key to dismiss modal")
                time.sleep(0.5)
                
                # Check if the modal is still visible
                is_visible = modal_element.is_visible()
                if not is_visible:
                    return True
            except:
                pass
            
            # Strategy 5: Try to use JavaScript to remove the modal
            try:
                self.page.evaluate("(modal) => { modal.remove(); }", modal_element)
                self.logger.info("Modal dismissed by removal.")
                time.sleep(0.5)
                return True
            except:
                pass
            
            # If all strategies failed
            self.logger.warning("All dismiss strategies failed for this modal")
            return False
        except Exception as e:
            self.logger.error(f"Error in modal dismiss strategies: {e}")
            return False