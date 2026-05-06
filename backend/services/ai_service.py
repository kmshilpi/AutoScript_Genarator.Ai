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
    def clean_variable_name(name: str) -> str:
        """
        Standardizes naming following strict rules:
        - Must not start with a number (1_ELEMENT -> ELEMENT_1)
        - Alphanumeric and underscores only
        """
        if not name: return "ELEMENT"
        # Remove non-alphanumeric, convert to upper
        name = re.sub(r'[^a-zA-Z0-9]', '_', str(name)).upper().strip('_')
        if not name: return "ELEMENT"
        
        # Rule: Variable names must NEVER start with a number
        if name[0].isdigit():
            match = re.match(r'^(\d+)(.*)', name)
            if match:
                digits, rest = match.groups()
                rest = rest.strip('_')
                if rest:
                    return f"{rest}_{digits}"
                else:
                    return f"ELEMENT_{digits}"
        return name

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
            prompt = f"""
            Convert these steps into a professional Gherkin BDD format.
            STRICT RULES:
            - Return ONLY a JSON object: {{"bdd_scenario": "Feature... Scenario..."}}
            - No extra text.
            Steps: {json.dumps(steps)}
            """
            response = AIService.generate_ai_output(prompt)
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0)).get("bdd_scenario", response)
                return response
            except:
                return response

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
            prompt = f"""
            Convert these steps into a production-ready Selenium Python script.
            STRICT RULES:
            - Use WebDriverWait.
            - Variable names must not start with numbers.
            - Return ONLY a JSON object: {{"selenium_code": "import selenium..."}}
            Steps: {json.dumps(steps)}
            """
            response = AIService.generate_ai_output(prompt)
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0)).get("selenium_code", response)
                return response
            except:
                return response

        # Better fallback than just a placeholder
        script = [
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.chrome.service import Service",
            "from webdriver_manager.chrome import ChromeDriverManager",
            "import time\n",
            "options = webdriver.ChromeOptions()",
            "options.add_argument('--disable-notifications')",
            "driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)",
            "driver.maximize_window()",
            "try:"
        ]
        for i, step in enumerate(steps):
            action = step.get("action")
            selector = step.get("selector", "")
            # Ensure safe variable name for locator mapping in fallback
            var_base = AIService.clean_variable_name(f"ELEM_{i}")
            
            if action == "navigate":
                script.append(f"    driver.get('{step.get('value')}')")
            elif action == "click":
                script.append(f"    # Interaction for {var_base}")
                script.append(f"    driver.find_element(By.XPATH, \"{selector}\").click()")
            elif action == "input":
                script.append(f"    driver.find_element(By.XPATH, \"{selector}\").send_keys(\"{step.get('value')}\")")
        
        script.append("finally:")
        script.append("    driver.quit()")
        return "\n".join(script)

    @staticmethod
    def generate_robot_script(steps: List[dict], use_ai: bool = True) -> str:
        """
        Converts recorded steps into a professional Robot Framework script.
        Follows STRICT formatting: 2 spaces, no custom keywords, mandatory retry blocks.
        """
        steps = AIService._filter_redundant_steps(steps)
        if not steps:
            return "*** Settings ***\nLibrary  SeleniumLibrary\n\n*** Test Cases ***\nEmpty Test\n  Log  No steps recorded"

        if use_ai and (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
            prompt = f"""
            Convert these steps into a stable, clean Robot Framework script.
            
            STRICT RULES:
            1. **NEVER use raw locators directly in keywords.** All locators MUST be variables.
            2. **ALWAYS store every locator in the *** Variables *** section.**
            3. **ALWAYS reuse existing variables** if the same locator appears again. Do NOT create duplicate variables for the same locator.
            4. **Generate meaningful variable names** based on element purpose (e.g., LOGIN_BUTTON, SUBMIT_BTN, USERNAME_INPUT, PROPERTY_TYPE_DROPDOWN).
            5. **In test steps, ALWAYS use ${{VARIABLE_NAME}}** instead of raw XPath/CSS.
            6. **FORMATTING**: Use EXACTLY 2 spaces between arguments. DO NOT use tabs.
            7. **NO CUSTOM KEYWORDS**: Use direct steps only. No "Wait And Click".
            8. **DROPDOWN HANDLING (CRITICAL)**:
               - Detect dropdowns (select, mat-select, [role="listbox"]).
               - ALWAYS use a 2-step interaction:
                 STEP 1 (Click Trigger):
                 Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  ${{DROPDOWN_LOCATOR}}  2s
                 Wait Until Keyword Succeeds  25x  2s  Click Element  ${{DROPDOWN_LOCATOR}}
                 STEP 2 (Click Option):
                 Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  ${{OPTION_LOCATOR}}  2s
                 Wait Until Keyword Succeeds  25x  2s  Click Element  ${{OPTION_LOCATOR}}
               - Option XPath: xpath=//mat-option[normalize-space()='VALUE']

            9. **CLICK/INPUT FORMAT**:
               Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  ${{LOCATOR}}  2s
               Wait Until Keyword Succeeds  25x  2s  Click Element/Input Text  ${{LOCATOR}}  [VALUE]

            Steps: {json.dumps(steps)}
            """
            response = AIService.generate_ai_output(prompt)
            try:
                # Rule 6: Ensure backend never breaks
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    return data.get("robot_script", response)
                return response
            except Exception as e:
                print(f"[AI ERROR] Failed to parse robot script JSON: {e}")
                return response

        # Fallback to rule-based generation with 2-space formatting
        variables = []
        locator_to_var = {}
        test_steps = []
        
        for i, step in enumerate(steps):
            action = step.get("action", "").lower()
            if action == "navigate":
                url = step.get("value", "")
                var_name = "${URL}"
                if i == 0 or "${URL}" not in locator_to_var.values():
                    variables.append("${BROWSER}  chrome")
                    variables.append(f"{var_name}  {url}")
                    locator_to_var[url] = var_name
                continue
                
            # Consistent locator selection logic
            best_locator = step.get("selector", "")
            if step.get("element_id"):
                best_locator = f"id={step['element_id']}"
            elif best_locator.startswith("/html/body") or not best_locator:
                if step.get("inner_text") and len(step["inner_text"]) < 50:
                    tag = step.get("tag_name", "*")
                    best_locator = f"xpath=//{tag}[normalize-space()='{step['inner_text']}']"
                elif step.get("element_id"): # Redundant but safe
                    best_locator = f"id={step['element_id']}"

            if best_locator not in locator_to_var:
                tag = step.get("tag_name", "").lower()
                suffix = "ELEMENT"
                if tag == "input" or tag == "textarea": suffix = "INPUT"
                elif tag in ["button", "a", "span", "label"]: suffix = "BUTTON"
                
                base = step.get("inner_text") or step.get("element_id") or f"ELEM_{i}"
                var_base = AIService.clean_variable_name(base)
                var_name = f"${{{var_base}_{suffix}}}"
                # Ensure no duplicate variable names
                counter = 1
                while var_name in variables:
                    var_name = f"${{{var_base}_{suffix}_{counter}}}"
                    counter += 1
                    
                locator_to_var[best_locator] = var_name
                variables.append(f"{var_name}  {best_locator}")

        for i, step in enumerate(steps):
            action = step.get("action", "").lower()
            value = step.get("value", "")
            
            if action == "navigate":
                var_selector = locator_to_var.get(value, "${URL}")
                if i == 0:
                    test_steps.append(f"  Open Browser  {var_selector}  ${{BROWSER}}")
                    test_steps.append(f"  Maximize Browser Window")
                else:
                    test_steps.append(f"  Go To  {var_selector}")
                continue

            # Consistent locator selection logic
            best_locator = step.get("selector", "")
            if step.get("element_id"):
                best_locator = f"id={step['element_id']}"
            elif best_locator.startswith("/html/body") or not best_locator:
                if step.get("inner_text") and len(step["inner_text"]) < 50:
                    tag = step.get("tag_name", "*")
                    best_locator = f"xpath=//{tag}[normalize-space()='{step['inner_text']}']"
            
            var_selector = locator_to_var.get(best_locator)
            if not var_selector:
                # Emergency fallback if logic above missed it
                var_base = AIService.clean_variable_name(f"ELEM_{i}")
                var_selector = f"${{{var_base}_ELEMENT}}"
                variables.append(f"{var_selector}  {best_locator}")
                locator_to_var[best_locator] = var_selector
            
            if action == "click":
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  {var_selector}  2s")
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Click Element  {var_selector}")
            elif action == "input":
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  {var_selector}  2s")
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Input Text  {var_selector}  {value}")
            elif action == "select":
                option_locator = f"xpath=//*[normalize-space()='{value}']"
                if option_locator in locator_to_var:
                    option_var = locator_to_var[option_locator]
                else:
                    option_var = f"${{{var_selector.strip('${}')}_OPTION_{AIService.clean_variable_name(value)}}}"
                    variables.append(f"{option_var}  {option_locator}")
                    locator_to_var[option_locator] = option_var
                
                test_steps.append(f"  # Step 1: Click Dropdown")
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  {var_selector}  2s")
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Click Element  {var_selector}")
                test_steps.append(f"  # Step 2: Click Option")
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  {option_var}  2s")
                test_steps.append(f"  Wait Until Keyword Succeeds  25x  2s  Click Element  {option_var}")

        return "\n".join(["*** Settings ***", "Library  SeleniumLibrary", "\n*** Variables ***", *variables, "\n*** Test Cases ***", "End To End Flow", *test_steps])

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
        🌐 BROWSER SETUP (MANDATORY):
        ==========================================
        - The script MUST start with:
            Open Browser    ${{URL}}    ${{BROWSER}}
            Maximize Browser Window

        ==========================================
        ⌨️ KEYWORDS (STRICT):
        ==========================================
        - Use ONLY:
            Wait And Click    ${{VARIABLE}}
            Wait And Input    ${{VARIABLE}}    value
        - Define these in *** Keywords ***:
            Wait And Click
                [Arguments]    ${{locator}}
                Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${{locator}}    15s
                Wait Until Keyword Succeeds    10x    2s    Click Element    ${{locator}}
            
            Wait And Input
                [Arguments]    ${{locator}}    ${{text}}
                Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${{locator}}    15s
                Wait Until Keyword Succeeds    10x    2s    Input Text    ${{locator}}    ${{text}}

        ==========================================
        🚫 LOCATOR RULES (STRICT):
        ==========================================
        1. **NEVER use raw locators directly in keywords.** All locators MUST be variables.
        2. **ALWAYS store every locator in the *** Variables *** section.**
        3. **ALWAYS reuse existing variables** if the same locator appears again. Do NOT create duplicate variables for the same locator.
        4. **Generate meaningful variable names** based on element purpose (e.g., LOGIN_BUTTON, SUBMIT_BTN, USERNAME_INPUT).
        5. **In test steps, ALWAYS use ${{VARIABLE_NAME}}** instead of raw XPath/CSS.
        6. **NEVER use absolute XPath** (/html/body/...).
        7. **NEVER use $${{VAR}}.** ALWAYS use ${{VAR}}.

        ==========================================
        📤 RETURN FORMAT:
        ==========================================
        Return a JSON object with EXACTLY this structure:
        {{
          "best_locator": "//... (example relative locator)",
          "alt_locator": "//...",
          "reason": "Stable and unique because...",
          "keywords": "*** Keywords ***\\nWait And Click\\n    [Arguments]    ${{locator}}\\n    Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${{locator}}    15s\\n    Wait Until Keyword Succeeds    10x    2s    Click Element    ${{locator}}\\n\\nWait And Input\\n    [Arguments]    ${{locator}}\\n    ${{text}}\\n    Wait Until Keyword Succeeds    10x    2s    Wait Until Element Is Visible    ${{locator}}    15s\\n    Wait Until Keyword Succeeds    10x    2s    Input Text    ${{locator}}    ${{text}}",
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
          "robot_code": "${{MY_VARIABLE}}    //...\\nClick Element    ${{MY_VARIABLE}}"
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
        Convert the following steps into TWO formats:
        1. Professional Gherkin BDD Scenario
        2. Production-ready Robot Framework script

        STRICT RULES FOR ROBOT FRAMEWORK:
        1. **NEVER use raw locators directly in keywords.** All locators MUST be variables.
        2. **ALWAYS store every locator in the *** Variables *** section.**
        3. **ALWAYS reuse existing variables** if the same locator appears again. Do NOT create duplicate variables for the same locator.
        4. **Generate meaningful variable names** based on element purpose (e.g., LOGIN_BUTTON, SUBMIT_BTN, USERNAME_INPUT).
        5. **In test steps, ALWAYS use ${{VARIABLE_NAME}}** instead of raw XPath/CSS.
        6. **FORMATTING**: Use EXACTLY 2 spaces between arguments. DO NOT use tabs.
        7. **NO CUSTOM KEYWORDS** (No Wait And Click).
        8. **CLICK ACTION FORMAT (MANDATORY)**:
          Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  ${{LOCATOR}}  2s
          Wait Until Keyword Succeeds  25x  2s  Click Element  ${{LOCATOR}}
        9. **INPUT ACTION FORMAT (MANDATORY)**:
          Wait Until Keyword Succeeds  25x  2s  Wait Until Element Is Visible  ${{LOCATOR}}  2s
          Wait Until Keyword Succeeds  25x  2s  Input Text  ${{LOCATOR}}  ${{VALUE}}
        10. **BROWSER SETUP**:
          Open Browser  ${{URL}}  ${{BROWSER}}
          Maximize Browser Window

        Steps: {json.dumps(steps)}

        Return ONLY a JSON object:
        {{
            "bdd": "Gherkin scenario here...",
            "robot": "Robot script here..."
        }}
        """
        response_text = AIService.generate_ai_output(prompt)
        
        try:
            # Rule 6: Safe parsing
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                # Ensure it has the structure the frontend expects
                return {
                    "bdd": result.get("bdd", ""),
                    "robot": result.get("robot_script") or result.get("robot") or ""
                }
            return json.loads(response_text)
        except Exception as e:
            print(f"[AI ERROR] Failed to parse consolidated JSON: {e}")
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
