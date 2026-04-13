from fastapi import APIRouter
from services.selenium_service import SeleniumService
from models.automation import ActionRequest, NavigationRequest, RecordRequest

router = APIRouter()
selenium_service = SeleniumService()

@router.post("/")
@router.post("/record")
async def record_action(req: RecordRequest):
    print(f"\n[API REQUEST] /record received:")
    print(f"Action: {req.action}")
    print(f"Selector: {req.selector}")
    print(f"Value: {req.value}")
    
    try:
        recorded = selenium_service.record_step(
            action=req.action,
            value=req.value,
            selector=req.selector,
            selector_type=req.selector_type,
            element_id=req.element_id,
            element_name=req.element_name,
            data_testid=req.data_testid,
            tag_name=req.tag_name,
            placeholder=req.placeholder,
            inner_text=req.inner_text
        )
        if not recorded:
            print("[API] Step ignored (duplicate)")
            return {"status": "ignored", "message": "Duplicate step ignored"}
        
        print(f"[API] Step recorded successfully. Total steps now: {len(selenium_service.get_steps())}")
        return {"status": "success", "message": f"Action '{req.action}' recorded"}
    except Exception as e:
        print(f"[API ERROR] /record: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/navigate")
async def navigate(req: NavigationRequest):
    try:
        return selenium_service.navigate(req.url)
    except Exception as e:
        print(f"[API ERROR] /navigate: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/click")
async def click(req: ActionRequest):
    try:
        return selenium_service.click(req.selector, req.selector_type)
    except Exception as e:
        print(f"[API ERROR] /click: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/input")
async def input_text(req: ActionRequest):
    try:
        return selenium_service.type_text(req.selector, req.value, req.selector_type)
    except Exception as e:
        print(f"[API ERROR] /input: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/steps")
async def get_steps():
    try:
        # Sync steps from browser before returning
        steps = selenium_service.sync_browser_steps()
        return {"status": "success", "steps": steps}
    except Exception as e:
        print(f"[API ERROR] /steps: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/clear")
@router.post("/reset")
async def clear_steps():
    try:
        selenium_service.clear_steps()
        return {"status": "success", "message": "Steps cleared"}
    except Exception as e:
        print(f"[API ERROR] /clear: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/open-tab")
async def open_tab(req: NavigationRequest):
    """Opens a new browser tab and navigates to the given URL."""
    try:
        return selenium_service.open_new_tab(req.url)
    except Exception as e:
        print(f"[API ERROR] /open-tab: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/tabs")
async def get_tabs():
    """Returns info about all open browser tabs."""
    try:
        return selenium_service.get_tabs()
    except Exception as e:
        print(f"[API ERROR] /tabs: {e}")
        return {"status": "error", "message": str(e)}

