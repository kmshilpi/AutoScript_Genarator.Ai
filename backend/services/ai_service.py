import time
import json
import os
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
        if not steps:
            return "*** Settings ***\nLibrary    SeleniumLibrary\n\n*** Test Cases ***\nEmpty Test\n    Log    No steps recorded"

        if use_ai and (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")):
            prompt = f"""
            Convert these REAL browser automation steps into a professional Robot Framework script using SeleniumLibrary. 
            
            STRICT REQUIREMENTS:
            1. Add a '*** Variables ***' section:
               - Extract all locators into variables.
               - Extract navigation URLs into variables (e.g., ${{BASE_URL}}, ${{LOGIN_URL}}).
               - LOCATOR PRIORITY (Use exact css prefix syntax):
                 1. id -> css=#id
                 2. name -> css=[name='value']
                 3. data-testid -> css=[data-testid='value']
                 4. xpath (last resort)
               - VARIABLE NAMING:
                 - input/textarea -> *_FIELD
                 - button -> *_BUTTON
                 - link (a) -> *_LINK
                 - select/dropdown -> *_DROPDOWN
                 - option -> *_OPTION
                 - generic -> *_ELEMENT
                 - Use element id, placeholder, or innerText for the name part.
            2. Replace raw locators and URLs in steps with these variables.
            3. Add retry logic to EVERY action step:
               - Use: Wait Until Keyword Succeeds    15x    2s
            4. For each interaction (Click, Input, etc.):
               - First 'Wait Until Element Is Visible' (with retry).
               - Then perform the action (with retry).
            5. For Navigation:
               - If it is the VERY FIRST action, use 'Open Browser    ${{URL_VAR}}    chrome' followed by 'Maximize Browser Window'.
               - Otherwise, use 'Go To' with the corresponding URL variable and retry logic.
            6. AVOID DUPLICATES: If the same locator is used multiple times, reuse the variable.
            
            DROPDOWN HANDLING (CRITICAL):
            - NEVER use index-based XPaths for dropdown options like (//mat-option)[2] or (//option)[3].
            - ALWAYS select dropdown options using VISIBLE TEXT from the step data.
            - Steps with action "select" contain an "option_text" or "value" field with the visible text.
            - For NATIVE <select> dropdowns:
              - Use: Select From List By Label    ${{DROPDOWN_VAR}}    VisibleText
            - For Angular Material (mat-select / mat-option) dropdowns:
              1. Click the dropdown trigger to open it (with retry + wait visible).
              2. Wait Until Element Is Visible for the option panel.
              3. Click the option using text-based XPath:
                 Click Element    xpath=//mat-option//span[normalize-space(text())="OptionText"]
            - For custom dropdowns ([role="listbox"], [role="combobox"]):
              1. Click the trigger to open options.
              2. Wait Until Element Is Visible for options container.
              3. Click option using text: xpath=//*[@role="option"][normalize-space(text())="OptionText"]
            - FORBIDDEN patterns:
              - (//mat-option)[1], (//mat-option)[2] etc.
              - Select From List By Index
              - Any position/index-based option selection
            
            Steps: {json.dumps(steps)}
            """
            return AIService.generate_ai_output(prompt)

        # Fallback to rule-based generation with improved structure
        variables = []
        locator_to_var = {}
        test_steps = []
        retry_prefix = "Wait Until Keyword Succeeds    15x    2s    "
        
        # Priority logic for variables
        for i, step in enumerate(steps):
            action = step.get("action", "").lower()
            if action == "navigate":
                url = step.get("value", "")
                var_name = f"${{URL_{i}}}" if i > 0 else "${URL}"
                variables.append(f"{var_name.ljust(30)} {url}")
                locator_to_var[url] = var_name
                continue
                
            # Determine best locator based on priority
            best_locator = step.get("selector")
            if step.get("element_id"):
                best_locator = f"id={step['element_id']}"
            elif step.get("element_name"):
                best_locator = f"name={step['element_name']}"
            elif step.get("data_testid"):
                best_locator = f"css=[data-testid='{step['data_testid']}']"
            
            if best_locator not in locator_to_var:
                # Generate name
                tag = step.get("tag_name", "").lower()
                suffix = "ELEMENT"
                if tag == "input" or tag == "textarea": suffix = "FIELD"
                elif tag == "button" or (tag == "input" and step.get("value") in ["submit", "button"]): suffix = "BUTTON"
                elif tag == "a": suffix = "LINK"
                elif tag == "select" or tag == "mat-select": suffix = "DROPDOWN"
                elif tag == "mat-option" or tag == "option": suffix = "OPTION"
                
                # Base name from id, name, placeholder or text
                base = step.get("element_id") or step.get("element_name") or step.get("placeholder") or step.get("inner_text") or f"ELEM_{i}"
                import re
                base = re.sub(r'[^a-zA-Z0-9]', '_', str(base)).upper()[:20]
                
                var_name = f"${{{base}_{suffix}}}"
                # Handle potential duplicate names for different locators
                if any(v.startswith(var_name[:-1]) for v in locator_to_var.values()):
                    var_name = f"${{{base}_{i}_{suffix}}}"
                    
                locator_to_var[best_locator] = var_name
                variables.append(f"{var_name.ljust(30)} {best_locator}")

        # Generate Test Steps
        for step in steps:
            action = step.get("action", "").lower()
            value = step.get("value", "")
            
            # Determine best locator again for the step
            best_locator = step.get("selector")
            if step.get("element_id"):
                best_locator = f"id={step['element_id']}"
            elif step.get("element_name"):
                best_locator = f"name={step['element_name']}"
            elif step.get("data_testid"):
                best_locator = f"css=[data-testid='{step['data_testid']}']"
            
            var_selector = locator_to_var.get(best_locator, best_locator)
            var_value = locator_to_var.get(value, value)
            
            if action == "navigate":
                if len(test_steps) == 0:
                    test_steps.append(f"    Open Browser    {var_value}    chrome")
                    test_steps.append(f"    Maximize Browser Window")
                else:
                    test_steps.append(f"    {retry_prefix}Go To    {var_value}")
            elif action == "click":
                test_steps.append(f"    {retry_prefix}Wait Until Element Is Visible    {var_selector}    2s")
                test_steps.append(f"    {retry_prefix}Click Element    {var_selector}")
            elif action == "input":
                test_steps.append(f"    {retry_prefix}Wait Until Element Is Visible    {var_selector}    2s")
                test_steps.append(f"    {retry_prefix}Input Text    {var_selector}    {value}")
            elif action == "select":
                option_text = step.get("option_text") or step.get("value", "")
                dropdown_type = step.get("dropdown_type", "")
                if dropdown_type == "native-select":
                    # Native select — use Select From List By Label
                    test_steps.append(f"    {retry_prefix}Wait Until Element Is Visible    {var_selector}    2s")
                    test_steps.append(f"    {retry_prefix}Select From List By Label    {var_selector}    {option_text}")
                else:
                    # Angular Material / custom — use text-based xpath click
                    test_steps.append(f"    {retry_prefix}Wait Until Element Is Visible    {var_selector}    2s")
                    test_steps.append(f"    {retry_prefix}Click Element    {var_selector}")
                    option_xpath = f"xpath=//mat-option//span[normalize-space(text())=\\\"{option_text}\\\"]"
                    test_steps.append(f"    {retry_prefix}Wait Until Element Is Visible    {option_xpath}    5s")
                    test_steps.append(f"    {retry_prefix}Click Element    {option_xpath}")

        return "\n".join([
            "*** Settings ***",
            "Library    SeleniumLibrary",
            "\n*** Variables ***",
            *variables,
            "\n*** Test Cases ***",
            "End To End Flow",
            *test_steps
        ])

    @staticmethod
    def improve_locator(html_snippet: str, failed_locator: str) -> str:
        """
        Uses AI to propose a better XPath given a failing one and the surrounding HTML.
        """
        prompt = f"The XPath '{failed_locator}' failed to find an element in this HTML snippet: \n{html_snippet}\n\nPlease provide a more robust and unique XPath for the intended element. Return only the XPath string."
        return AIService.generate_ai_output(prompt)

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
            - The script MUST start with a valid `*** Settings ***` section containing `Library    SeleniumLibrary`.
            - Ensure a valid `*** Test Cases ***` block is present.
            - Provide a `*** Variables ***` section for all locators AND URLs.
            - For the VERY FIRST navigation step in the test case, use `Open Browser    ${{URL_VAR}}    chrome` followed by `Maximize Browser Window`. NEVER start with just `Go To`.
            - LOCATOR PRIORITY (Use exact css prefix syntax):
              1. id -> css=#id
              2. name -> css=[name='value']
              3. data-testid -> css=[data-testid='value']
              4. xpath (last resort)
            - VARIABLE NAMING:
              - input/textarea -> *_FIELD
              - button -> *_BUTTON
              - link (a) -> *_LINK
              - select/dropdown -> *_DROPDOWN
              - option -> *_OPTION
              - generic -> *_ELEMENT
              - Use element id, placeholder, or innerText for the name part.
            - Add retry logic: 'Wait Until Keyword Succeeds    15x    2s' for every step including Go To (Make sure you use exactly 4 spaces to separate arguments, NOT a single space!).
            - Every action (Click, Input, etc.) MUST Wait Until Element Is Visible (with retry) BEFORE interaction.
            - Avoid duplicate variables. If a locator or URL is used multiple times, reuse the variable.
        - If no steps are provided, indicate that no actions were recorded.

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
