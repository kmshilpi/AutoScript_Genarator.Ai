# AI Service for Browser Automation
import time
import json
import os
import re
from openai import OpenAI
from groq import Groq
from typing import List
from dotenv import load_dotenv

load_dotenv()

class AIService:
    @staticmethod
    def generate_test_case_json(steps: List[dict]) -> str:
        """
        Converts recorded steps into a JSON test case format.
        """
        return json.dumps({"steps": steps}, indent=4)

    @staticmethod
    def generate_bdd_test_case(steps: List[dict], use_ai: bool = True) -> str:
        """
        Converts recorded steps into business-readable Gherkin BDD format.
        """
        steps = AIService._filter_redundant_steps(steps)
        steps = AIService._collapse_input_steps(steps)
        if not steps:
            return "Feature: Empty Test\n  Scenario: No steps recorded"

        if use_ai and (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
            prompt = f"Convert these REAL browser automation steps into a professional Gherkin BDD format. DO NOT use any dummy data or examples. ONLY use the steps provided. Detect common flows like Login if present in the steps. Steps: {json.dumps(steps)}"
            return AIService.generate_ai_output(prompt)

        # Fallback to rule-based generation
        gherkin = [
            "Feature: Web Automation Scenario",
            "  Scenario: User performs recorded actions"
        ]
        for step in steps:
            action = step.get("action", "").capitalize()
            selector = step.get("selector", "element")
            value = f" with value '{step.get('value')}'" if step.get("value") else ""
            gherkin.append(f"    Then {action} on {selector}{value}")
        
        return "\n".join(gherkin)

    @staticmethod
    def generate_selenium_script(steps: List[dict], use_ai: bool = True) -> str:
        """
        Converts recorded steps into a production-ready Selenium Python script.
        """
        steps = AIService._filter_redundant_steps(steps)
        steps = AIService._collapse_input_steps(steps)
        if use_ai and (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
            prompt = f"Convert these REAL browser automation steps into a professional, production-ready Selenium Python script. \n- DO NOT use any dummy data or examples. \n- ONLY use the steps provided. \n- Use meaningful variable names for element finders. \n- Use WebDriverWait and avoid fixed time.sleep(). \n- Use try/except for robustness. \nSteps: {json.dumps(steps)}"
            return AIService.generate_ai_output(prompt)

        # Better fallback than just a placeholder
        script = [
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "import time\n",
            "driver = webdriver.Chrome()",
            "try:"
        ]
        for step in steps:
            action = step.get("action")
            selector = step.get("selector")
            if action == "navigate":
                script.append(f"    driver.get('{step.get('value')}')")
            elif action == "click":
                script.append(f"    driver.find_element(By.XPATH, '{selector}').click()")
            elif action == "input":
                script.append(f"    driver.find_element(By.XPATH, '{selector}').send_keys('{step.get('value')}')")
        
        script.append("finally:")
        script.append("    driver.quit()")
        return "\n".join(script)

    @staticmethod
    def generate_robot_script(steps: List[dict], use_ai: bool = True) -> str:
        """
        Converts recorded steps into a professional Robot Framework script.
        Optionally uses AI for meaningful variable names and flow detection.
        """
        steps = AIService._filter_redundant_steps(steps)
        if not steps:
            return "*** Settings ***\nLibrary    SeleniumLibrary\n\n*** Test Cases ***\nEmpty Test\n    Log    No steps recorded"

        if use_ai and (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
            prompt = f"""
            Convert these REAL browser automation steps into a professional Robot Framework script using SeleniumLibrary. 
            
            STRICT REQUIREMENTS:
            1. **Variables Section**:
               - Extract ALL locators and URLs into variables.
               - LOCATOR PRIORITY (HIGHEST PRIORITY):
                 - visible text -> xpath=//tag[normalize-space()='Text'] (USE THIS FIRST)
                 - id -> id=value (STRICT: Reject dynamic IDs like mat-input-*)
                 - name -> name=value
                 - data-testid -> css=[data-testid='value']
                 - aria-label / placeholder -> css=[aria-label='value'] or //*[@placeholder='value']
                 - relative xpath (STRICT: NEVER use absolute /html/body/...)
               - VARIABLE NAMING: Pattern: ${{TYPE_LABEL_SUFFIX}} (e.g., ${{LOGIN_BUTTON}})
               - CRITICAL: Variable names MUST NOT start with a number. Use ${{VAR_1_ELEMENT}} instead of ${{1_ELEMENT}}.
               - FORMATTING: Ensure exactly 4 spaces between the variable name and its value.

            2. **Test Cases Section**:
               - **BROWSER**: ALWAYS use 'Open Browser    ${{URL}}    chrome'. NEVER use Firefox.
               - Use reusable keywords for all interactions (Wait And Click, Wait And Input).
               - REMOVE REDUNDANT STEPS: 
                 - Do NOT click an element immediately before inputting text into it.
                 - Do NOT click wrapper divs or containers if the target element is reachable.
               - CLEANUP: Remove consecutive duplicate actions.

            3. **Keywords Section**:
               - Define 'Wait And Click' and 'Wait And Input'.
               - Use 'Wait Until Keyword Succeeds    10x    2s' inside these keywords for robustness.
            
            Steps: {json.dumps(steps)}
            """
            return AIService.generate_ai_output(prompt)

        # Fallback to rule-based generation with improved structure
        variables = []
        locator_to_var = {}
        test_steps = []
        
        # Priority logic for variables
        for i, step in enumerate(steps):
            action = step.get("action", "").lower()
            if action == "navigate":
                url = step.get("value", "")
                var_name = "${URL}"
                if i == 0 or "${URL}" not in locator_to_var.values():
                    variables.append("${: <30}    chrome".format("${BROWSER}"))
                    variables.append(f"{var_name.ljust(30)}    {url}")
                    locator_to_var[url] = var_name
                else:
                    var_name = f"${{URL_{i}}}"
                    variables.append(f"{var_name.ljust(30)}    {url}")
                    locator_to_var[url] = var_name
                continue
                
            # Priority logic for variables
            # Reject absolute XPath
            best_locator = step.get("selector", "")
            if best_locator.startswith("/html/body") or not best_locator:
                if step.get("inner_text") and len(step["inner_text"]) < 50:
                    tag = step.get("tag_name", "*")
                    best_locator = f"xpath=//{tag}[normalize-space()='{step['inner_text']}']"
                elif step.get("element_id") and "mat-input" not in step["element_id"]:
                    best_locator = f"id={step['element_id']}"
                elif step.get("element_name"):
                    best_locator = f"name={step['element_name']}"
                else:
                    best_locator = step.get("selector", "")

            # Double check: if inner_text exists, prefer it
            if step.get("inner_text") and len(step["inner_text"]) < 50:
                tag = step.get("tag_name", "*")
                best_locator = f"xpath=//{tag}[normalize-space()='{step['inner_text']}']"

            if best_locator not in locator_to_var:
                tag = step.get("tag_name", "").lower()
                suffix = "ELEMENT"
                if tag == "input" or tag == "textarea": suffix = "FIELD"
                elif tag in ["button", "a", "span", "label"] or (tag == "input" and step.get("type") in ["submit", "button"]): suffix = "BUTTON"
                elif tag == "select" or tag == "mat-select": suffix = "DROPDOWN"
                
                base = step.get("inner_text") or step.get("element_id") or step.get("element_name") or step.get("placeholder") or f"ELEM_{i}"
                base = re.sub(r'[^a-zA-Z0-9]', '_', str(base)).upper()[:20]
                
                # STABILITY FIX: Ensure variable name doesn't start with a number
                if base and base[0].isdigit():
                    base = f"VAR_{base}"
                elif not base:
                    base = f"VAR_{i}"
                
                var_name = f"${{{base}_{suffix}}}"
                
                locator_to_var[best_locator] = var_name
                variables.append(f"{var_name.ljust(30)}    {best_locator}")

        # Generate Test Steps
        for i, step in enumerate(steps):
            action = step.get("action", "").lower()
            value = step.get("value", "")
            best_locator = step.get("selector", "")
            # Re-apply logic to match var
            if step.get("element_id") and "mat-input" not in step["element_id"]:
                best_locator = f"id={step['element_id']}"
            elif step.get("element_name"):
                best_locator = f"name={step['element_name']}"
            
            var_selector = locator_to_var.get(best_locator, best_locator)
            
            # EMERGENCY FIX: Ensure var_selector is never empty for Go To
            if action == "navigate" and not var_selector:
                var_selector = "${URL}"

            if action == "navigate":
                if i == 0:
                    test_steps.append(f"    ${{options}}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver")
                    test_steps.append(f"    Call Method    ${{options}}    add_argument    --disable-notifications")
                    test_steps.append(f"    Call Method    ${{options}}    add_argument    --disable-infobars")
                    test_steps.append(f"    ${{prefs}}=    Create Dictionary    profile.default_content_setting_values.notifications=2    credentials_enable_service=${{False}}    profile.password_manager_enabled=${{False}}")
                    test_steps.append(f"    Call Method    ${{options}}    add_experimental_option    prefs    ${{prefs}}")
                    test_steps.append(f"    Create Webdriver    Chrome    options=${{options}}")
                    test_steps.append(f"    Go To    {var_selector}")
                    test_steps.append(f"    Maximize Browser Window")
                else:
                    test_steps.append(f"    Go To    {var_selector}")
            elif action == "click":
                # Check if next step is input for same element, if so skip click
                if i + 1 < len(steps) and steps[i+1].get("action") == "input" and steps[i+1].get("selector") == step.get("selector"):
                    continue
                test_steps.append(f"    Wait And Click    {var_selector}")
            elif action == "input":
                test_steps.append(f"    Wait And Input    {var_selector}    {value}")

        return "\n".join([
            "*** Settings ***",
            "Library    SeleniumLibrary",
            "\n*** Variables ***",
            *variables,
            "\n*** Test Cases ***",
            "End To End Flow",
            *test_steps,
            "\n*** Keywords ***",
            "Wait And Click",
            "    [Arguments]    ${locator}",
            "    Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${locator}    15s",
            "    Wait Until Keyword Succeeds    10x    2s    Click Element    ${locator}",
            "\nWait And Input",
            "    [Arguments]    ${locator}    ${text}",
            "    Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${locator}    15s",
            "    Wait Until Keyword Succeeds    10x    2s    Input Text    ${locator}    ${text}"
        ])

    @staticmethod
    def improve_locator(html_snippet: str, failed_locator: str) -> str:
        """
        Uses AI to propose a better XPath given a failing one and the surrounding HTML.
        Follows expert rules for stable, robust, and unique locators.
        """
        prompt = f"""
        You are an expert in Selenium, XPath, and Robot Framework automation.
        Your task is to analyze the given HTML snippet and generate a UNIQUE, STABLE, and ROBUST XPath.
        
        The XPath '{failed_locator}' failed to find the element in this HTML:
        {html_snippet}

        STRICT LOCATOR GENERATION RULES:
        1. First priority: ID (only if stable and unique)
        2. Second: Visible text (exact or contains)
        3. Third: Stable attributes (name, placeholder, type, aria-*, data-* attributes)
        4. Fourth: Parent → Child relationship
        5. Avoid class unless it is clearly unique and stable
        6. Detect dynamic attributes (random IDs, dynamic classes) and AVOID them
        7. Use index ONLY as last fallback
        8. Avoid absolute XPath (NEVER use /html/body)
        9. ALWAYS use relative XPath starting with //
        
        SMART DETECTION:
        - Identify dynamic values (e.g., id="a123x9", class="ng-xyz-123")
        - Prefer contains() for partially dynamic attributes
        - Combine multiple attributes if needed to ensure uniqueness
        - Ensure locator matches ONLY ONE element

        Return ONLY the raw XPath string (no labels, no quotes, no markdown backticks).
        """
        result = AIService.generate_ai_output(prompt)
        # Cleanup: sometimes AI adds quotes or backticks despite instructions
        return result.strip().replace('"', '').replace("'", "").replace("`", "")

    @staticmethod
    def refactor_robot_script(script: str) -> dict:
        """
        Refactors a Robot Framework script following expert rules:
        - Stable unique locators (ID → text → stable attrs)
        - Reusable keywords (Wait And Click, Wait And Input With Validation)
        - Proper input handling (clear-before-type, full value at once, verify after)
        - Angular/Material UI detection
        Returns a structured dict with best_locator, alt_locator, reason, keywords, refactored_script.
        """
        prompt = f"""
        You are a strict Robot Framework automation optimizer and expert in Selenium and XPath.
        Rewrite the given script with all rules below — produce a CLEAN, FAST, PRODUCTION-READY script.

        INPUT SCRIPT:
        {script}

        ==========================================
        🚨 CRITICAL FIX 1 — REMOVE CHAR-BY-CHAR TYPING:
        ==========================================
        - SCAN for character-by-character Input Text steps, e.g.:
            Input Text    <locator>    S
            Input Text    <locator>    Sh
            Input Text    <locator>    Shi
        - DELETE the entire group completely
        - Replace with ONE block per field:
            Wait Until Element Is Visible    <locator>    10s
            Clear Element Text    <locator>
            Input Text    <locator>    <FULL_VALUE>
            Element Attribute Value Should Be    <locator>    value    <FULL_VALUE>

        ❗ If output still contains: Input Text    S / Input Text    Sh → INVALID

        ==========================================
        ⌨️ INPUT RULE:
        ==========================================
        - EVERY input field uses this exact pattern:
            Wait Until Element Is Visible    <locator>    10s
            Clear Element Text    <locator>
            Input Text    <locator>    <FULL_VALUE>
            Element Attribute Value Should Be    <locator>    value    <FULL_VALUE>
        - ONE block per field, DO NOT repeat Input Text for the same locator

        ==========================================
        🖱️ CLICK RULE:
        ==========================================
        - For click actions, use Wait Until Keyword Succeeds only if needed:
            Wait Until Element Is Visible    <locator>    10s
            Click Element    <locator>
        - Or with retry:
            Wait Until Keyword Succeeds    3x    2s    Click Element    <locator>

        ==========================================
        🚫 LOCATOR RULES (VERY STRICT):
        ==========================================
        - REMOVE all absolute XPath starting with /html/body — REJECT and REWRITE
        - NEVER use index-based locators like div[2], div[4], span[3]
        - LOCATOR PRIORITY:
            1. id   → css=#id or //tag[@id='value']
            2. name → //tag[@name='value']
            3. Visible text → //tag[normalize-space()='Text'] or //tag[text()='Text']
            4. Stable attribute → name, placeholder, type, aria-*, data-*
            5. Parent → Child relative XPath (NEVER absolute)
        - For Angular Material elements:
            ✔ mat-select  → //mat-select
            ✔ mat-option  → //mat-option//span[text()='VALUE']
            ✔ mat-dialog  → //mat-dialog-container
            ✔ Text button → //button[normalize-space()='Submit']

        ==========================================
        ⚡ PERFORMANCE RULES:
        ==========================================
        - Max retry = 3x (only for clicks if needed)
        - NEVER use Wait Until Keyword Succeeds for Input Text
        - Use Wait Until Element Is Visible (10s timeout) instead
        - Remove all unnecessary duplicate waits

        ==========================================
        🧹 REFACTORING:
        ==========================================
        - Create reusable keywords:
            Wait And Click    → visible check + click
            Wait And Input    → visible + clear + input + verify
        - Remove redundant steps
        - Keep script fast, clean, production-ready

        ==========================================
        📤 RETURN FORMAT:
        ==========================================
        Return a JSON object with EXACTLY this structure:
        {{
          "best_locator": "//... (example from first interactive element in script)",
          "alt_locator": "//... (alternative for same element)",
          "reason": "Why these locators are stable and unique",
          "keywords": "*** Keywords ***\\nWait And Click\\n    [Arguments]    ${{locator}}\\n    Wait Until Element Is Visible    ${{locator}}    10s\\n    Click Element    ${{locator}}\\n\\nWait And Input\\n    [Arguments]    ${{locator}}\\n    ${{value}}\\n    Wait Until Element Is Visible    ${{locator}}    10s\\n    Clear Element Text    ${{locator}}\\n    Input Text    ${{locator}}    ${{value}}\\n    Element Attribute Value Should Be    ${{locator}}    value    ${{value}}",
          "refactored_script": "*** Settings ***\\n...full refactored robot script..."
        }}
        Return ONLY the JSON. No markdown. No backticks. No extra text.
        """
        response_text = AIService.generate_ai_output(prompt)
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response_text)
        except Exception as e:
            print(f"[AI] Failed to parse refactor_robot_script response: {e}")
            return {
                "best_locator": "",
                "alt_locator": "",
                "reason": "AI failed to parse the script.",
                "keywords": "",
                "refactored_script": "",
                "raw": response_text
            }

    @staticmethod
    def generate_locator(html: str) -> dict:
        """
        Analyzes an HTML element and generates a UNIQUE, STABLE, and ROBUST locator.
        Follows expert XPath generation rules.
        Returns a structured dict with best_xpath, alt_xpath, reason, selenium_code, robot_code.
        """
        prompt = f"""
        You are an expert in Selenium, XPath, and Robot Framework automation.
        Analyze the following HTML element and generate a UNIQUE, STABLE, and ROBUST locator.

        HTML:
        {html}

        STRICT LOCATOR GENERATION RULES:
        1. First priority: ID (only if stable and unique — NOT if it's dynamic like id="mat-input-15")
        2. Second: Visible text (exact or contains)
        3. Third: Stable attributes (name, placeholder, type, aria-*, data-* attributes)
        4. Fourth: Parent → Child relationship
        5. Avoid class unless clearly unique and stable
        6. Detect dynamic attributes (random IDs like id="a123x9", dynamic classes like "ng-xyz-123") and AVOID them
        7. Use index ONLY as last fallback

        ABSOLUTE XPATH FORBIDDEN (CRITICAL — HIGHEST PRIORITY RULE):
        - NEVER return any locator starting with /html or /html/body under ANY condition
        - If the HTML contains an existing /html/body/... locator — IGNORE it, rewrite into relative XPath
        - Any answer containing /html/body is INVALID and must be corrected before returning
        - For Angular Material elements:
            ✔ mat-select  → //mat-select
            ✔ mat-option  → //mat-option[normalize-space()="OptionText"]
            ✔ mat-dialog  → //mat-dialog-container
            ✔ Text match  → //span[normalize-space()="Text"]
        - If no obvious locator exists → build a parent-child relative XPath:
            e.g. //div[@role='dialog']//button[normalize-space()='Submit']
        - NEVER fall back to absolute XPath under any circumstances

        SMART DETECTION:
        - Identify dynamic values and avoid them
        - Prefer contains() for partially dynamic attributes
        - Combine multiple attributes if needed to ensure uniqueness
        - Ensure locator matches ONLY ONE element

        Return a JSON object with EXACTLY this structure:
        {{
          "best_xpath": "//...",
          "alt_xpath": "//...",
          "reason": "Why this locator is stable and unique",
          "selenium_code": "driver.find_element(By.XPATH, \\"//...\\")",
          "robot_code": "Click Element    //..."
        }}
        Return ONLY the JSON. No markdown, no backticks, no extra text.
        """
        response_text = AIService.generate_ai_output(prompt)
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response_text)
        except Exception as e:
            print(f"[AI] Failed to parse generate_locator response: {e}")
            return {
                "best_xpath": "",
                "alt_xpath": "",
                "reason": "AI failed to parse the HTML. Please check the input.",
                "selenium_code": "",
                "robot_code": "",
                "raw": response_text
            }

    @staticmethod
    def analyze_steps(steps: List[dict]) -> str:
        """
        AI-driven analysis of steps.
        """
        prompt = f"Analyze these browser automation steps for logic and efficiency: {json.dumps(steps)}"
        return AIService.generate_ai_output(prompt)

    @staticmethod
    def generate_all_formats(steps: List[dict]) -> dict:
        """
        Generates both BDD and Robot formats in a single AI call.
        Returns a dictionary with 'bdd' and 'robot' keys.
        """
        steps = AIService._filter_redundant_steps(steps)
        prompt = f"""
        Convert the following REAL browser automation steps into two formats:
        1. Professional Gherkin BDD Scenario
        2. Production-ready Robot Framework Selenium script

        STRICT RULES:
        - DO NOT use any dummy data, examples, or hardcoded navigation like google.com if not in steps.
        - ONLY use the steps provided below.
        
        MULTI-TAB AWARENESS:
        - Steps may contain "tab_index", "tab_url", and "tab_title" fields indicating which browser tab the action was performed in.
        - If steps span MULTIPLE tabs (different tab_index values):
          - For Robot Framework: Use "Switch Window" keyword when the tab context changes between consecutive steps. Use the tab title or handle as identifier.
          - For BDD: Group actions by tab context, e.g., "When the user switches to the Admin tab" or "And the user switches to the Client tab".
        - If all steps are from a single tab, do NOT add any Switch Window commands.
        
        DROPDOWN HANDLING (CRITICAL):
        - NEVER use index-based XPaths for dropdown options like (//mat-option)[2] or (//option)[3].
        - ALWAYS select dropdown options using VISIBLE TEXT.
        - Steps with action "select" contain "option_text" or "value" with the visible text of the selected option.
        - For NATIVE <select> dropdowns:
          - Robot: Use "Select From List By Label    ${{DROPDOWN}}    VisibleText"
          - BDD: "Then select 'VisibleText' from the dropdown"
        - For Angular Material (mat-select / mat-option):
          - Robot:
            1. Click dropdown trigger (with Wait Until Element Is Visible + retry)
            2. Wait Until Element Is Visible for mat-option panel
            3. Click Element    xpath=//mat-option//span[normalize-space(text())="OptionText"]
          - BDD: "Then select 'OptionText' from the material dropdown"
        - For custom dropdowns ([role="listbox"], [role="combobox"]):
          - Robot: Click trigger, wait, then Click Element using text-based xpath
          - BDD: "Then select 'OptionText' from the dropdown"
        - FORBIDDEN patterns (DO NOT USE):
          - (//mat-option)[1], (//mat-option)[2] etc.
          - Select From List By Index
          - Any position/index-based option selection
        
        - For Robot Framework:
            - The script MUST start with `*** Settings ***` containing `Library    SeleniumLibrary`.
            - Ensure valid `*** Test Cases ***` and `*** Variables ***` blocks.

            ===========================================
            🛠️ KEYWORDS (STABILITY):
            ===========================================
            - ALWAYS use `Wait Until Element Is Visible    ${{locator}}    15s` before Click or Input.
            - Create Reusable Keywords:
                Wait And Click
                    [Arguments]    ${{locator}}
                    Wait Until Element Is Visible    ${{locator}}    15s
                    Click Element    ${{locator}}

                Wait And Input
                    [Arguments]    ${{locator}}    ${{text}}
                    Wait Until Element Is Visible    ${{locator}}    15s
                    Input Text    ${{locator}}    ${{text}}

            ===========================================
            🌐 BROWSER & CACHE SETUP (MANDATORY):
            ===========================================
            - ALWAYS start the test case with a clean WebDriver using SEPARATE Call Method lines:
                ${{options}}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
                Call Method    ${{options}}    add_argument    --disable-notifications
                Call Method    ${{options}}    add_argument    --disable-infobars
                ${{prefs}}=    Create Dictionary    profile.default_content_setting_values.notifications=2    credentials_enable_service=${{False}}    profile.password_manager_enabled=${{False}}
                Call Method    ${{options}}    add_experimental_option    prefs    ${{prefs}}
                Create Webdriver    Chrome    options=${{options}}
                Go To    ${{URL}}
                Maximize Browser Window
            - NEVER use "Open Browser". Use "Create Webdriver" for better control.
            - NEVER combine Call Method calls with semicolons or on one line.

            ===========================================
            🚫 LOCATOR STRATEGY (STRICT RULES):
            ===========================================
            - ABSOLUTELY FORBIDDEN: Absolute XPaths like `/html/body/...`
            - ABSOLUTELY FORBIDDEN: Dynamic Angular/Material IDs like `mat-option-123`, `mat-input-0`
            - PREFERRED: id=, name=, placeholder=
            - FOR TEXT: Use `xpath=//tag[normalize-space()='Text']` or `xpath=//*[contains(normalize-space(), 'Text')]`
            - FOR BUTTONS: Use `xpath=//button[normalize-space()='Submit']`
            - Ensure all locators are stable and unique.
            - NEVER use /html/body/... or any absolute XPath — INVALID, must be rewritten
            - NEVER use index-based locators: div[2], span[3], li[4] — FORBIDDEN
            - NEVER use Angular auto-generated IDs: id=mat-input-15, id=mat-option-272 — FORBIDDEN
            - LOCATOR PRIORITY:
                1. id     → css=#stable-id
                2. name   → //tag[@name='value']
                3. placeholder → //input[@placeholder='value']
                4. Visible text → //tag[normalize-space()='Text']
                5. Stable data-* or aria-* attribute
                6. Relative parent→child XPath (LAST RESORT — NEVER absolute)

            ===========================================
            🎯 ANGULAR MATERIAL DROPDOWNS:
            ===========================================
            - Click trigger: //mat-select (or closest stable parent)
            - Select option: //mat-option//span[normalize-space()='VALUE']
            - NEVER use (//mat-option)[1], index-based selection, or mat-option-XXX IDs
            - PATTERN:
                Wait Until Element Is Visible    //mat-select    10s
                Click Element    //mat-select
                Wait Until Element Is Visible    //mat-option//span[normalize-space()='VALUE']    10s
                Click Element    //mat-option//span[normalize-space()='VALUE']

            ===========================================
            ⌨️ INPUT PATTERN (MANDATORY — ONE BLOCK PER FIELD):
            ===========================================
            - NEVER type character by character (Input Text    S / Input Text    Sh = INVALID)
            - NEVER wrap Input Text in Wait Until Keyword Succeeds
            - ALWAYS use this exact pattern:
                Wait Until Element Is Visible    ${{LOCATOR}}    10s
                Clear Element Text    ${{LOCATOR}}
                Input Text    ${{LOCATOR}}    ${{FULL_VALUE}}
                Element Attribute Value Should Be    ${{LOCATOR}}    value    ${{FULL_VALUE}}

            ===========================================
            🖱️ CLICK PATTERN:
            ===========================================
                Wait Until Element Is Visible    ${{LOCATOR}}    10s
                Click Element    ${{LOCATOR}}
            - Use `Wait Until Keyword Succeeds    3x    2s    Click Element    ${{LOCATOR}}` only when needed for unstable elements.
            - NEVER use Wait Until Keyword Succeeds for Input Text.

            ===========================================
            📦 VARIABLES & NAMING (CLEANUP):
            ===========================================
            - Extract ALL locators and URLs into `*** Variables ***`
            - DO NOT create duplicate variables for the same locator.
            - Variable names MUST be valid (A-Z, 0-9, _). NO spaces.
            - DO NOT start variables with numbers. Use ${{VAR_1_ELEMENT}} or ${{ELEMENT_1}} instead.
            - Remove any "undefined" locators.
            - mat-select/dropdown → *_DROPDOWN
            - mat-option → *_OPTION
            - generic → *_ELEMENT
            - Reuse variables — no duplicates

            ===========================================
            🧹 CLEAN STRUCTURE:
            ===========================================
            - One action per step — no duplicate Input Text for same field
            - Create reusable keywords: Wait And Click, Wait And Input
            - Keep script FAST, CLEAN, and PRODUCTION-READY

        Steps: {json.dumps(steps)}

        Return your response strictly as a JSON object with this structure:
        {{
            "bdd": "Scenario text here...",
            "robot": "Robot script here..."
        }}
        """
        response_text = AIService.generate_ai_output(prompt)
        
        try:
            # Attempt to parse as JSON
            import re
            # Extract JSON if LLM added markdown triple backticks
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(response_text)
        except Exception as e:
            print(f"[AI] Failed to parse consolidated response: {e}")
            # Fallback to separate calls if consolidated fails
            return {
                "bdd": AIService.generate_bdd_test_case(steps),
                "robot": AIService.generate_robot_script(steps)
            }

    @staticmethod
    def _filter_redundant_steps(steps: List[dict]) -> List[dict]:
        """
        Removes redundant 'navigate' steps that immediately follow a 'click' or 'input' 
        in the same tab, as those actions likely triggered the navigation anyway.
        Also removes consecutive 'navigate' steps to the same URL.
        """
        if not steps:
            return []
            
        filtered = []
        for i, step in enumerate(steps):
            action = step.get("action")
            url = step.get("value")
            tab = step.get("tab_index", 0)
            
            if action == "navigate":
                # Skip if it's the same URL as the previous step in the same tab
                if filtered and filtered[-1].get("action") == "navigate" and filtered[-1].get("value") == url and filtered[-1].get("tab_index", 0) == tab:
                    continue
                
                # Skip if the previous step was an interaction in the same tab (click/input/select)
                # Reason: The interaction likely caused the navigation.
                if filtered and filtered[-1].get("action") in ["click", "input", "select"] and filtered[-1].get("tab_index", 0) == tab:
                    print(f"[FILTER] Removing redundant navigation to {url} following {filtered[-1].get('action')}")
                    continue
            
            filtered.append(step)
            
        return filtered

    @staticmethod
    def _collapse_input_steps(steps: List[dict]) -> List[dict]:
        """
        Collapses consecutive input steps for the same field into ONE step with the final value.
        This is a backend safety net against character-by-character typing recorded by the JS recorder.
        e.g. input 'S', input 'Sh', input 'Shi' → input 'Shilpi@gmail.com'
        """
        if not steps:
            return []
        
        collapsed = []
        i = 0
        while i < len(steps):
            step = steps[i]
            if step.get('action') == 'input':
                selector = step.get('selector')
                # Gather all consecutive input steps for this same selector
                group = [step]
                j = i + 1
                while j < len(steps) and steps[j].get('action') == 'input' and steps[j].get('selector') == selector:
                    group.append(steps[j])
                    j += 1
                # Keep only the last one (final value)
                final_step = group[-1]
                if len(group) > 1:
                    print(f"[COLLAPSE] Collapsed {len(group)} input steps for '{selector}' → final value: '{final_step.get('value')}'")
                collapsed.append(final_step)
                i = j
            else:
                collapsed.append(step)
                i += 1
        
        return collapsed

    @staticmethod
    def generate_ai_output(prompt: str) -> str:
        """
        Generates text output using a multi-provider fallback system:
        1. OpenAI (gpt-4o-mini)
        2. Groq (llama3-70b-8192)
        3. Together AI (meta-llama/Llama-3-70b-chat-hf)
        4. OpenRouter (google/gemini-pro-1.5)
        """
        providers = [
            {
                "name": "OpenAI",
                "key": os.getenv("OPENAI_API_KEY"),
                "model": "gpt-4o-mini",
                "base_url": None
            },
            {
                "name": "Groq",
                "key": os.getenv("GROQ_API_KEY"),
                "model": "llama-3.3-70b-versatile",
                "use_groq_sdk": True
            },
            {
                "name": "Together AI",
                "key": os.getenv("TOGETHER_API_KEY"),
                "model": "meta-llama/Llama-3-70b-chat-hf",
                "base_url": "https://api.together.xyz/v1"
            },
            {
                "name": "OpenRouter",
                "key": os.getenv("OPENROUTER_API_KEY"),
                "model": "google/gemini-2.0-flash-001",
                "base_url": "https://openrouter.ai/api/v1"
            }
        ]

        for provider in providers:
            if not provider["key"] or "your_" in provider["key"]:
                continue

            try:
                print(f"[AI] Attempting generation with {provider['name']} ({provider['model']})...")
                
                if provider.get("use_groq_sdk"):
                    from groq import Groq
                    client = Groq(api_key=provider["key"])
                else:
                    from openai import OpenAI
                    client = OpenAI(api_key=provider["key"], base_url=provider["base_url"])

                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.choices[0].message.content
                print(f"[AI] Success using {provider['name']}!")
                return content

            except Exception as e:
                print(f"[AI] {provider['name']} failed: {e}")
                continue

        return "Error: All AI providers failed or no valid API keys found in environment variables."
