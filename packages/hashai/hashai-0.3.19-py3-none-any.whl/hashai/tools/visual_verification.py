import time
import json
import re
import logging
from typing import Dict, Any, Tuple, List, Optional
from playwright.sync_api import Page

class VisualVerification:
    """
    A system that uses vision-based LLM capabilities to verify task completion
    and suggest corrective actions when tasks fail.
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def verify_task(self, page: Page, task: Dict[str, Any], llm: Any, 
                    max_correction_attempts: int = 3) -> Dict[str, Any]:
        """
        Visually verify if a task was completed successfully using LLM vision capabilities.
        Can automatically attempt corrections if the task was not completed.
        
        Args:
            page: The Playwright page object
            task: The task that was attempted (with action, selector, value, description)
            llm: The LLM instance with vision capabilities
            max_correction_attempts: Maximum number of correction attempts
            
        Returns:
            Dict with verification results including success status and any corrections made
        """
        result = {
            "verified": False,
            "original_task": task,
            "corrections_attempted": 0,
            "corrections_succeeded": False,
            "message": ""
        }
        
        # Take a screenshot of the current page state
        try:
            for attempt in range(max_correction_attempts + 1):  # +1 for initial verification
                # If this is a correction attempt, log it
                if attempt > 0:
                    self.logger.info(f"Attempting correction #{attempt} for task: {task.get('description', task.get('action', ''))}")
                    result["corrections_attempted"] += 1
                
                # Capture the current page state
                screenshot = page.screenshot()
                
                # Generate verification prompt
                prompt = self._create_verification_prompt(task, attempt > 0)
                
                # Send to LLM with vision capabilities
                try:
                    if hasattr(llm, "supports_vision") and llm.supports_vision:
                        response = llm.generate_from_image(prompt, image_bytes=screenshot)
                    else:
                        # Fall back to text-only if vision not available
                        page_content = page.content()
                        fallback_prompt = f"{prompt}\n\nHTML content (partial):\n{page_content[:5000]}..."
                        response = llm.generate(prompt=fallback_prompt)
                        
                    self.logger.info(f"Verification response received (length: {len(response)})")
                    
                    # Parse the verification response
                    verification_result = self._parse_verification_response(response)
                    
                    # If task is verified as complete, we're done
                    if verification_result.get("status") == "completed":
                        result["verified"] = True
                        result["message"] = verification_result.get("reason", "Task appears to be completed successfully.")
                        return result
                    
                    # If this was the last attempt, return the final result
                    if attempt == max_correction_attempts:
                        result["message"] = verification_result.get("reason", "Task verification failed after correction attempts.")
                        return result
                    
                    # Otherwise, attempt the suggested correction
                    correction = verification_result.get("correction", {})
                    if correction and correction.get("action"):
                        correction_success = self._apply_correction(page, correction)
                        if correction_success:
                            self.logger.info(f"Applied correction: {correction.get('action')} - {correction.get('description', '')}")
                            # If this was the last planned correction and it succeeded,
                            # do one final verification
                            if attempt == max_correction_attempts - 1:
                                # Quick wait to let any effects take place
                                time.sleep(1)
                                
                                # Take a final screenshot
                                final_screenshot = page.screenshot()
                                final_prompt = self._create_verification_prompt(task, False)
                                
                                if hasattr(llm, "supports_vision") and llm.supports_vision:
                                    final_response = llm.generate_from_image(final_prompt, image_bytes=final_screenshot)
                                else:
                                    page_content = page.content()
                                    fallback_prompt = f"{final_prompt}\n\nHTML content (partial):\n{page_content[:5000]}..."
                                    final_response = llm.generate(prompt=fallback_prompt)
                                
                                final_result = self._parse_verification_response(final_response)
                                if final_result.get("status") == "completed":
                                    result["verified"] = True
                                    result["corrections_succeeded"] = True
                                    result["message"] = "Task completed after corrections."
                        else:
                            self.logger.warning(f"Correction failed: {correction.get('action')} - {correction.get('description', '')}")
                    else:
                        self.logger.warning("No valid correction suggested by LLM")
                        # If no correction was suggested, break the loop
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error during verification: {e}")
                    result["message"] = f"Verification error: {str(e)}"
                    return result
            
            return result
                
        except Exception as e:
            self.logger.error(f"Error in visual verification: {e}")
            result["message"] = f"Verification system error: {str(e)}"
            return result
    
    def _create_verification_prompt(self, task: Dict[str, Any], is_correction: bool = False) -> str:
        """Create a prompt for the vision LLM to verify the task completion"""
        action = task.get("action", "unknown").lower()
        selector = task.get("selector", "")
        value = task.get("value", "")
        description = task.get("description", f"Perform {action} on {selector}")
        
        if is_correction:
            prompt = f"""TASK VERIFICATION AND CORRECTION

