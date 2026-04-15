from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import browser, record, generate, run_test
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Automation Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(browser.router, prefix="/api/browser", tags=["browser"])
app.include_router(record.router, prefix="/api/record", tags=["record"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])
app.include_router(run_test.router, prefix="/api/run-test", tags=["run_test"])

# Direct access as requested
app.include_router(record.router, tags=["record"])

@app.get("/")
async def root():
    return {"message": "AI Automation Agent API (Refactored) is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
