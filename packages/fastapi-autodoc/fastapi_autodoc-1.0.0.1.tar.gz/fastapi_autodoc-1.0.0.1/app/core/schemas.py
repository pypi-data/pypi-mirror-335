from pydantic import BaseModel, validator, Field
from typing import Dict, List, Optional, Any, Set
import os
from datetime import datetime

class ProjectConfig(BaseModel):
    """Configuration for a project to be documented."""
    
    project_path: str
    watch_mode: bool = False
    include_private: bool = False
    excluded_dirs: List[str] = ["__pycache__", ".git", ".venv", "venv", "env", "node_modules"]
    excluded_files: List[str] = []
    doc_output_path: str = "docs"
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that the project path exists and is a directory."""
        if not os.path.exists(v):
            raise ValueError(f"Project path '{v}' does not exist")
        if not os.path.isdir(v):
            raise ValueError(f"Project path '{v}' is not a directory")
        return os.path.abspath(v)
    
    @validator('doc_output_path')
    def validate_output_path(cls, v, values):
        """Ensure output path is valid."""
        if os.path.isabs(v):
            return v
        
        
        if 'project_path' in values:
            return os.path.join(values['project_path'], v)
        return v

class FunctionInfo(BaseModel):
    """Information about a function in a Python module."""
    
    name: str
    docstring: Optional[str] = None
    params: List[str] = []
    return_type: Optional[str] = None
    decorators: List[str] = []
    line_number: int
    source_code: Optional[str] = None
    is_async: bool = False

class MethodInfo(FunctionInfo):
    """Information about a method in a class."""
    pass

class ClassInfo(BaseModel):
    """Information about a class in a Python module."""
    
    name: str
    docstring: Optional[str] = None
    methods: Dict[str, MethodInfo] = {}
    base_classes: List[str] = []
    decorators: List[str] = []
    line_number: int
    source_code: Optional[str] = None
    class_variables: Dict[str, Any] = {}

class ImportInfo(BaseModel):
    """Information about imports in a Python module."""
    
    module: str
    names: List[str] = []
    alias: Optional[str] = None

class FileDocumentation(BaseModel):
    """Documentation for a single Python file."""
    
    file_path: str
    module_docstring: Optional[str] = None
    classes: Dict[str, ClassInfo] = {}
    functions: Dict[str, FunctionInfo] = {}
    imports: List[ImportInfo] = []
    last_modified: Optional[datetime] = None
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate that the file path exists."""
        if not os.path.exists(v):
            raise ValueError(f"File path '{v}' does not exist")
        return os.path.abspath(v)

class DirectoryStructure(BaseModel):
    """Recursive model representing a directory structure."""
    
    name: str
    type: str  
    children: Optional[List['DirectoryStructure']] = None


DirectoryStructure.update_forward_refs()

class ProjectDocumentation(BaseModel):
    """Complete documentation for a project."""
    
    project_path: str
    structure: DirectoryStructure
    files: Dict[str, FileDocumentation] = {}
    last_updated: datetime = Field(default_factory=datetime.now)
    config: ProjectConfig = None
    
    @validator('project_path')
    def validate_project_path(cls, v):
        """Validate that the project path exists and is a directory."""
        if not os.path.exists(v):
            raise ValueError(f"Project path '{v}' does not exist")
        if not os.path.isdir(v):
            raise ValueError(f"Project path '{v}' is not a directory")
        return os.path.abspath(v)

class DocumentationResult(BaseModel):
    """Result of a documentation generation process."""
    
    project_path: str
    total_files: int
    total_functions: int
    total_classes: int
    timestamp: datetime = Field(default_factory=datetime.now)
    output_path: str
    documentation_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "total_files": 10,
                "total_functions": 25,
                "total_classes": 5,
                "timestamp": "2023-01-01T12:00:00",
                "output_path": "/path/to/project/docs"
            }
        }

class ErrorResponse(BaseModel):
    
    detail: str
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Project path not found"
            }
        }