I previously attempted to: {description}

Action: {action}
Selector: {selector}
Value: {value}

Based on the screenshot of the current page state, please verify if the task has been completed successfully.

Answer these questions:
1. Has the task been completed? (Look for visual evidence)
2. If not completed, what specifically indicates failure?
3. What would be the best SPECIFIC corrective action?

Return your analysis in this JSON format:
{{
  "status": "completed" or "failed",
  "reason": "detailed explanation of your determination",
  "correction": {{
    "action": "click" or "type" or "scroll" or other specific action,
    "selector": "very specific way to identify the element",
    "value": "any text to input if applicable",
    "description": "clear explanation of what this correction does"
  }}
}}

If the task is completed, the correction field can be empty. Be very specific with selectors in corrections.
"""
        else:
            prompt = f"""TASK VERIFICATION

I attempted to: {description}

Action: {action}
Selector: {selector}
Value: {value}

Based on the screenshot of the current page state, please verify if the task has been completed successfully.

Look for visual confirmation such as:
- For click actions: The expected result of the click (like a modal opened, menu expanded, page changed)
- For type actions: The text appears in the field
- For navigation: The correct page has loaded
- For form submissions: Success messages or expected redirects

Return your analysis in this JSON format:
{{
  "status": "completed" or "failed",
  "reason": "detailed explanation of your determination",
  "correction": {{
    "action": "click" or "type" or "scroll" or other specific action,
    "selector": "very specific way to identify the element",
    "value": "any text to input if applicable",
    "description": "clear explanation of what this correction does"
  }}
}}

