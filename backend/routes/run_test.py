from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
import sys
import re
from services.selenium_service import SeleniumService

router = APIRouter()
selenium_service = SeleniumService()

class RunRequest(BaseModel):
    script: str

@router.post("")
@router.post("/")
async def run_test_script(request: RunRequest):
    try:
        selenium_service.is_executing = True
        print("[DEBUG] /run-test: Setting is_executing = True")
        script_content = request.script
        
        # Safeguard: Inject Settings and Library if missing
        if "*** Settings ***" not in script_content:
            script_content = "*** Settings ***\nLibrary    SeleniumLibrary\n\n" + script_content
            
        # Safeguard: Fix AI formatting for Wait Until Keyword Succeeds spacing
        script_content = re.sub(r'Wait Until Keyword Succeeds\s+15x\s+2s', r'Wait Until Keyword Succeeds    15x    2s', script_content)
        
        # Safeguard: Auto-prefix #id locators with css= if missing
        script_content = re.sub(r'(\s+)#([a-zA-Z0-9_\-]+)', r'\1css=#\2', script_content)

        # Safeguard: Fix variables starting with numbers (e.g. ${1_ELEMENT} -> ${ELEMENT_1})
        script_content = re.sub(r'\$\{([0-9]+)_([a-zA-Z0-9_]+)\}', r'${\2_\1}', script_content)

        # Safeguard: Fix malformed BROWSER variable definition
        script_content = re.sub(r'\$\{\'BROWSER\'\.ljust\(\d+\)\}', r'${BROWSER}', script_content)
        script_content = re.sub(r'\$\{BROWSER\.ljust\(\d+\)\}', r'${BROWSER}', script_content)

        # FORCE CHROME: Ensure any browser opening call uses chrome
        script_content = re.sub(r'\bfirefox\b', 'chrome', script_content, flags=re.IGNORECASE)
        script_content = re.sub(r'\bff\b', 'chrome', script_content, flags=re.IGNORECASE)

        # Inject Chrome options to disable notifications and password manager if using Open Browser
        if "Open Browser" in script_content and "options=" not in script_content:
            chrome_options_str = 'add_argument("--disable-notifications"); add_argument("--disable-infobars"); add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2, "credentials_enable_service": False, "profile.password_manager_enabled": False})'
            script_content = re.sub(r'(Open Browser\s+\S+\s+\S+)', rf'\1    options={chrome_options_str}', script_content)

        # Ensure Keywords section has Wait And Click / Wait And Input if missing
        if "Wait And Click" not in script_content:
            keywords_block = """
*** Keywords ***
Wait And Click
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    20s
    Click Element    ${locator}

Wait And Input
    [Arguments]    ${locator}    ${text}
    Wait Until Element Is Visible    ${locator}    20s
    Input Text    ${locator}    ${text}
"""
            script_content += keywords_block
            
        with open("temp.robot", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        # Execute robot framework script using current python executable
        result = subprocess.run([sys.executable, "-m", "robot", "temp.robot"], capture_output=True, text=True)
        
        status = "success" if result.returncode == 0 else "failed"
        
        return {
            "status": status,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "stdout": "",
            "stderr": str(e)
        }
    finally:
        selenium_service.is_executing = False
        print("[DEBUG] /run-test: Setting is_executing = False")
