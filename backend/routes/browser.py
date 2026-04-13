from fastapi import APIRouter
from services.selenium_service import SeleniumService

router = APIRouter()
selenium_service = SeleniumService()

@router.post("/start")
async def start_browser():
    try:
        selenium_service.clear_steps()
        return selenium_service.start_browser()
    except Exception as e:
        print(f"[API ERROR] /start: {e}")
        return {"status": "error", "message": f"Could not start browser: {e}"}

@router.post("/stop")
async def stop_browser():
    try:
        return selenium_service.stop_browser()
    except Exception as e:
        print(f"[API ERROR] /stop: {e}")
        return {"status": "error", "message": f"Could not stop browser: {e}"}
