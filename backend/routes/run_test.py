from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
import sys
import re

router = APIRouter()

class RunRequest(BaseModel):
    script: str

@router.post("")
@router.post("/")
async def run_test_script(request: RunRequest):
    try:
        script_content = request.script
        
        # Safeguard: Inject Settings and Library if missing
        if "*** Settings ***" not in script_content:
            script_content = "*** Settings ***\nLibrary    SeleniumLibrary\n\n" + script_content
            
        # Safeguard: Fix AI formatting for Wait Until Keyword Succeeds spacing
        script_content = re.sub(r'Wait Until Keyword Succeeds\s+15x\s+2s', r'Wait Until Keyword Succeeds    15x    2s', script_content)
        
        # Safeguard: Auto-prefix #id locators with css= if missing
        script_content = re.sub(r'(\s+)#([a-zA-Z0-9_\-]+)', r'\1css=#\2', script_content)
            
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
