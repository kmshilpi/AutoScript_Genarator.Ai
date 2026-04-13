from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.logger import setup_logger

logger = setup_logger("SeleniumService")

import threading

class SeleniumService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SeleniumService, cls).__new__(cls)
                cls._instance.driver = None
                cls._instance.steps = []
                cls._instance.is_syncing = False
        return cls._instance

    def _is_browser_alive(self):
        """Check if the existing browser session is still responsive."""
        try:
            # Accessing title will throw if the browser was closed
            _ = self.driver.title
            return True
        except Exception:
            return False

    def start_browser(self):
        if self.driver:
            if self._is_browser_alive():
                # Browser is still open — close it first, then start fresh
                logger.info("Browser already running. Restarting with a fresh session...")
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
            else:
                # Browser was closed manually — clean up stale reference
                logger.info("Stale browser session detected. Cleaning up...")
                self.driver = None
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            logger.info("Browser started successfully")
            return {"status": "success", "message": "Browser started"}
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            self.driver = None
            return {"status": "error", "message": str(e)}

    def stop_browser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        logger.info("Browser stopped")
        return {"status": "success", "message": "Browser stopped"}

    def open_new_tab(self, url: str):
        """Opens a new browser tab and navigates to the given URL."""
        if not self.driver:
            return {"status": "error", "message": "Browser not started"}
        try:
            # Open a new tab via JavaScript
            self.driver.execute_script("window.open('');")
            # Switch to the new tab (last handle)
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[-1])
            # Navigate to the URL
            self.driver.get(url)
            # Inject the recorder on the new tab
            self.inject_recorder_js()
            logger.info(f"Opened new tab and navigated to {url}")
            return {
                "status": "success",
                "message": f"New tab opened: {url}",
                "tab_index": len(handles) - 1,
                "window_handle": handles[-1]
            }
        except Exception as e:
            logger.error(f"Failed to open new tab: {e}")
            return {"status": "error", "message": str(e)}

    def switch_to_tab(self, index: int):
        """Switches Selenium focus to the tab at the given index."""
        if not self.driver:
            return {"status": "error", "message": "Browser not started"}
        try:
            handles = self.driver.window_handles
            if index < 0 or index >= len(handles):
                return {"status": "error", "message": f"Tab index {index} out of range (0-{len(handles)-1})"}
            self.driver.switch_to.window(handles[index])
            current_url = self.driver.current_url
            logger.info(f"Switched to tab {index}: {current_url}")
            return {"status": "success", "message": f"Switched to tab {index}", "url": current_url}
        except Exception as e:
            logger.error(f"Failed to switch tab: {e}")
            return {"status": "error", "message": str(e)}

    def get_tabs(self):
        """Returns info about all open tabs."""
        if not self.driver:
            return {"status": "error", "message": "Browser not started", "tabs": []}
        try:
            handles = self.driver.window_handles
            current_handle = self.driver.current_window_handle
            tabs = []
            for i, handle in enumerate(handles):
                self.driver.switch_to.window(handle)
                tabs.append({
                    "index": i,
                    "window_handle": handle,
                    "url": self.driver.current_url,
                    "title": self.driver.title,
                    "active": handle == current_handle
                })
            # Switch back to the original tab
            self.driver.switch_to.window(current_handle)
            return {"status": "success", "tabs": tabs, "count": len(tabs)}
        except Exception as e:
            logger.error(f"Failed to get tabs: {e}")
            return {"status": "error", "message": str(e), "tabs": []}

    def navigate(self, url: str, inject_recorder: bool = True):
        if not self.driver:
            start_res = self.start_browser()
            if start_res["status"] == "error":
                return start_res
        try:
            if inject_recorder:
                self.inject_recorder_js()
            
            self.driver.get(url)
            self.record_step("navigate", value=url)
            
            return {"status": "success", "message": f"Navigated to {url}"}
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"status": "error", "message": str(e)}

    def execute_script(self, script: str):
        if not self.driver:
            return {"status": "error", "message": "Browser not started"}
        try:
            result = self.driver.execute_script(script)
            return {"status": "success", "message": "Script executed", "result": result}
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return {"status": "error", "message": str(e)}

    def inject_recorder_js(self):
        # Full E2E Session Recorder logic
        recorder_script = """
        (function() {
            if (window.automationRecorderInitialised) return;
            window.automationRecorderInitialised = true;

            const STORAGE_KEY = 'recordedSteps';
            
            // Helper to get/set steps safely
            function getSteps() {
                try {
                    return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]');
                } catch(e) { return []; }
            }
            function saveSteps(steps) {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify(steps));
                window.recordedSteps = steps; // Maintain in window too as requested
            }

            // Persistence across reloads
            window.recordedSteps = getSteps();

            // Capture navigation (first time on this page)
            const currentUrl = window.location.href;
            let steps = getSteps();
            if (steps.length === 0 || steps[steps.length-1].action !== 'navigate' || steps[steps.length-1].value !== currentUrl) {
                steps.push({
                    action: "navigate",
                    value: currentUrl,
                    timestamp: Date.now() / 1000
                });
                saveSteps(steps);
            }

            function getXPath(el) {
                if (!el) return "";
                if (el.id) return `//*[@id='${el.id}']`;
                const parts = [];
                while (el && el.nodeType === Node.ELEMENT_NODE) {
                    let nbOfPrecedingControls = 0;
                    let hasFollowingControls = false;
                    let sibling = el.previousSibling;
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === el.tagName) nbOfPrecedingControls++;
                        sibling = sibling.previousSibling;
                    }
                    sibling = el.nextSibling;
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === el.tagName) { hasFollowingControls = true; break; }
                        sibling = sibling.nextSibling;
                    }
                    const tagName = el.tagName.toLowerCase();
                    const pathIndex = (nbOfPrecedingControls || hasFollowingControls) ? `[${nbOfPrecedingControls + 1}]` : "";
                    parts.unshift(tagName + pathIndex);
                    el = el.parentNode;
                }
                return parts.length ? "/" + parts.join("/") : null;
            }

            function getBestSelector(el) {
                if (el.id) return "#" + el.id;
                if (el.name) return "[name='" + el.name + "']";
                if (el.getAttribute("data-testid")) return "[data-testid='" + el.getAttribute("data-testid") + "']";
                return getXPath(el);
            }

            function recordAction(action, el, value = "") {
                const step = {
                    action: action,
                    selector: getBestSelector(el),
                    value: value,
                    element_id: el.id || null,
                    element_name: el.name || null,
                    data_testid: el.getAttribute('data-testid') || null,
                    tag_name: el.tagName ? el.tagName.toLowerCase() : null,
                    placeholder: el.placeholder || null,
                    inner_text: (el.innerText || "").trim(),
                    timestamp: Date.now() / 1000
                };

                let steps = getSteps();
                
                // Avoid simple duplicates
                if (steps.length > 0) {
                    const last = steps[steps.length-1];
                    if (last.action === step.action && last.selector === step.selector && last.value === step.value) return;
                }

                steps.push(step);
                saveSteps(steps);
                console.log(`[RECORDER] Recorded ${action}:`, step);
            }

            // Event Listeners
            document.addEventListener('click', function(e) {
                // Detect dropdown option selection (Angular Material, custom dropdowns, listbox items)
                let matOption = e.target.closest('mat-option, [role="option"], .mat-option, li[role="option"]');
                if (matOption) {
                    const optionText = (matOption.innerText || matOption.textContent || "").trim();
                    // Find the parent dropdown/select trigger
                    let dropdownTrigger = document.querySelector('mat-select, [role="listbox"], [role="combobox"], select');
                    const step = {
                        action: 'select',
                        selector: getBestSelector(matOption),
                        value: optionText,
                        element_id: matOption.id || null,
                        element_name: matOption.getAttribute('name') || null,
                        data_testid: matOption.getAttribute('data-testid') || null,
                        tag_name: matOption.tagName ? matOption.tagName.toLowerCase() : null,
                        placeholder: null,
                        inner_text: optionText,
                        option_text: optionText,
                        dropdown_type: matOption.tagName.toLowerCase() === 'mat-option' ? 'angular-material' : 'custom',
                        timestamp: Date.now() / 1000
                    };
                    let steps = getSteps();
                    if (steps.length > 0) {
                        const last = steps[steps.length-1];
                        if (last.action === step.action && last.value === step.value) return;
                    }
                    steps.push(step);
                    saveSteps(steps);
                    console.log(`[RECORDER] Recorded select (dropdown):`, step);
                    return;
                }

                let target = e.target.closest('button, a, input[type="submit"], input[type="button"], [role="button"]');
                if (!target) target = e.target;
                const value = (target.innerText || target.value || target.placeholder || "").trim();
                recordAction('click', target, value);
            }, true);

            // Native <select> change detection
            document.addEventListener('change', function(e) {
                if (e.target.tagName === 'SELECT') {
                    const selectedOption = e.target.options[e.target.selectedIndex];
                    const optionText = (selectedOption.text || selectedOption.innerText || "").trim();
                    const step = {
                        action: 'select',
                        selector: getBestSelector(e.target),
                        value: optionText,
                        element_id: e.target.id || null,
                        element_name: e.target.name || null,
                        data_testid: e.target.getAttribute('data-testid') || null,
                        tag_name: 'select',
                        placeholder: null,
                        inner_text: optionText,
                        option_text: optionText,
                        dropdown_type: 'native-select',
                        timestamp: Date.now() / 1000
                    };
                    let steps = getSteps();
                    steps.push(step);
                    saveSteps(steps);
                    console.log(`[RECORDER] Recorded select (native):`, step);
                }
            }, true);

            document.addEventListener('input', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.contentEditable === 'true') {
                    recordAction('input', e.target, e.target.value);
                }
            }, true);

            console.log("[RECORDER] AI Automation Recorder Initialized");
        })();
        """
        try:
            # Use CDP for persistence across reloads
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": recorder_script})
            # Try to execute on current page, but don't fail if storage is disabled (e.g. data: URLs)
            try:
                self.driver.execute_script(recorder_script)
            except:
                logger.warning("Could not execute recorder on initial page (likely storage disabled)")
                
            logger.info("Persistent E2E recorder injected")
            return {"status": "success", "message": "E2E recorder injected"}
        except Exception as e:
            logger.error(f"Failed to inject recorder: {e}")
            return {"status": "error", "message": str(e)}

    def sync_recorded_steps(self):
        """
        Fetches recorded steps FROM ALL BROWSER TABS when requested.
        Tags each step with window_handle and tab_url for multi-tab support.
        Implements anti-recursion protection.
        """
        if not self.driver:
            return {"status": "error", "message": "Browser not started"}
        
        if self.is_syncing:
            logger.warning("Sync already in progress!")
            return {"status": "ignored", "message": "Sync in progress"}

        self.is_syncing = True
        try:
            handles = self.driver.window_handles
            current_handle = self.driver.current_window_handle
            all_steps = []
            
            logger.info(f"Syncing steps from {len(handles)} tab(s)...")
            
            for i, handle in enumerate(handles):
                try:
                    self.driver.switch_to.window(handle)
                    tab_url = self.driver.current_url
                    tab_title = self.driver.title
                    
                    browser_steps = self.driver.execute_script(
                        "return JSON.parse(sessionStorage.getItem('recordedSteps') || '[]');"
                    )
                    
                    if browser_steps:
                        for step in browser_steps:
                            step["window_handle"] = handle
                            step["tab_index"] = i
                            step["tab_url"] = tab_url
                            step["tab_title"] = tab_title
                        all_steps.extend(browser_steps)
                        logger.info(f"Tab {i} ({tab_title}): {len(browser_steps)} steps")
                except Exception as tab_err:
                    logger.warning(f"Failed to sync tab {i}: {tab_err}")
            
            # Restore focus to original tab
            try:
                self.driver.switch_to.window(current_handle)
            except Exception:
                if handles:
                    self.driver.switch_to.window(handles[0])
            
            # Sort all steps by timestamp for correct chronological order
            all_steps.sort(key=lambda s: s.get("timestamp", 0))
            
            with self._lock:
                self.steps = all_steps
                logger.info(f"Successfully synced {len(self.steps)} total steps from {len(handles)} tab(s)")
            
            return {"status": "success", "count": len(self.steps), "tabs": len(handles)}
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.is_syncing = False

    def get_recorded_steps(self):
        # Alias as requested
        return self.sync_recorded_steps()

    def click(self, selector: str, selector_type: str = "css"):
        if not self.driver:
            return {"status": "error", "message": "Browser not started"}
        
        try:
            by = self._get_by_type(selector_type)
            element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((by, selector)))
            element.click()
            self.record_step(
                "click", 
                selector=selector, 
                selector_type=selector_type,
                element_id=element.get_attribute("id"),
                element_name=element.get_attribute("name"),
                data_testid=element.get_attribute("data-testid"),
                tag_name=element.tag_name,
                placeholder=element.get_attribute("placeholder"),
                inner_text=element.text
            )
            return {"status": "success", "message": f"Clicked {selector}"}
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"status": "error", "message": str(e)}

    def type_text(self, selector: str, text: str, selector_type: str = "css"):
        if not self.driver:
            return {"status": "error", "message": "Browser not started"}
        
        try:
            by = self._get_by_type(selector_type)
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by, selector)))
            element.clear()
            element.send_keys(text)
            self.record_step(
                "input", 
                selector=selector, 
                value=text, 
                selector_type=selector_type,
                element_id=element.get_attribute("id"),
                element_name=element.get_attribute("name"),
                data_testid=element.get_attribute("data-testid"),
                tag_name=element.tag_name,
                placeholder=element.get_attribute("placeholder"),
                inner_text=element.text
            )
            return {"status": "success", "message": f"Typed into {selector}"}
        except Exception as e:
            logger.error(f"Input failed: {e}")
            return {"status": "error", "message": str(e)}

    def record_step(self, action: str, value: str = None, selector: str = None, selector_type: str = "css", 
                    element_id: str = None, element_name: str = None, data_testid: str = None, 
                    tag_name: str = None, placeholder: str = None, inner_text: str = None):
        # Validate and refine locator before recording
        validated_selector = self.validate_and_refine_locator(selector, selector_type) if selector else selector
        
        current_step = {
            "action": action,
            "value": value,
            "selector": validated_selector,
            "selector_type": selector_type,
            "element_id": element_id,
            "element_name": element_name,
            "data_testid": data_testid,
            "tag_name": tag_name,
            "placeholder": placeholder,
            "inner_text": inner_text
        }

        # Avoid duplicates (check against the last step)
        if self.steps:
            last_step = self.steps[-1]
            if (last_step.get("action") == action and 
                last_step.get("selector") == validated_selector and 
                last_step.get("value") == value):
                return False

        current_step["timestamp"] = time.time()
        
        with self._lock:
            self.steps.append(current_step)
            step_count = len(self.steps)
        
        # Enhanced logging as requested
        print(f"\n[STEP RECORDED] Action: {action.upper()}")
        print(f"Selector: {validated_selector}")
        print(f"Value: {value}")
        print(f"Total Steps: {step_count}")
        print("-" * 30)
        
        logger.info(f"Recorded step: {action} on {validated_selector}. Total steps: {step_count}")
        return True

    def validate_and_refine_locator(self, selector: str, selector_type: str = "xpath"):
        """
        Validates if a locator actually finds an element.
        If not, attempts alternative XPath strategies.
        Returns the best working locator.
        """
        if not self.driver:
            return selector

        # 1. Try primary locator with retries
        for attempt in range(3):
            try:
                elements = self.driver.find_elements(self._get_by_type(selector_type), selector)
                if len(elements) == 1:
                    return selector
                elif len(elements) > 1:
                    logger.warning(f"Selector {selector} is not unique ({len(elements)} found)")
                    # Could refine here if needed
                    return selector
                
                time.sleep(0.5) # Quick wait before retry
            except Exception:
                continue

        # 2. Healer: If primary failed, try alternative strategies (only for XPaths)
        if selector_type == "xpath":
            logger.info(f"Healer: Primary XPath {selector} failed. Trying alternatives...")
            
            # Extract common elements for building alternatives (naive approach)
            # e.g. //input[@id='foo'] -> input
            import re
            match = re.search(r'//(\w+)', selector)
            tag = match.group(1) if match else "*"
            
            # Simple fallback: try by tag if it's unique (very naive but follows 'retry logic' context)
            try:
                tag_selector = f"//{tag}"
                elements = self.driver.find_elements(By.XPATH, tag_selector)
                if len(elements) == 1:
                    logger.info(f"Healer: Resolved to tag-based selector: {tag_selector}")
                    return tag_selector
            except Exception:
                pass

            # 3. AI Healer: If rule-based fallback fails, use LLM
            try:
                # Grab a snippet of the current page around the likely area (simplified: body)
                # In a real app, we'd target the parent container
                html_snippet = self.driver.execute_script("return document.body.innerHTML.substring(0, 5000);")
                from .ai_service import AIService
                ai_refined = AIService.improve_locator(html_snippet, selector)
                if ai_refined and ai_refined.startswith("//"):
                    elements = self.driver.find_elements(By.XPATH, ai_refined)
                    if len(elements) == 1:
                        logger.info(f"Healer: AI resolved to better XPath: {ai_refined}")
                        return ai_refined
            except Exception as e:
                logger.error(f"AI Healer failed: {e}")

        return selector # Return original if all else fails

    def _get_by_type(self, selector_type: str):
        types = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME
        }
        return types.get(selector_type, By.CSS_SELECTOR)

    def get_steps(self):
        with self._lock:
            return list(self.steps)

    def clear_steps(self):
        with self._lock:
            self.steps = []
        
        # Clear sessionStorage in ALL tabs
        if self.driver:
            try:
                handles = self.driver.window_handles
                current_handle = self.driver.current_window_handle
                for handle in handles:
                    try:
                        self.driver.switch_to.window(handle)
                        self.driver.execute_script("sessionStorage.setItem('recordedSteps', JSON.stringify([]));")
                        self.driver.execute_script("window.recordedSteps = [];")
                    except Exception:
                        pass
                # Restore focus
                try:
                    self.driver.switch_to.window(current_handle)
                except Exception:
                    if handles:
                        self.driver.switch_to.window(handles[0])
            except Exception:
                pass
                
        print("\n[STEPS RESET] Global recorded steps cleared across all tabs.")
        logger.info("Steps cleared across all tabs")
