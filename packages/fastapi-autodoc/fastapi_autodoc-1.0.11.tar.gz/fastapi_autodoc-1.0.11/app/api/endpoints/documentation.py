from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, Any, Optional
import os
import time

from app.core.schemas import (
    ProjectConfig, 
    DocumentationResult, 
    ProjectDocumentation
)
from app.services.doc_generator import DocGenerator
from app.core.config import settings

router = APIRouter()


documentation_store: Dict[str, ProjectDocumentation] = {}

active_watchers: Dict[str, Any] = {}

@router.post("/", response_model=DocumentationResult)
async def document_project(
    config: ProjectConfig,
    background_tasks: BackgroundTasks
):
    """
    Document a project and generate documentation files.
    
    Optionally start watching the project for file changes.
    """
    if not os.path.exists(config.project_path):
        raise HTTPException(status_code=404, detail="Project path not found")
    
    if not os.path.isdir(config.project_path):
        raise HTTPException(status_code=400, detail="Path must be a directory")
    
    doc_generator = DocGenerator(config)
    
    try:
        # Generate documentation
        doc_result = doc_generator.document_project()
        documentation_store[config.project_path] = doc_result
        
        if config.watch_mode:
            # Stop existing watcher if any
            if config.project_path in active_watchers:
                active_watchers[config.project_path].stop_watching()
                
            # Start watching for changes
            doc_generator.start_watching()
            active_watchers[config.project_path] = doc_generator
        
        return doc_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation failed: {str(e)}")

@router.get("/projects")
async def list_documented_projects():
    """
    List all projects that have been documented.
    """
    projects = []
    for path, doc in documentation_store.items():
        project_name = os.path.basename(path)
        is_watching = path in active_watchers
        
        projects.append({
            "name": project_name,
            "path": path,
            "watching": is_watching,
            "last_updated": doc.timestamp,
            "stats": {
                "files": doc.total_files,
                "functions": doc.total_functions,
                "classes": doc.total_classes
            }
        })
    
    return {"projects": projects}

@router.get("/project/{project_path:path}", response_model=ProjectDocumentation)
async def get_project_documentation(project_path: str):
    """
    Get the documentation for a specific project.
    """
    if project_path not in documentation_store:
        raise HTTPException(status_code=404, detail="Documentation not found for this project")
    
    return documentation_store[project_path]

@router.delete("/watch/{project_path:path}")
async def stop_watching_project(project_path: str):
    """
    Stop watching a project for changes.
    """
    if project_path not in active_watchers:
        raise HTTPException(status_code=404, detail="Project not being watched")
    
    try:
        active_watchers[project_path].stop_watching()
        del active_watchers[project_path]
        return {"message": f"Stopped watching {project_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop watcher: {str(e)}")

@router.get("/view/{project_path:path}")
async def view_documentation(project_path: str):
    """
    View the HTML documentation for a project.
    """
    if project_path not in documentation_store:
        raise HTTPException(status_code=404, detail="Documentation not found for this project")
    
    project_doc = documentation_store[project_path]
    
    # Construct the path to the index.html file
    html_path = os.path.join(
        project_path, 
        project_doc.config.doc_output_path if hasattr(project_doc, 'config') else "docs",
        "index.html"
    )
    
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Documentation file not found")
    
    return FileResponse(html_path)

@router.post("/refresh/{project_path:path}", response_model=DocumentationResult)
async def refresh_documentation(project_path: str):
    """
    Manually refresh the documentation for a project.
    """
    if project_path not in documentation_store:
        raise HTTPException(status_code=404, detail="Project not found in documentation store")
    
    existing_doc = documentation_store[project_path]
    config = existing_doc.config
    
    doc_generator = DocGenerator(config)
    
    try:
        # Generate documentation
        project_doc = doc_generator.document_project()
        documentation_store[project_path] = project_doc
        
        # Generate output files and get result
        doc_result = doc_generator.generate_output()
        
        return doc_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation refresh failed: {str(e)}")

@router.get("/dashboard", response_class=HTMLResponse)
async def documentation_dashboard():
    """
    Return the HTML dashboard for managing documentation.
    """
    template_path = os.path.join(os.path.dirname(__file__), "../../templates/dashboard.html")
    template_path = os.path.abspath(template_path)

    with open(template_path, "r") as f:
        dashboard_html = f.read()
    
    return HTMLResponse(content=dashboard_html)

@router.get("/status")
async def get_service_status():
    """
    Get the status of the documentation service.
    """
    return {
        "status": "running",
        "documented_projects": len(documentation_store),
        "active_watchers": len(active_watchers),
        "service_uptime": time.time() - settings.start_time
    }