If the task is completed, the correction field can be empty. Be very specific with selectors in corrections.
"""
        return prompt
    
    def _parse_verification_response(self, response: str) -> Dict[str, Any]:
        """Extract the verification result from the LLM response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'```json\n?(.+?)\n?```', response, re.DOTALL)
            if json_match:
                json_text = json_match.group(1).strip()
            else:
                # Try to find JSON object
                json_pattern = r'\{[\s\S]*"status"[\s\S]*\}'
                json_match = re.search(json_pattern, response, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    return {
                        "status": "failed",
                        "reason": "Could not parse verification response. No valid JSON found."
                    }
            
            # Parse the JSON
            result = json.loads(json_text)
            
            # Validate required fields
            if "status" not in result:
                result["status"] = "failed"
                result["reason"] = "Missing status field in verification response"
                
            return result
            
        except Exception as e:
            return {
                "status": "failed",
                "reason": f"Error parsing verification response: {str(e)}",
                "correction": {}
            }
    
    def _apply_correction(self, page: Page, correction: Dict[str, Any]) -> bool:
        """Apply the suggested correction on the page"""
        try:
            action = correction.get("action", "").lower()
            selector = correction.get("selector", "")
            value = correction.get("value", "")
            
            if not action:
                return False
                
            if action == "click":
                if selector:
                    # Try multiple selector finding strategies
                    element = None
                    
                    # 1. Direct CSS selector
                    try:
                        element = page.wait_for_selector(selector, timeout=5000)
                    except:
                        pass
                        
                    # 2. Text content selector
                    if not element and not selector.startswith("#") and not selector.startswith("."):
                        try:
                            text_selector = f"text='{selector}'"
                            element = page.wait_for_selector(text_selector, timeout=3000)
                        except:
                            pass
                    
                    # 3. Using evaluate to find by text content
                    if not element:
                        try:
                            js_result = page.evaluate(f"""
                                () => {{
                                    const targetText = "{selector}";
                                    const elements = Array.from(document.querySelectorAll('button, a, [role="button"], input[type="submit"]'));
                                    const element = elements.find(el => 
                                        (el.innerText && el.innerText.includes(targetText)) ||
                                        (el.textContent && el.textContent.includes(targetText)) ||
                                        (el.value && el.value.includes(targetText)) ||
                                        (el.placeholder && el.placeholder.includes(targetText)) ||
                                        (el.id && el.id.includes(targetText)) ||
                                        (el.name && el.name.includes(targetText))
                                    );
                                    if (!element) return null;
                                    element.scrollIntoView();
                                    const rect = element.getBoundingClientRect();
                                    return {{
                                        x: rect.x + rect.width / 2,
                                        y: rect.y + rect.height / 2,
                                        found: true
                                    }};
                                }}
                            """)
                            
                            if js_result and js_result.get("found"):
                                # Click at the coordinates
                                page.mouse.click(js_result.get("x"), js_result.get("y"))
                                return True
                        except:
                            pass
                    
                    # If element found by any method, click it
                    if element:
                        element.click()
                        return True
                
                return False
                
            elif action == "type":
                if selector and value is not None:
                    element = None
                    
                    # Try to find the input field
                    try:
                        element = page.wait_for_selector(selector, timeout=5000)
                    except:
                        # Try finding by placeholder or label
                        try:
                            js_result = page.evaluate(f"""
                                () => {{
                                    const targetText = "{selector}";
                                    
                                    // Try to find by placeholder
                                    let element = Array.from(document.querySelectorAll('input, textarea'))
                                        .find(el => el.placeholder && el.placeholder.includes(targetText));
                                    
                                    // Try to find by label
                                    if (!element) {{
                                        const labels = Array.from(document.querySelectorAll('label'))
                                            .filter(label => label.textContent.includes(targetText));
                                        
                                        if (labels.length > 0) {{
                                            const forId = labels[0].getAttribute('for');
                                            if (forId) {{
                                                element = document.getElementById(forId);
                                            }}
                                        }}
                                    }}
                                    
                                    // Try to find input near text
                                    if (!element) {{
                                        const textElements = Array.from(document.querySelectorAll('*'))
                                            .filter(el => el.textContent.includes(targetText) && 
                                                   !['INPUT', 'TEXTAREA'].includes(el.tagName));
                                        
                                        for (const textEl of textElements) {{
                                            const nearbyInput = textEl.querySelector('input, textarea') || 
                                                              textEl.nextElementSibling;
                                            if (nearbyInput && 
                                                (nearbyInput.tagName === 'INPUT' || nearbyInput.tagName === 'TEXTAREA')) {{
                                                element = nearbyInput;
                                                break;
                                            }}
                                        }}
                                    }}
                                    
                                    if (!element) return null;
                                    
                                    element.scrollIntoView();
                                    
                                    return {{
                                        id: element.id,
                                        name: element.name,
                                        found: true
                                    }};
                                }}
                            """)
                            
                            if js_result and js_result.get("found"):
                                if js_result.get("id"):
                                    element = page.wait_for_selector(f"#{js_result['id']}")
                                elif js_result.get("name"):
                                    element = page.wait_for_selector(f"[name='{js_result['name']}']")
                        except:
                            pass
                    
                    if element:
                        element.fill(value)
                        return True
                
                return False
                
            elif action == "scroll":
                try:
                    if selector:
                        # Scroll to a specific element
                        element = page.wait_for_selector(selector, timeout=5000)
                        if element:
                            element.scroll_into_view_if_needed()
                            return True
                    else:
                        # Scroll by an amount or to bottom
                        direction = value.lower() if value else "down"
                        if direction == "down" or direction == "bottom":
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        elif direction == "up" or direction == "top":
                            page.evaluate("window.scrollTo(0, 0)")
                        else:
                            # Try to parse numerical value
                            try:
                                scroll_amount = int(value)
                                page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                            except:
                                pass
                        return True
                except:
                    pass
                    
                return False
                
            elif action == "wait":
                try:
                    wait_time = float(value) if value else 2.0
                    time.sleep(wait_time)
                    return True
                except:
                    return False
                    
            elif action == "refresh":
                try:
                    page.reload()
                    return True
                except:
                    return False
                    
            elif action == "press_key":
                try:
                    key = value if value else "Enter"
                    page.keyboard.press(key)
                    return True
                except:
                    return False
                    
            elif action == "execute_script":
                try:
                    if value:
                        page.evaluate(value)
                        return True
                except:
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error applying correction: {e}")
            return False