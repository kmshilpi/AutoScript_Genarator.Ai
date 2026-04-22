from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.selenium_service import SeleniumService
from services.ai_service import AIService

router = APIRouter()
selenium_service = SeleniumService()

@router.get("/generate-script")
async def generate_script():
    try:
        # Stop recording/syncing immediately
        selenium_service.is_syncing = False
        selenium_service.is_generating = True
        print("[DEBUG] /generate-script: Stopped sync and started generation.")
        
        # Rely on steps already captured by background sync
        
        # Rely on background sync thread
        steps = selenium_service.get_steps()
        if not steps:
            return {"error": "No steps recorded. Please perform actions."}
        
        print(f"\n[GENERATE] Python Script")
        print(f"Total Steps: {len(steps)}")
        print(f"Steps Data: {steps}")
        
        script = AIService.generate_selenium_script(steps)
        return {"status": "success", "script": script}
    except Exception as e:
        print(f"[API ERROR] /generate-script: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        selenium_service.is_generating = False
        # Do NOT restart syncing automatically as requested

@router.get("/generate-testcase")
async def generate_testcase():
    try:
        selenium_service.is_syncing = False
        selenium_service.is_generating = True
        print("[DEBUG] /generate-testcase: Stopped sync and started generation.")
        
        # Rely on background sync thread
        steps = selenium_service.get_steps()
        if not steps:
            return {"error": "No steps recorded. Please perform actions."}
        
        json_data = AIService.generate_test_case_json(steps)
        return {"status": "success", "testcase": json_data}
    except Exception as e:
        print(f"[API ERROR] /generate-testcase: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        selenium_service.is_generating = False

@router.get("/generate-bdd")
async def generate_bdd():
    try:
        selenium_service.is_syncing = False
        selenium_service.is_generating = True
        print("[DEBUG] /generate-bdd: Stopped sync and started generation.")
        
        # Rely on background sync thread
        steps = selenium_service.get_steps()
        if not steps:
            return {"error": "No steps recorded. Please perform actions."}
        
        print(f"\n[GENERATE] BDD Scenario")
        print(f"Total Steps: {len(steps)}")
        
        bdd = AIService.generate_bdd_test_case(steps)
        return {"status": "success", "bdd": bdd}
    except Exception as e:
        print(f"[API ERROR] /generate-bdd: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        selenium_service.is_generating = False

@router.get("/generate-robot")
async def generate_robot():
    try:
        selenium_service.is_syncing = False
        selenium_service.is_generating = True
        print("[DEBUG] /generate-robot: Stopped sync and started generation.")
        
        # Rely on background sync thread
        steps = selenium_service.get_steps()
        if not steps:
            return {"error": "No steps recorded. Please perform actions."}
        
        print(f"\n[GENERATE] Robot Script")
        print(f"Total Steps: {len(steps)}")
        
        robot = AIService.generate_robot_script(steps)
        return {"status": "success", "robot": robot}
    except Exception as e:
        print(f"[API ERROR] /generate-robot: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        selenium_service.is_generating = False

@router.get("/generate-all")
async def generate_all():
    try:
        selenium_service.is_syncing = False
        selenium_service.is_generating = True
        print("[DEBUG] /generate-all: Stopped sync and started generation.")
        
        # Rely on background sync thread
        steps = selenium_service.get_steps()
        if not steps:
            return {"error": "No steps recorded. Please perform actions."}
        
        print(f"\n[GENERATE ALL] Started")
        print(f"Total Steps: {len(steps)}")
        print(f"Steps Data: {steps}")
        
        result = AIService.generate_all_formats(steps)
        return {"status": "success", **result}
    except Exception as e:
        print(f"[API ERROR] /generate-all: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        selenium_service.is_generating = False
        print("[DEBUG] /generate-all: Generation complete. Sync remains stopped.")

@router.get("/analyze")
async def analyze_with_ai():
    try:
        # Rely on background sync thread
        steps = selenium_service.get_steps()
        analysis = AIService.analyze_steps(steps)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        print(f"[API ERROR] /analyze: {e}")
        return {"status": "error", "message": str(e)}

class LocatorRequest(BaseModel):
    html: str

@router.post("/generate-locator")
async def generate_locator(req: LocatorRequest):
    """
    Accepts raw HTML and returns an expert-generated XPath locator.
    Follows strict rules: ID first, text second, stable attrs third.
    Avoids dynamic attributes and absolute XPaths.
    """
    try:
        if not req.html or not req.html.strip():
            return {"status": "error", "message": "HTML input is empty. Please paste HTML."}
        
        print(f"[DEBUG] /generate-locator: Analyzing HTML ({len(req.html)} chars)")
        result = AIService.generate_locator(req.html)
        return {"status": "success", **result}
    except Exception as e:
        print(f"[API ERROR] /generate-locator: {e}")
        return {"status": "error", "message": str(e)}

class ScriptRefactorRequest(BaseModel):
    script: str

@router.post("/refactor-robot")
async def refactor_robot(req: ScriptRefactorRequest):
    """
    Accepts a Robot Framework script and returns a fully refactored version.
    - Generates stable, unique locators (ID → text → stable attrs)
    - Creates reusable keywords: Wait And Click, Wait And Input With Validation
    - Fixes input handling (clear-before-type, full value, verify after input)
    - Detects Angular/Material UI and applies text-based locators
    """
    try:
        if not req.script or not req.script.strip():
            return {"status": "error", "message": "Script is empty. Please paste a Robot Framework script."}
        
        print(f"[DEBUG] /refactor-robot: Refactoring script ({len(req.script)} chars)")
        result = AIService.refactor_robot_script(req.script)
        return {"status": "success", **result}
    except Exception as e:
        print(f"[API ERROR] /refactor-robot: {e}")
        return {"status": "error", "message": str(e)}
