import os
import time
import fnmatch
from typing import Dict, List, Optional, Set, Callable
from datetime import datetime
import logging

from app.core.schemas import DirectoryStructure
from app.core.config import settings

logger = logging.getLogger("autodoc.scanner")

class DirectoryScanner:
    """Scanner for project directories that builds structure and tracks files."""
    
    def __init__(
        self, 
        project_path: str, 
        excluded_dirs: Optional[List[str]] = None, 
        excluded_files: Optional[List[str]] = None
    ):
        """
        Initialize the directory scanner.
        
        Args:
            project_path: Path to the project directory
            excluded_dirs: List of directory names to exclude
            excluded_files: List of file patterns to exclude
        """
        self.project_path = os.path.abspath(project_path)
        self.excluded_dirs = excluded_dirs or settings.DEFAULT_EXCLUDED_DIRS
        self.excluded_files = excluded_files or settings.DEFAULT_EXCLUDED_FILES
        
    def is_python_file(self, filename: str) -> bool:
        """Check if a file is a Python file."""
        return filename.endswith('.py')
    
    def should_exclude(self, path: str) -> bool:
        """Check if a path should be excluded from documentation."""
        basename = os.path.basename(path)
        
        if os.path.isdir(path):
            return basename in self.excluded_dirs
            
        if os.path.isfile(path):
            for pattern in self.excluded_files:
                if fnmatch.fnmatch(basename, pattern):
                    return True
            
            current_dir = os.path.dirname(path)
            while current_dir != self.project_path:
                if os.path.basename(current_dir) in self.excluded_dirs:
                    return True
                current_dir = os.path.dirname(current_dir)
        
        return False
    
    def get_all_python_files(self) -> List[str]:
        """Get all Python files in the project directory."""
        python_files = []
        
        logger.debug(f"Scanning directory: {self.project_path}")
        logger.debug(f"Excluded dirs: {self.excluded_dirs}")
        logger.debug(f"Excluded files: {self.excluded_files}")
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                logger.debug(f"Scanning directory: {root}")
                logger.debug(f"Found directories: {dirs}")
                logger.debug(f"Found files: {files}")
                
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
                logger.debug(f"After filtering directories: {dirs}")
                
                for file in files:
                    if not self.is_python_file(file):
                        logger.debug(f"Skipping non-Python file: {file}")
                        continue
                        
                    file_path = os.path.join(root, file)
                    if self.should_exclude(file_path):
                        logger.debug(f"Excluding file: {file_path}")
                        continue
                    
                    logger.debug(f"Adding Python file: {file_path}")
                    python_files.append(file_path)
            
            logger.debug(f"Total Python files found: {len(python_files)}")
            logger.debug(f"Python files: {python_files}")
            return python_files
            
        except Exception as e:
            logger.error(f"Error scanning directory: {str(e)}")
            raise
    
    def get_project_structure(self) -> DirectoryStructure:
        """
        Generate a recursive structure representing the project directory.
        
        Returns:
            DirectoryStructure object with the project hierarchy
        """
        def create_structure(path: str, name: str) -> DirectoryStructure:
            """Recursively create directory structure."""
            if os.path.isfile(path):
                return DirectoryStructure(
                    name=name,
                    type="file"
                )
            
            children = []
            
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if self.should_exclude(item_path):
                    continue
                
                if os.path.isfile(item_path) and not self.is_python_file(item):
                    continue
                
                children.append(create_structure(item_path, item))
            
            return DirectoryStructure(
                name=name,
                type="directory",
                children=children
            )
        
        return create_structure(
            self.project_path, 
            os.path.basename(self.project_path)
        )