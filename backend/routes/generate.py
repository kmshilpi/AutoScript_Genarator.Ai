from fastapi import APIRouter, HTTPException
from services.selenium_service import SeleniumService
from services.ai_service import AIService

router = APIRouter()
selenium_service = SeleniumService()

@router.get("/generate-script")
async def generate_script():
    try:
        selenium_service.sync_recorded_steps()
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

@router.get("/generate-testcase")
async def generate_testcase():
    try:
        selenium_service.sync_recorded_steps()
        steps = selenium_service.get_steps()
        if not steps:
            return {"error": "No steps recorded. Please perform actions."}
        
        json_data = AIService.generate_test_case_json(steps)
        return {"status": "success", "testcase": json_data}
    except Exception as e:
        print(f"[API ERROR] /generate-testcase: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/generate-bdd")
async def generate_bdd():
    try:
        selenium_service.sync_recorded_steps()
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

@router.get("/generate-robot")
async def generate_robot():
    try:
        selenium_service.sync_recorded_steps()
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

@router.get("/generate-all")
async def generate_all():
    try:
        selenium_service.sync_recorded_steps()
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

@router.get("/analyze")
async def analyze_with_ai():
    try:
        selenium_service.sync_recorded_steps()
        steps = selenium_service.get_steps()
        analysis = AIService.analyze_steps(steps)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        print(f"[API ERROR] /analyze: {e}")
        return {"status": "error", "message": str(e)}
