import os
import time
import threading
from typing import Dict, List, Set, Callable, Optional
import logging

logger = logging.getLogger("autodoc.watcher")

class FileSystemWatcher:
    """Watches a directory for changes to Python files."""
    
    def __init__(
        self, 
        directory: str, 
        callback: Callable[[str], None], 
        interval: int = 1,
        file_filter: Optional[Callable[[str], bool]] = None
    ):
        """
        Initialize the file system watcher.
        
        Args:
            directory: Directory to watch
            callback: Function to call when a file changes
            interval: Polling interval in seconds
            file_filter: Optional function to filter files to watch
        """
        self.directory = os.path.abspath(directory)
        self.callback = callback
        self.interval = interval
        self.file_filter = file_filter or (lambda _: True)
        self.stopped = threading.Event()
        self.modified_files: Set[str] = set()
        self.file_mtimes: Dict[str, float] = {}
        self._thread = None
        
        
        self._scan_files()
        
    def _scan_files(self):
        """Scan all files in the directory and record their modification times."""
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                if not self.file_filter(file_path):
                    continue
                
                try:
                    
                    mtime = os.path.getmtime(file_path)
                    self.file_mtimes[file_path] = mtime
                except OSError:
                    
                    continue
    
    def _check_for_changes(self):
        """Check for modified files and trigger callbacks."""
        
        current_files = set()
        
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                if not self.file_filter(file_path):
                    continue
                
                current_files.add(file_path)
                
                try:
                    
                    mtime = os.path.getmtime(file_path)
                    
                    if file_path in self.file_mtimes:
                        if mtime > self.file_mtimes[file_path]:
                            
                            self.modified_files.add(file_path)
                            self.file_mtimes[file_path] = mtime
                    else:
                        
                        self.modified_files.add(file_path)
                        self.file_mtimes[file_path] = mtime
                except OSError:
                    
                    continue
        
        
        for file_path in list(self.file_mtimes.keys()):
            if file_path not in current_files:
                
                del self.file_mtimes[file_path]
        
        
        if self.modified_files:
            for file_path in self.modified_files:
                try:
                    self.callback(file_path)
                except Exception as e:
                    logger.error(f"Error processing modified file {file_path}: {str(e)}")
            
            
            self.modified_files.clear()
    
    def start(self):
        """Start watching for file changes in a background thread."""
        if self._thread is not None:
            return
        
        self.stopped.clear()
        
        def _watch():
            """Watch loop."""
            while not self.stopped.is_set():
                self._check_for_changes()
                self.stopped.wait(self.interval)
        
        self._thread = threading.Thread(target=_watch, daemon=True)
        self._thread.start()
        logger.info(f"Started watching directory: {self.directory}")
    
    def stop(self):
        """Stop watching for file changes."""
        if self._thread is None:
            return
        
        self.stopped.set()
        self._thread.join(timeout=2.0)
        self._thread = None
        logger.info(f"Stopped watching directory: {self.directory}")