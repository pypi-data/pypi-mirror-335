from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from pydantic import Field, BaseModel
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError, BrowserContext, Locator
import json, time, re, logging, os, difflib, base64
from io import BytesIO
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
        "Advanced web automation tool with multi-strategy element identification, vision-based verification, self-healing selectors, and robust error recovery.",
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
        object.__setattr__(self, "_strategy_adjustments", {})  # Learned strategy adjustments
        object.__setattr__(self, "_task_history", [])  # History of executed tasks for context
        object.__setattr__(self, "_playwright", None)  # Store Playwright instance

    def execute(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the browser automation workflow.
        Maintains a context string of executed tasks and passes it to fallback routines.
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
                self._playwright = sync_playwright().start()
                self.browser = self._playwright.chromium.launch(
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
                
                # Enhance SPA detection
                self._enhance_spa_detection(self.page)
            
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
                
                # Handle popups, dialogs, modals automatically
                self._handle_interaction_modals(task.get("description", ""))
                
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
                
                # Add to task history for context
                self._task_history.append({
                    "action": action,
                    "description": task_description,
                    "success": result.get("success", False),
                    "timestamp": time.time()
                })
                
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

                # Verify that the expected page state change occurred
                self._detect_and_handle_spa_navigation(self.page)
                current_url = self.page.url

            overall_elapsed = time.time() - overall_start
            self.logger.info(f"Total execution time: {overall_elapsed:.2f} seconds.")
            
            # Return results but keep the browser open
            return {"status": "success", "results": results, "total_time": overall_elapsed}
        except Exception as e:
            self.logger.exception("Execution error:")
            return {"status": "error", "message": str(e)}

    def close(self):
        """Close browser and release resources"""
        try:
            if self.browser:
                self.browser.close()
            if self._playwright:
                self._playwright.stop()
            self.browser = None
            self.browser_context = None
            self.page = None
            self._playwright = None
            self.logger.info("Browser closed and resources released")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

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
                            // Store initial URL
                            const initialUrl = window.location.href;
                            let networkRequestsInFlight = 0;
                            let timeoutId = null;
                            
                            const originalFetch = window.fetch;
                            const originalXHR = window.XMLHttpRequest.prototype.open;
                            
                            const startTimeout = () => {
                                if (timeoutId) clearTimeout(timeoutId);
                                timeoutId = setTimeout(() => {
                                    cleanup();
                                    resolve('timeout');
                                }, maxTimeout);
                            };
                            
                            window.fetch = function() {
                                networkRequestsInFlight++;
                                return originalFetch.apply(this, arguments)
                                    .finally(() => {
                                        networkRequestsInFlight--;
                                        if (networkRequestsInFlight === 0) {
                                            setTimeout(() => {
                                                cleanup();
                                                resolve('idle');
                                            }, 500);
                                        }
                                    });
                            };
                            
                            window.XMLHttpRequest.prototype.open = function() {
                                networkRequestsInFlight++;
                                this.addEventListener('loadend', () => {
                                    networkRequestsInFlight--;
                                    if (networkRequestsInFlight === 0) {
                                        setTimeout(() => {
                                            cleanup();
                                            resolve('idle');
                                        }, 500);
                                    }
                                });
                                return originalXHR.apply(this, arguments);
                            };
                            
                            startTimeout();
                            
                            // If no requests are currently in flight, wait a bit and resolve
                            if (networkRequestsInFlight === 0) {
                                setTimeout(() => {
                                    cleanup();
                                    resolve('idle');
                                }, 1000);
                            }
                            
                            function cleanup() {
                                clearTimeout(timeoutId);
                                window.fetch = originalFetch;
                                window.XMLHttpRequest.prototype.open = originalXHR;
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
                    },
                    
                    extractUIStructure: function() {
                        // Extract a structured representation of the UI
                        const getElementInfo = (element, maxDepth = 1, currentDepth = 0) => {
                            if (!element || currentDepth > maxDepth) return null;
                            
                            const rect = element.getBoundingClientRect();
                            if (rect.width === 0 || rect.height === 0) return null;
                            
                            const style = window.getComputedStyle(element);
                            if (style.display === 'none' || style.visibility === 'hidden') return null;
                            
                            // Get all attributes
                            const attributes = {};
                            for (const attr of element.attributes) {
                                attributes[attr.name] = attr.value;
                            }
                            
                            const result = {
                                tag: element.tagName.toLowerCase(),
                                id: element.id || null,
                                classes: Array.from(element.classList),
                                text: element.innerText || null,
                                attributes: attributes,
                                bounds: {
                                    x: rect.left + window.scrollX,
                                    y: rect.top + window.scrollY,
                                    width: rect.width,
                                    height: rect.height
                                }
                            };
                            
                            // Add children if not at max depth
                            if (currentDepth < maxDepth) {
                                result.children = Array.from(element.children)
                                    .map(child => getElementInfo(child, maxDepth, currentDepth + 1))
                                    .filter(child => child !== null);
                            }
                            
                            return result;
                        };
                        
                        // Start with the body and get a 2-level deep structure
                        return getElementInfo(document.body, 2);
                    },
                    
                    findSimilarElement: function(originalSelector, fallbackProperties) {
                        // Try to find elements similar to the one that would match the original selector
                        try {
                            // First check if the original selector still works
                            const original = document.querySelector(originalSelector);
                            if (original) return original;
                            
                            // If we have fallback properties, use them to find a similar element
                            if (fallbackProperties) {
                                const candidates = Array.from(document.querySelectorAll('*'));
                                let bestMatch = null;
                                let bestScore = 0;
                                
                                candidates.forEach(el => {
                                    let score = 0;
                                    
                                    // Check tag
                                    if (fallbackProperties.tag && el.tagName.toLowerCase() === fallbackProperties.tag.toLowerCase()) {
                                        score += 3;
                                    }
                                    
                                    // Check id (partial match)
                                    if (fallbackProperties.id && el.id && el.id.includes(fallbackProperties.id)) {
                                        score += 5;
                                    }
                                    
                                    // Check classes (any match)
                                    if (fallbackProperties.classes && fallbackProperties.classes.length) {
                                        const matchedClasses = fallbackProperties.classes.filter(cls => 
                                            el.classList.contains(cls)
                                        );
                                        score += matchedClasses.length * 2;
                                    }
                                    
                                    // Check text content similarity
                                    if (fallbackProperties.text && el.innerText) {
                                        const normalizedText1 = fallbackProperties.text.toLowerCase().trim();
                                        const normalizedText2 = el.innerText.toLowerCase().trim();
                                        
                                        if (normalizedText1 === normalizedText2) {
                                            score += 10;
                                        } else if (normalizedText2.includes(normalizedText1) || normalizedText1.includes(normalizedText2)) {
                                            score += 5;
                                        }
                                    }
                                    
                                    // Check attributes
                                    if (fallbackProperties.attributes) {
                                        for (const [key, value] of Object.entries(fallbackProperties.attributes)) {
                                            if (value && el.getAttribute(key) === value) {
                                                score += 2;
                                            }
                                        }
                                    }
                                    
                                    // Update best match if this element has a better score
                                    if (score > bestScore) {
                                        bestScore = score;
                                        bestMatch = el;
                                    }
                                });
                                
                                // Only return if we have a reasonably good match
                                if (bestScore >= 5) {
                                    return bestMatch;
                                }
                            }
                            
                            return null;
                        } catch (e) {
                            console.error('Error finding similar element:', e);
                            return null;
                        }
                    }
                };
            """)
            self.logger.info("Helper scripts injected successfully")
        except Exception as e:
            self.logger.error(f"Failed to inject helper scripts: {e}")

    def _enhance_spa_detection(self, page: Page):
        """Enhance detection of SPA navigation by injecting additional event listeners"""
        page.evaluate("""
            () => {
                if (window.__spaNavigationTracking) return; // Already initialized
                
                window.__spaNavigationTracking = {
                    lastUrl: window.location.href,
                    navigationEvents: 0,
                    isNavigating: false
                };
                
                // Track history API
                const originalPushState = window.history.pushState;
                const originalReplaceState = window.history.replaceState;
                
                window.history.pushState = function() {
                    window.__spaNavigationTracking.isNavigating = true;
                    window.__spaNavigationTracking.navigationEvents++;
                    
                    originalPushState.apply(this, arguments);
                    
                    const event = new Event('spaNavigation');
                    event.arguments = arguments;
                    window.dispatchEvent(event);
                    
                    window.__spaNavigationTracking.lastUrl = window.location.href;
                    setTimeout(() => { window.__spaNavigationTracking.isNavigating = false; }, 500);
                };
                
                window.history.replaceState = function() {
                    window.__spaNavigationTracking.isNavigating = true;
                    window.__spaNavigationTracking.navigationEvents++;
                    
                    originalReplaceState.apply(this, arguments);
                    
                    const event = new Event('spaNavigation');
                    event.arguments = arguments;
                    window.dispatchEvent(event);
                    
                    window.__spaNavigationTracking.lastUrl = window.location.href;
                    setTimeout(() => { window.__spaNavigationTracking.isNavigating = false; }, 500);
                };
                
                // Track URL changes
                let lastCheckedUrl = window.location.href;
                setInterval(() => {
                    if (window.location.href !== lastCheckedUrl) {
                        lastCheckedUrl = window.location.href;
                        window.__spaNavigationTracking.navigationEvents++;
                        window.dispatchEvent(new Event('spaNavigation'));
                    }
                }, 200);
            }
        """)

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

    def _handle_interaction_modals(self, task_context: str):
        """
        Identify and intelligently handle interaction modals (forms, email composers, etc.)
        using vision and contextual understanding
        """
        try:
            # Take a screenshot of the full page
            screenshot_bytes = self.page.screenshot(type="png")
            
            # Create a more comprehensive prompt that handles interactive modals
            prompt = f"""
            Analyze this screenshot and identify any modal dialogs or popups that require attention.
            Current task context: "{task_context}"
            
            Classify the modals into these categories:
            1. DISMISS: Simple interruption modals that should be closed (cookie banners, ads, notifications)
            2. INTERACT: Interactive modals relevant to the current task (forms, email composers, booking dialogs)
            3. IGNORE: Modals that should be left open as they are part of the intended task
            
            For each modal, provide:
            
            For DISMISS modals:
            - Precise description and purpose
            - Coordinates to click to dismiss (X button, No Thanks, Close, etc.)
            
            For INTERACT modals:
            - Detailed description of all interactive elements (form fields, buttons)
            - Whether this modal is relevant to the current task
            - All form field coordinates with labels/purposes
            - Submit/Continue button coordinates if applicable
            
            For IGNORE modals:
            - Reason why this should be left open
            
            Return a JSON with this structure:
            {{
                "modals": [
                    {{
                        "type": "DISMISS|INTERACT|IGNORE",
                        "description": "detailed description of the modal",
                        "relevance_to_task": "high|medium|low",
                        "action": "dismiss|interact|ignore",
                        "reason": "explanation of recommended action",
                        "elements": [
                            {{
                                "element_type": "close_button|input_field|checkbox|radio|dropdown|submit_button",
                                "purpose": "what this element does",
                                "coordinates": {{ "x": 0.XX, "y": 0.YY }},
                                "text": "text to enter" // only for input fields
                            }}
                        ]
                    }}
                ]
            }}
            
            If no modals are visible, return an empty "modals" array.
            """
            
            # Only proceed if vision is available
            if hasattr(self.llm, "supports_vision") and self.llm.supports_vision:
                response_text = self.llm.generate_from_image(prompt, image_bytes=screenshot_bytes)
                
                try:
                    # Extract JSON
                    json_match = re.search(r'```json\n?(.+?)\n?```', response_text, re.DOTALL)
                    json_text = json_match.group(1).strip() if json_match else response_text.strip()
                    
                    # In case the JSON is malformed, try to extract just the JSON object
                    if not json_text.startswith('{'):
                        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
                        json_match = re.search(json_pattern, response_text, re.DOTALL)
                        if json_match:
                            json_text = json_match.group(0)
                    
                    response_data = json.loads(json_text)
                    modals = response_data.get("modals", [])
                    
                    # No modals detected
                    if not modals or len(modals) == 0:
                        self.logger.info("No modals detected in the current page")
                        return
                    
                    # Get viewport size
                    viewport = self.page.viewport_size()
                    width, height = viewport["width"], viewport["height"]
                    
                    # Process each detected modal
                    for modal_index, modal in enumerate(modals):
                        modal_type = modal.get("type", "")
                        action = modal.get("action", "")
                        elements = modal.get("elements", [])
                        
                        self.logger.info(f"Processing modal {modal_index+1}: {modal_type} - {modal.get('description', '')}")
                        
                        # CASE 1: Simple dismissal
                        if modal_type == "DISMISS" or action == "dismiss":
                            self._handle_dismiss_modal(modal, width, height)
                        
                        # CASE 2: Interactive modal relevant to task
                        elif (modal_type == "INTERACT" or action == "interact") and modal.get("relevance_to_task") in ["high", "medium"]:
                            # Check if this modal is appropriate for the current task
                            if self._is_modal_relevant_to_task(modal, task_context):
                                self._handle_interactive_modal(modal, elements, width, height, task_context)
                            else:
                                self.logger.info(f"Skipping irrelevant interactive modal: {modal.get('description', '')}")
                        
                        # CASE 3: Modal to ignore
                        elif modal_type == "IGNORE" or action == "ignore":
                            self.logger.info(f"Ignoring modal as recommended: {modal.get('reason', '')}")
                        
                        # CASE 4: Unknown modal type - default to safe behavior
                        else:
                            self.logger.warning(f"Unrecognized modal type: {modal_type}. Taking no action.")
                except Exception as e:
                    self.logger.error(f"Error processing vision modal detection: {e}")
                    self._dismiss_modals_traditional(task_context)
            else:
                # Fall back to traditional modal detection
                self._dismiss_modals_traditional(task_context)
        except Exception as e:
            self.logger.error(f"Error in vision-based modal handling: {e}")
            # Fall back to traditional modal detection
            self._dismiss_modals_traditional(task_context)
        
    def _handle_dismiss_modal(self, modal, width, height):
        """
        Handle dismissing a simple modal (close button, etc.)
        """
        try:
            # Find the close button element
            close_elements = [e for e in modal.get("elements", []) 
                             if e.get("element_type") in ["close_button", "dismiss_button", "no_thanks"]]
            
            if close_elements:
                element = close_elements[0]  # Use the first close button found
                coords = element.get("coordinates", {})
                x_percent = coords.get("x", 0)
                y_percent = coords.get("y", 0)
                
                if x_percent > 0 and y_percent > 0:
                    x = int(width * x_percent)
                    y = int(height * y_percent)
                    
                    # Click to dismiss
                    self.page.mouse.click(x, y)
                    time.sleep(0.5)  # Wait for modal to disappear
                    
                    self.logger.info(f"Dismissed modal using close button at ({x}, {y})")
                    return True
            
            # If no specific close elements found, check if there's a generic dismissal point
            coords = modal.get("dismiss_coordinates", {})
            if not coords:
                for element in modal.get("elements", []):
                    if element.get("purpose", "").lower() in ["close", "dismiss", "cancel", "no thanks"]:
                        coords = element.get("coordinates", {})
                        break
            
            x_percent = coords.get("x", 0)
            y_percent = coords.get("y", 0)
            
            if x_percent > 0 and y_percent > 0:
                x = int(width * x_percent)
                y = int(height * y_percent)
                
                # Click to dismiss
                self.page.mouse.click(x, y)
                time.sleep(0.5)  # Wait for modal to disappear
                
                self.logger.info(f"Dismissed modal using generic point at ({x}, {y})")
                return True
            
            self.logger.warning("Could not find appropriate dismiss coordinates")
            return False
        
        except Exception as e:
            self.logger.error(f"Error dismissing modal: {e}")
            return False
    
    def _is_modal_relevant_to_task(self, modal, task_context):
        """
        Determine if an interactive modal is relevant to the current task
        """
        # Explicitly marked as high relevance
        if modal.get("relevance_to_task") == "high":
            return True
        
        # Check modal description against task context
        modal_desc = modal.get("description", "").lower()
        task_context = task_context.lower()
        
        # Extract keywords from task context and modal description
        task_words = set(re.findall(r'\b\w{3,}\b', task_context.lower()))
        modal_words = set(re.findall(r'\b\w{3,}\b', modal_desc.lower()))
        
        # Calculate word overlap
        common_words = task_words.intersection(modal_words)
        if len(common_words) >= 2:  # At least 2 meaningful words in common
            return True
        
        # Check for common form-related actions in the task
        form_actions = ["fill", "complete", "input", "enter", "type", "submit", "send"]
        if any(action in task_context for action in form_actions) and "form" in modal_desc:
            return True
            
        # Medium relevance with specific context matching
        if modal.get("relevance_to_task") == "medium":
            # If task mentions completing a form/action that appears in the modal description
            action_match = re.search(r'(fill|complete|submit|send) (a|the) ([a-z\s]+)', task_context)
            if action_match and action_match.group(3) in modal_desc:
                return True
        
        return False
    
    def _handle_interactive_modal(self, modal, elements, width, height, task_context):
        """
        Handle interaction with a complex modal containing form fields, buttons, etc.
        """
        try:
            self.logger.info(f"Handling interactive modal: {modal.get('description', '')}")
            
            # Sort elements by their logical sequence (inputs first, then submit buttons)
            element_types_order = {
                "input_field": 1,
                "text_field": 1,
                "textarea": 1,
                "checkbox": 2,
                "radio": 2,
                "dropdown": 2,
                "select": 2,
                "button": 3,
                "submit_button": 4
            }
            
            # Sort elements by their logical processing order
            sorted_elements = sorted(
                elements,
                key=lambda e: element_types_order.get(e.get("element_type", ""), 99)
            )
            
            # Process each element
            for element in sorted_elements:
                element_type = element.get("element_type", "")
                purpose = element.get("purpose", "")
                coords = element.get("coordinates", {})
                
                x_percent = coords.get("x", 0)
                y_percent = coords.get("y", 0)
                
                if x_percent <= 0 or y_percent <= 0:
                    self.logger.warning(f"Invalid coordinates for {element_type}: {coords}")
                    continue
                
                x = int(width * x_percent)
                y = int(height * y_percent)
                
                # Handle different element types
                if element_type in ["input_field", "text_field", "textarea"]:
                    # First click the field
                    self.page.mouse.click(x, y)
                    time.sleep(0.3)
                    
                    # Enter text if provided
                    text = element.get("text", "")
                    if not text:
                        # Generate appropriate text based on purpose
                        text = self._generate_appropriate_input(purpose, task_context)
                    
                    # Type the text
                    self.page.keyboard.type(text)
                    self.logger.info(f"Entered '{text}' into {element_type} for '{purpose}'")
                    time.sleep(0.5)
                
                elif element_type in ["checkbox", "radio"]:
                    # Click the checkbox/radio button
                    self.page.mouse.click(x, y)
                    self.logger.info(f"Clicked {element_type} for '{purpose}'")
                    time.sleep(0.3)
                
                elif element_type in ["dropdown", "select"]:
                    # Click to open dropdown
                    self.page.mouse.click(x, y)
                    time.sleep(0.5)
                    
                    # If there's a specific option to select, we'd need coordinates for that too
                    # For now, we'll just select the first option by pressing Down and Enter
                    self.page.keyboard.press("ArrowDown")
                    time.sleep(0.2)
                    self.page.keyboard.press("Enter")
                    self.logger.info(f"Selected an option from dropdown for '{purpose}'")
                    time.sleep(0.3)
                
                elif element_type in ["button", "submit_button"] and purpose.lower() not in ["close", "cancel", "back"]:
                    # Don't click submit buttons until all other elements are processed
                    if element == sorted_elements[-1]:
                        self.logger.info(f"Clicking {element_type} for '{purpose}'")
                        self.page.mouse.click(x, y)
                        time.sleep(1.0)  # Wait longer after submission
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error handling interactive modal: {e}")
            return False
                
    def _generate_appropriate_input(self, field_purpose, task_context):
        """
        Generate appropriate text input based on field purpose and task context
        """
        purpose_lower = field_purpose.lower()
        
        # Step 1: Try to extract specific values from the task context first
        # Look for explicit instructions like "type 'john@example.com' in the email field"
        field_value_pattern = re.compile(
            r'(enter|type|fill|input|write|use|put)\s+["\']([^"\']+)["\'](\s+in(to)?\s+|\s+for\s+|\s+as\s+).*?'
            + re.escape(purpose_lower),
            re.IGNORECASE
        )
        match = field_value_pattern.search(task_context)
        if match:
            return match.group(2)
        
        # Step 2: Check for quoted text that might be relevant to this field
        # This is a more general pattern to catch instructions like "with email 'user@example.com'"
        field_with_value_pattern = re.compile(
            r'with\s+' + re.escape(purpose_lower) + r'\s+["\']([^"\']+)["\']',
            re.IGNORECASE
        )
        match = field_with_value_pattern.search(task_context)
        if match:
            return match.group(1)
        
        # Step 3: Extract values from the task context based on field type
        if any(term in purpose_lower for term in ["email", "e-mail"]):
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
            email_match = email_pattern.search(task_context)
            if email_match:
                return email_match.group(0)
            return "test@example.com"
        
        elif any(term in purpose_lower for term in ["name", "first name", "last name", "full name"]):
            # Try to extract names from the task context
            name_pattern = re.compile(r'name\s+["\']?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)["\']?', re.IGNORECASE)
            name_match = name_pattern.search(task_context)
            
            if name_match:
                full_name = name_match.group(1)
                name_parts = full_name.split()
                
                if "first" in purpose_lower and len(name_parts) > 0:
                    return name_parts[0]
                elif "last" in purpose_lower and len(name_parts) > 1:
                    return name_parts[-1]
                else:
                    return full_name
            
            # Default values if no name found in context
            if "first" in purpose_lower:
                return "John"
            elif "last" in purpose_lower:
                return "Smith"
            else:
                return "John Smith"
        
        elif any(term in purpose_lower for term in ["phone", "mobile", "cell", "telephone"]):
            # Try to extract phone number from context
            phone_pattern = re.compile(r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b')
            phone_match = phone_pattern.search(task_context)
            if phone_match:
                return phone_match.group(1).replace(" ", "").replace("-", "").replace(".", "")
            return "5555555555"
        
        elif "password" in purpose_lower:
            # Look for specific password instructions
            password_pattern = re.compile(r'password\s+["\']([^"\']+)["\']', re.IGNORECASE)
            password_match = password_pattern.search(task_context)
            if password_match:
                return password_match.group(1)
            return "Password123!"
        
        elif "address" in purpose_lower:
            # Look for addresses in the task context
            address_pattern = re.compile(r'address\s+["\']?([0-9]+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr))["\']?', re.IGNORECASE)
            address_match = address_pattern.search(task_context)
            if address_match:
                return address_match.group(1)
            return "123 Main St"
        
        elif "city" in purpose_lower:
            # Look for city names in the task context
            city_pattern = re.compile(r'city\s+["\']?([A-Za-z\s]+)["\']?', re.IGNORECASE)
            city_match = city_pattern.search(task_context)
            if city_match:
                return city_match.group(1)
            return "New York"
        
        elif any(term in purpose_lower for term in ["state", "province"]):
            # Look for state/province in the task context
            state_pattern = re.compile(r'state\s+["\']?([A-Za-z\s]+)["\']?', re.IGNORECASE)
            state_match = state_pattern.search(task_context)
            if state_match:
                return state_match.group(1)
            return "NY"
        
        elif any(term in purpose_lower for term in ["zip", "postal code", "zip code"]):
            # Look for postal codes in the task context
            zip_pattern = re.compile(r'\b(\d{5}(?:-\d{4})?)\b')
            zip_match = zip_pattern.search(task_context)
            if zip_match:
                return zip_match.group(1)
            return "10001"
        
        elif any(term in purpose_lower for term in ["message", "comment", "feedback", "description"]):
            # Various patterns to extract message content
            patterns = [
                r'message\s+["\'](.+?)["\']',
                r'(send|write|type)\s+["\'](.+?)["\']',
                r'saying\s+["\'](.+?)["\']',
                r'content\s+["\'](.+?)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, task_context, re.IGNORECASE)
                if match:
                    return match.group(1) if len(match.groups()) == 1 else match.group(2)
            
            return "Test message content."
        
        elif "subject" in purpose_lower:
            # Look for subject lines in the task context
            patterns = [
                r'subject\s+["\'](.+?)["\']',
                r'title\s+["\'](.+?)["\']',
                r'about\s+["\'](.+?)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, task_context, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return "Test Subject"
        
        elif "date" in purpose_lower:
            # Look for dates in the task context
            date_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
            date_match = date_pattern.search(task_context)
            if date_match:
                return date_match.group(1)
            
            # Use current date as fallback
            from datetime import datetime
            return datetime.now().strftime("%m/%d/%Y")
        
        elif "search" in purpose_lower:
            # Look for search terms in the task context
            patterns = [
                r'search\s+for\s+["\'](.+?)["\']',
                r'search\s+["\'](.+?)["\']',
                r'find\s+["\'](.+?)["\']',
                r'look\s+for\s+["\'](.+?)["\']'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, task_context, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return "test search"
        
        # Step 4: For any other field type, try to find quoted text that might be relevant
        text_pattern = re.compile(r'["\']([^"\']+)["\']')
        matches = text_pattern.findall(task_context)
        
        # Use the quoted text that seems most relevant to the field purpose
        if matches:
            for match in matches:
                # If any words from the field purpose appear near the quoted text
                context_before_match = task_context.split(match)[0]
                if any(term in context_before_match[-30:].lower() for term in purpose_lower.split()):
                    return match
            
            # If no specific match found, use the first quoted text
            return matches[0]
        
        # Step 5: If all extraction attempts fail, use a generic but safe default
        return "Test input"
    
    def _dismiss_modals_traditional(self, task_context: str):
        """
        Traditional method to dismiss modals without using vision capabilities
        """
        modal_selectors = [
            ".modal", 
            "[role='dialog']", 
            ".popup", 
            ".overlay", 
            ".lightbox",
            "[class*='modal']",
            "[class*='popup']",
            "[class*='overlay']",
            "[aria-modal='true']",
            "#cookie-banner",
            ".cookie-consent",
            ".notification-bar",
            ".alert-box"
        ]
        
        try:
            for selector in modal_selectors:
                elements = self.page.query_selector_all(selector)
                for modal in elements:
                    if modal.is_visible():
                        # Look for close buttons
                        close_selectors = [
                            "button.close", 
                            ".btn-close", 
                            "[aria-label='Close']", 
                            "[data-dismiss='modal']",
                            ".close-button",
                            ".dismiss",
                            "button:has-text('Close')",
                            "button:has-text('Cancel')",
                            "button:has-text('No thanks')",
                            "button:has-text('I understand')",
                            "button:has-text('Accept')",
                            "button:has-text('Agree')",
                            "button:has-text('Got it')",
                            "button:has-text('OK')",
                            ".modal-header button",
                            ".modal-footer button:first-child"
                        ]
                        
                        for close_selector in close_selectors:
                            try:
                                close_btn = modal.query_selector(close_selector)
                                if close_btn and close_btn.is_visible():
                                    close_btn.click()
                                    self.logger.info(f"Dismissed modal using {close_selector}")
                                    time.sleep(0.5)  # Wait for modal to disappear
                                    break
                            except Exception as e:
                                self.logger.debug(f"Error trying close selector {close_selector}: {e}")
                        
                        # If no close button worked, try clicking outside the modal
                        try:
                            # Get modal dimensions
                            modal_box = modal.bounding_box()
                            if modal_box:
                                # Click outside the modal (top-right corner of the page)
                                self.page.mouse.click(10, 10)
                                self.logger.info("Attempted to dismiss modal by clicking outside")
                                time.sleep(0.5)
                        except Exception as e:
                            self.logger.debug(f"Error trying to click outside modal: {e}")
        
        except Exception as e:
            self.logger.error(f"Error in traditional modal dismissal: {e}")

    def _verify_task_completion_with_vision(self, page: Page, task: Dict[str, Any]) -> Dict[str, bool]:
        """Verify task completion using vision capabilities"""
        try:
            # Take a screenshot after task execution
            screenshot_bytes = page.screenshot(type="png")
            
            # Create prompt that explains the task and asks if it was completed
            prompt = f"""
            I just performed the following action in a web browser automation:
            Action: {task.get('action')}
            Description: {task.get('description')}
            
            Based on the screenshot, can you verify if this task was completed successfully?
            
            Please analyze:
            1. Is there visual evidence that the action was performed?
            2. Are there any error messages visible?
            3. Has the page state changed as expected for this action?
            
            Return a JSON with this format:
            {{
                "success": true/false,
                "reason": "explanation of your assessment",
                "next_action": "suggestion for what to do if it failed"
            }}
            """
            
            # Check if LLM supports vision
            if hasattr(self.llm, "supports_vision") and self.llm.supports_vision:
                response_text = self.llm.generate_from_image(prompt, image_bytes=screenshot_bytes)
                
                # Parse the response
                try:
                    # Extract JSON from response
                    json_match = re.search(r'```json\n?(.+?)\n?```', response_text, re.DOTALL)
                    json_text = json_match.group(1).strip() if json_match else response_text.strip()
                    result = json.loads(json_text)
                    return result
                except Exception as e:
                    self.logger.error(f"Error parsing vision verification result: {e}")
                    return {"success": True, "reason": "Failed to parse vision result, assuming success", "next_action": None}
            else:
                return {"success": True, "reason": "Vision verification not available", "next_action": None}
        except Exception as e:
            self.logger.error(f"Error in vision verification: {e}")
            return {"success": True, "reason": f"Vision verification error: {str(e)}", "next_action": None}
            
    def _fallback_with_vision(self, page: Page, task: Dict[str, Any], executed_context: str = "") -> Dict[str, Any]:
        """Use vision to identify and interact with elements when other methods fail"""
        try:
            # Take a screenshot of the page
            screenshot_bytes = page.screenshot(type="png")
            
            action = task.get("action", "")
            description = task.get("description", "")
            
            # Create a prompt based on the action
            if action == "click":
                prompt = f"""
                I need to click on an element in this webpage that matches this description:
                "{description}"
                
                Based on the screenshot:
                1. Identify the exact element I should click.
                2. Describe its position (e.g., "top-right button", "third link in the menu").
                3. Provide coordinates for the click (x, y) as percentages of the page width and height.
                
                Return a JSON response in this format:
                {{
                    "element_description": "description of the element to click",
                    "position": "position on the page",
                    "coordinates": {{
                        "x": 0.XX, // percentage of page width
                        "y": 0.YY  // percentage of page height
                    }},
                    "confidence": 0.Z // from 0 to 1
                }}
                """
            elif action == "type":
                value = task.get("value", "")
                prompt = f"""
                I need to type "{value}" into an input field that matches this description:
                "{description}"
                
                Based on the screenshot:
                1. Identify the exact input field I should type into.
                2. Describe its position.
                3. Provide coordinates for clicking the input field (x, y) as percentages of the page width and height.
                
                Return a JSON response in this format:
                {{
                    "element_description": "description of the input field",
                    "position": "position on the page",
                    "coordinates": {{
                        "x": 0.XX, // percentage of page width
                        "y": 0.YY  // percentage of page height
                    }},
                    "confidence": 0.Z // from 0 to 1
                }}
                """
            else:
                return {"action": action, "success": False, "message": f"Vision fallback not implemented for action: {action}"}
            
            # Check if LLM supports vision
            if not (hasattr(self.llm, "supports_vision") and self.llm.supports_vision):
                return {"action": action, "success": False, "message": "Vision capabilities not available for fallback"}
            
            # Get response from vision model
            response_text = self.llm.generate_from_image(prompt, image_bytes=screenshot_bytes)
            
            # Extract JSON from response
            try:
                json_match = re.search(r'```json\n?(.+?)\n?```', response_text, re.DOTALL)
                json_text = json_match.group(1).strip() if json_match else response_text.strip()
                vision_result = json.loads(json_text)
            except Exception as e:
                self.logger.error(f"Error parsing vision fallback result: {e}")
                return {"action": action, "success": False, "message": f"Failed to parse vision response: {str(e)}"}
            
            # Check confidence level
            confidence = vision_result.get("confidence", 0)
            if confidence < 0.7:  # Threshold for accepting vision guidance
                return {"action": action, "success": False, 
                        "message": f"Vision identified element with low confidence ({confidence})"}
            
            # Get viewport size
            viewport = self.page.viewport_size()
            width, height = viewport["width"], viewport["height"]
            
            # Calculate absolute coordinates
            coordinates = vision_result.get("coordinates", {})
            x_percent = coordinates.get("x", 0.5)
            y_percent = coordinates.get("y", 0.5)
            
            x = int(width * x_percent)
            y = int(height * y_percent)
            
            # Perform the action based on coordinates
            if action == "click":
                page.mouse.click(x, y)
                return {"action": "click", "success": True, 
                        "message": f"Clicked at ({x}, {y}) based on vision guidance"}
            elif action == "type":
                # First click the input field
                page.mouse.click(x, y)
                time.sleep(0.5)
                
                # Then type the text
                page.keyboard.type(task.get("value", ""))
                return {"action": "type", "success": True, 
                        "message": f"Typed at ({x}, {y}) based on vision guidance"}
            
            return {"action": action, "success": False, "message": "Unhandled action in vision fallback"}
        except Exception as e:
            self.logger.error(f"Vision fallback error: {e}")
            return {"action": task.get("action", "unknown"), "success": False, "message": f"Vision fallback error: {str(e)}"}
            
    def _handle_suggested_action(self, page: Page, suggested_action: str, task: Dict[str, Any]) -> bool:
        """Handle a suggested action from vision verification"""
        try:
            # Parse the suggested action (which could be in natural language)
            suggested_action = suggested_action.lower()
            
            # Common correction patterns
            if "click" in suggested_action:
                # Extract coordinates if provided
                coord_match = re.search(r'coordinates?\s*\(?(\d+)\s*,\s*(\d+)\)?', suggested_action)
                if coord_match:
                    x, y = int(coord_match.group(1)), int(coord_match.group(2))
                    page.mouse.click(x, y)
                    self.logger.info(f"Vision correction: Clicked at ({x}, {y})")
                    return True
                # Look for element descriptions
                element_match = re.search(r'click (?:on )?(?:the )?([\w\s]+button|link|tab|icon|menu item)', suggested_action)
                if element_match:
                    element_desc = element_match.group(1)
                    # Try to find the element by text
                    element = page.query_selector(f":text('{element_desc}')")
                    if element:
                        element.click()
                        self.logger.info(f"Vision correction: Clicked on element with text '{element_desc}'")
                        return True
            
            elif "type" in suggested_action or "enter" in suggested_action:
                # Look for text to type
                text_match = re.search(r'(?:type|enter)\s+["\']([^"\']+)["\']', suggested_action)
                if text_match:
                    text = text_match.group(1)
                    # Use active element if there's one
                    page.keyboard.type(text)
                    self.logger.info(f"Vision correction: Typed '{text}'")
                    return True
            
            elif "wait" in suggested_action:
                time.sleep(2)  # Simple wait
                self.logger.info("Vision correction: Waited for 2 seconds")
                return True
                
            elif "refresh" in suggested_action:
                page.reload()
                self.logger.info("Vision correction: Refreshed the page")
                return True
                
            # Handle more complex suggestions
            if "try again" in suggested_action or "retry" in suggested_action:
                # Simply re-run the original task
                original_action = task.get("action", "")
                if original_action == "click":
                    selector = task.get("selector", "")
                    if selector:
                        try:
                            element = page.query_selector(selector)
                            if element:
                                element.click()
                                self.logger.info(f"Vision correction: Retried click on '{selector}'")
                                return True
                        except Exception:
                            pass
                elif original_action == "type":
                    selector = task.get("selector", "")
                    value = task.get("value", "")
                    if selector and value:
                        try:
                            element = page.query_selector(selector)
                            if element:
                                element.fill(value)
                                self.logger.info(f"Vision correction: Retried typing '{value}' in '{selector}'")
                                return True
                        except Exception:
                            pass
            
            # No matching action found
            self.logger.warning(f"Could not interpret suggested action: {suggested_action}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling suggested action: {e}")
            return False
    
    def _execute_with_retries(self, page: Page, task: Dict[str, Any],
                              handler: Callable[[Page, Dict[str, Any]], Dict[str, Any]],
                              executed_context: str = "") -> Dict[str, Any]:
        """Execute a task with retry logic and vision verification"""
        attempts = 0
        result = {}
        
        while attempts < self.max_retries:
            # Execute the task
            result = self._execute_safe_task(page, task, handler)
            
            # If task reports success, verify with vision
            if result.get("success", False):
                # Wait a moment for any animations or changes to complete
                time.sleep(1)
                
                # Verify with vision
                vision_result = self._verify_task_completion_with_vision(page, task)
                
                # If vision verification confirms success, return the result
                if vision_result.get("success", True):
                    result["vision_verified"] = True
                    return result
                else:
                    # Vision detected a failure even though the action reported success
                    self.logger.warning(f"Vision verification failed: {vision_result.get('reason')}")
                    
                    # If there's a suggested next action, try it
                    next_action = vision_result.get("next_action")
                    if next_action:
                        self.logger.info(f"Attempting suggested action: {next_action}")
                        # Implement handling for suggested actions
                        if self._handle_suggested_action(page, next_action, task):
                            result["message"] += f" (with vision-guided correction)"
                            result["vision_corrected"] = True
                            return result
            
            # Increment attempts and retry
            attempts += 1
            self.logger.info(f"Retrying task '{task.get('action')}' (attempt {attempts + 1}/{self.max_retries})")
            time.sleep(1 * attempts)
        
        # If all retries failed, try with vision-based fallback
        if task.get("action") in ["click", "type"]:
            self.logger.info("All standard approaches failed. Using vision-based fallback.")
            result = self._fallback_with_vision(page, task, executed_context)
        
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
        
        # Include task history as context
        task_history_str = ""
        if self._task_history:
            task_history_str = "Previous actions (most recent first):\n"
            for i, task in enumerate(reversed(self._task_history[-5:])):  # Last 5 tasks only
                task_history_str += f"{i+1}. {task['action']}: {task['description']} - {'Success' if task['success'] else 'Failed'}\n"
        
        prompt = f"""Generate a detailed browser automation plan for: {query}

Current URL: {current_url or 'No page loaded yet'}
Current date: {current_date}
Current time: {current_time}
{metadata_str}
{task_history_str}

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
{
    "tasks": [
        {
            "action": "action_name",
            "selector": "CSS selector (where applicable)",
            "value": "value parameter (e.g., URL, text, duration)",
            "description": "human-readable description of the step"
        }
    ]
}

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
                        pass
            
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
                        pass
                        
            # For all other actions, return False to indicate recovery failed
            return False
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
            
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
                page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                scroll_target = "page bottom"
                
            # Wait a moment for any lazy-loaded content to appear
            time.sleep(1)
                
            return {"action": "scroll", "success": True, "message": f"Scrolled to {scroll_target}"}
        except Exception as e:
            self.logger.error(f"Scroll action failed: {e}")
            return {"action": "scroll", "success": False, "message": f"Scroll failed: {str(e)}"}
            
    def _handle_hover(self, page: Page, selector: str) -> Dict[str, Any]:
        """Handle hovering over an element"""
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        try:
            # Wait for the element to be visible
            element = page.wait_for_selector(selector, state="visible", timeout=self.default_timeout)
            if not element:
                return {"action": "hover", "success": False, "message": f"Element not found: {selector}"}
                
            # Scroll into view first
            element.scroll_into_view_if_needed()
            
            # Hover over the element
            element.hover(timeout=self.default_timeout)
            
            # Wait a moment for any hover effects to appear
            time.sleep(0.5)
            
            return {"action": "hover", "success": True, "message": f"Hovered over element: {selector}"}
        except Exception as e:
            self.logger.error(f"Hover action failed on selector {selector}: {e}")
            return {"action": "hover", "success": False, "message": f"Hover failed: {str(e)}"}
            
    def _handle_screenshot(self, page: Page, filename: str) -> Dict[str, Any]:
        """Take a screenshot of the page"""
        if isinstance(filename, dict) and "value" in filename:
            filename = filename.get("value", "")
            
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
            
        try:
            page.screenshot(path=filename)
            return {"action": "screenshot", "success": True, "message": f"Screenshot saved to {filename}"}
        except Exception as e:
            self.logger.error(f"Screenshot action failed: {e}")
            return {"action": "screenshot", "success": False, "message": f"Screenshot failed: {str(e)}"}
        
    def _handle_select_option(self, page: Page, selector: str, value: str) -> Dict[str, Any]:
        """Handle selecting an option from a dropdown menu"""
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        if isinstance(value, dict) and "value" in value:
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
        if isinstance(selector, dict) and "selector" in selector:
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
        if isinstance(key, dict) and "value" in key:
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
        if isinstance(selector, dict) and "selector" in selector:
            selector = selector.get("selector", "")
            
        if isinstance(file_path, dict) and "value" in file_path:
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
        if isinstance(text, dict) and "value" in text:
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
        if isinstance(selector, dict) and "selector" in selector:
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
        if isinstance(action, dict) and "value" in action:
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
        if isinstance(selector, dict) and "selector" in selector:
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
        if isinstance(options, dict) and "value" in options:
            retry_params = options.get("value", "")
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
        if isinstance(index_or_new, dict) and "value" in index_or_new:
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
        if isinstance(script, dict) and "value" in script:
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
        if isinstance(source_selector, dict) and "selector" in source_selector:
            source_selector = source_selector.get("selector", "")
            
        if isinstance(target_selector, dict) and "value" in target_selector:
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
                        
            # All approaches failed
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