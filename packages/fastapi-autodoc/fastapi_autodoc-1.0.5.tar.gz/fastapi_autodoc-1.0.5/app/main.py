from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
import os
import traceback
import logging
from app.api.router import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.DEBUG)

def create_app() -> FastAPI:
    """
    Create and return a FastAPI app instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Automatically generate documentation for Python projects",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.mount  ("/static", StaticFiles(directory="app/static"), name="static")


    @app.middleware("http")
    async def error_handling_middleware(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"detail": str(e), "traceback": traceback.format_exc()}
            )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", response_class=RedirectResponse)
    async def root():
        return RedirectResponse(url=f"{settings.API_V1_STR}/documentation/dashboard")

    
    @app.get("/health") 
    async def health():
        """Health check endpoint."""
        return {"status": "ok"}
    
    @app.get("/view/{project_path:path}")
    async def view_documentation(project_path: str):
        """
        Dynamically serve the documentation for a given project path.
        """
        
        docs_path = os.path.join(project_path, "docs", "index.html")

        
        if not os.path.exists(docs_path):
            raise HTTPException(status_code=404, detail="Documentation not found for this project")

        
        return FileResponse(docs_path)
    project_docs_path = os.path.join(settings.PROJECT_PATH, "docs")

    @app.on_event("startup")
    async def mount_docs_directory():
        if not os.path.exists(project_docs_path):
            logger.warning(f"Documentation directory not found at {project_docs_path}")
            logger.warning("Run 'fastapi-autodoc generate' first to create documentation")
            # Create an empty docs directory with a placeholder
            os.makedirs(project_docs_path, exist_ok=True)
            with open(os.path.join(project_docs_path, "index.html"), "w") as f:
                f.write("""<!DOCTYPE html>
    <html>
    <head>
        <title>Documentation Not Generated</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #e74c3c; }
            .container { max-width: 800px; margin: 0 auto; }
            .steps { background-color: #f9f9f9; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Documentation Not Generated Yet</h1>
            <p>It looks like you haven't generated documentation for this project yet.</p>
            
            <div class="steps">
                <h2>How to generate documentation:</h2>
                <ol>
                    <li>Open a terminal in your project directory</li>
                    <li>Run: <code>fastapi-autodoc generate</code></li>
                    <li>Once completed, refresh this page</li>
                </ol>
            </div>
            
            <p>For more information, refer to the FastAPI AutoDoc documentation.</p>
        </div>
    </body>
    </html>""")
    
    app.mount("/docs", StaticFiles(directory=project_docs_path), name="docs")


    return app

app= create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)