import os
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import logging
import threading
import json

from app.core.schemas import (
    ProjectConfig, 
    ProjectDocumentation, 
    FileDocumentation, 
    DocumentationResult
)
from app.services.file_parser import FileParser
from app.services.directory_scanner import DirectoryScanner
from app.services.watcher import FileSystemWatcher
from app.core.config import settings

logger = logging.getLogger("autodoc.generator")

class DocGenerator:
    """
    Main documentation generator service.
    Coordinates parsing files and generating documentation.
    """
    
    def __init__(self, config: ProjectConfig):
        """
        Initialize the documentation generator.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.parser = FileParser(include_private=config.include_private)
        self.scanner = DirectoryScanner(
            project_path=config.project_path,
            excluded_dirs=config.excluded_dirs or settings.DEFAULT_EXCLUDED_DIRS,
            excluded_files=config.excluded_files or settings.DEFAULT_EXCLUDED_FILES
        )
        self.watcher = None
        self._documentation = None
        self._lock = threading.Lock()  
    
    def save_documentation(self, output_path: str) -> None:
        """
        Save the documentation data to a JSON file.
        
        Args:
            output_path: Directory where the JSON file should be saved.
        """
        if not self._documentation:
            raise ValueError("No documentation has been generated yet")

        
        os.makedirs(output_path, exist_ok=True)
        
        
        doc_dict = {
            "project_path": self._documentation.project_path,
            "structure": self._documentation.structure.dict(),
            "files": {
                path: doc.dict()
                for path, doc in self._documentation.files.items()
            },
            "last_updated": self._documentation.last_updated.isoformat(),
            "config": self._documentation.config.dict() if self._documentation.config else None
        }
        
        json_path = os.path.join(output_path, "documentation.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc_dict, f, indent=4, default=str)

        logger.info(f"Documentation saved at {json_path}")
    
    def document_project(self) -> DocumentationResult:
        """Generate documentation for the entire project."""
        try:
            # Create output directories if they don't exist
            output_dir = os.path.join(self.config.project_path, self.config.doc_output_path)
            html_dir = os.path.join(output_dir, "html")
            os.makedirs(html_dir, exist_ok=True)
            
            
            files = self.scanner.get_all_python_files()
            if not files:
                raise ValueError("No Python files found in project")
            
            logger.debug(f"Found {len(files)} Python files")
            
            
            results = []
            for file_path in files:
                try:
                    result = self.document_file(file_path)
                    if result:
                        results.append(result)
                        logger.debug(f"Documented file: {file_path}")
                except Exception as e:
                    logger.error(f"Error documenting {file_path}: {str(e)}")
                    continue
            
            if not results:
                raise ValueError("No documentation generated for any files")
            
            logger.debug(f"Generated documentation for {len(results)} files")
            
            
            self.generate_output(results)
            
            
            return DocumentationResult(
            project_path=self.config.project_path,
                total_files=len(results),
                total_functions=sum(result.total_functions for result in results),
                total_classes=sum(result.total_classes for result in results),
                output_path=output_dir,
                documentation_url=f"http://localhost:8000/api/v1/documentation/view/{self.config.project_path}"
            )
            
        except Exception as e:
            logger.error(f"Documentation failed: {str(e)}")
            raise
    
    def start_watching(self) -> None:
        """Start watching the project directory for changes."""
        if self.watcher:
            
            return
        
        self.watcher = FileSystemWatcher(
            directory=self.config.project_path,
            callback=self._file_changed_callback,
            interval=settings.DEFAULT_WATCH_INTERVAL,
            file_filter=lambda f: f.endswith('.py') and not self.scanner.should_exclude(f)
        )
        
        self.watcher.start()
        logger.info(f"Started watching project: {self.config.project_path}")
    
    def stop_watching(self) -> None:
        """Stop watching the project directory."""
        if not self.watcher:
            return
        
        self.watcher.stop()
        self.watcher = None
        logger.info(f"Stopped watching project: {self.config.project_path}")
    
    def _file_changed_callback(self, file_path: str) -> None:
        """
        Callback for when a file changes.
        
        Args:
            file_path: Path to the modified file
        """
        with self._lock:
            if not self._documentation:
                
                return
            
            logger.info(f"File changed: {file_path}")
            
            
            file_doc = self.parser.parse_file(file_path)
            if file_doc:
                self._documentation.files[file_path] = file_doc
                self._documentation.last_updated = datetime.now()
                
                self.generate_output()
    
    def generate_output(self, results: Optional[List[DocumentationResult]] = None) -> None:
        """
        Generate documentation output files.
        
        Args:
            results: Optional list of DocumentationResult objects. If not provided,
                    will use stored documentation.
        """
        if not results and not self._documentation:
            raise ValueError("No documentation available to generate output")
        
        
        output_dir = os.path.abspath(self.config.doc_output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        
        self._generate_html_docs(output_dir, results or [])
        
        
        self._generate_json_docs(output_dir)
        
        
        self.save_documentation(output_dir)
        
        
        if results:
            total_files = len(results)
            total_functions = sum(
                result.total_functions for result in results
            )
            total_classes = sum(
                result.total_classes for result in results
            )
        else:
            total_files = len(self._documentation.files)  
            total_functions = sum(
                len(doc.functions) for doc in self._documentation.files.values()
        )
        total_classes = sum(
            len(doc.classes) for doc in self._documentation.files.values()
        )

        
        logger.info(f"Documentation generated: {total_files} files, {total_functions} functions, {total_classes} classes")
        
    def _generate_html_docs(self, output_dir: str, results: List[DocumentationResult]) -> None:
        """
        Generate HTML documentation files.
        
        Args:
            output_dir: Directory to write HTML files
            results: List of DocumentationResult objects
        """
        if not self._documentation:
            raise ValueError("No documentation has been generated yet")
        
        html_dir = os.path.join(output_dir, "html")
        os.makedirs(html_dir, exist_ok=True)
        
        
        css_path = os.path.join(output_dir, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write("""
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                color: #333;
                background-color: #0d9488;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 30px;
                background-color: #f0fdfa;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
            header {
                background-color: #0d9488;
                color: white;
                padding: 20px;
                margin-bottom: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 500;
            }
            h2 {
                color: #0f766e;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
                margin-top: 40px;
                font-size: 22px;
            }
            h3 {
                color: #0d9488;
                margin-top: 25px;
                font-size: 18px;
                font-weight: 500;
            }
            pre, code {
                font-family: 'Courier New', Courier, monospace;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
            pre {
                padding: 15px;
                overflow: auto;
                border: 1px solid #ddd;
            }
            code {
                padding: 2px 4px;
                font-size: 90%;
            }
            /* Accordion styles */
            .accordion {
                margin-bottom: 10px;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
                background-color: white;
            }
            .accordion:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
                transform: translateY(-2px);
            }
            .accordion-header {
                background-color: #f8f9fa;
                padding: 15px 20px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background-color 0.2s;
                border-bottom: 1px solid #e1e4e8;
            }
            .accordion-header:hover {
                background-color: #f1f1f1;
            }
            .accordion-header h3 {
                margin: 0;
                font-size: 16px;
                color: #0f766e;
            }
            .accordion-content {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease-out;
                background-color: #fff;
                padding: 0 20px;
            }
            .accordion-content.active {
                max-height: 1000px;
                padding: 20px;
                transition: max-height 0.5s ease-in;
            }
            .accordion-icon {
                width: 20px;
                height: 20px;
                position: relative;
            }
            .accordion-icon:before,
            .accordion-icon:after {
                content: '';
                position: absolute;
                background-color: #0d9488;
                transition: transform 0.3s ease;
            }
            .accordion-icon:before {
                width: 2px;
                height: 16px;
                top: 2px;
                left: 9px;
            }
            .accordion-icon:after {
                width: 16px;
                height: 2px;
                top: 9px;
                left: 2px;
            }
            .accordion.active .accordion-icon:before {
                transform: rotate(90deg);
            }
            .file-meta {
                color: #666;
                font-size: 14px;
                margin-bottom: 15px;
                display: flex;
                gap: 15px;
            }
            .file-meta span {
                display: inline-flex;
                align-items: center;
            }
            .file-meta i {
                margin-right: 5px;
                display: inline-block;
                width: 16px;
                height: 16px;
                background-size: contain;
                background-repeat: no-repeat;
            }
            .file-purpose {
                background-color: #f8f9fa;
                border-left: 4px solid #0d9488;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 3px 3px 0;
            }
            .navigation {
                margin-bottom: 30px;
            }
            .navigation a {
                display: inline-block;
                padding: 10px 20px;
                background-color: #0d9488;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
            }
            .navigation a:hover {
                background-color: #0f766e;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                transform: translateY(-2px);
            }
            .folder-structure {
                font-family: monospace;
                white-space: pre;
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border: 1px solid #ddd;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            }
            .summary-box {
                background-color: #f1f8ff;
                border: 1px solid #c8e1ff;
                border-radius: 6px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }
            .summary-box ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            .view-details {
                display: inline-block;
                margin-top: 10px;
                color: #0d9488;
                text-decoration: none;
                font-weight: 500;
                padding: 5px 10px;
                border-radius: 4px;
                transition: background-color 0.2s;
            }
            .view-details:hover {
                background-color: #e6fffa;
                text-decoration: underline;
            }
            .directory-title {
                background-color: #e6fffa;
                padding: 10px 15px;
                border-radius: 4px;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: 500;
                color: #0f766e;
                border-left: 4px solid #0d9488;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            }
            .content-section {
                margin-bottom: 30px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                padding: 20px;
                border: 1px solid #e1e4e8;
            }
            """)
        
        
        js_path = os.path.join(output_dir, "script.js")
        with open(js_path, "w", encoding="utf-8") as f:
            f.write("""
            document.addEventListener('DOMContentLoaded', function() {
                
                const accordionHeaders = document.querySelectorAll('.accordion-header');
                
                
                accordionHeaders.forEach(header => {
                    header.addEventListener('click', function() {
                        
                        const accordion = this.parentElement;
                        accordion.classList.toggle('active');
                        
                        
                        const content = this.nextElementSibling;
                        content.classList.toggle('active');
                    });
                });
            });
            """)
        
        
        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Project Documentation - {os.path.basename(self.config.project_path)}</title>
                <link rel="stylesheet" href="style.css">
            </head>
            <body>
                <div class="container">
                    <header>
                        <h1>Documentation for {os.path.basename(self.config.project_path)}</h1>
                        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    </header>
                    
                    <div class="summary-box">
                        <h2>Project Overview</h2>
                        <p>This documentation provides a detailed explanation of each file in the project. Click on any file to view its description.</p>
                        <ul>
                            <li><strong>Project Path:</strong> {self.config.project_path}</li>
                            <li><strong>Total Files:</strong> {len(self._documentation.files)}</li>
                            <li><strong>Total Functions:</strong> {sum(len(doc.functions) for doc in self._documentation.files.values())}</li>
                            <li><strong>Total Classes:</strong> {sum(len(doc.classes) for doc in self._documentation.files.values())}</li>
                        </ul>
                    </div>
                    
                    <h2>Project Structure</h2>
                    <div class="folder-structure">
                    {self._generate_folder_structure()}
                    </div>
                    
                    <h2>Files Documentation</h2>
            """)
            
            
            files_by_dir = {}
            for file_path, file_doc in self._documentation.files.items():
                rel_path = os.path.relpath(file_path, self.config.project_path)
                dir_name = os.path.dirname(rel_path) or "root"
                
                if dir_name not in files_by_dir:
                    files_by_dir[dir_name] = []
                
                files_by_dir[dir_name].append((file_path, rel_path, file_doc))
            
            for dir_name, files in sorted(files_by_dir.items()):
                if dir_name != "root":
                    f.write(f'<div class="directory-title">{dir_name}</div>')
                else:
                    f.write('<div class="directory-title">Root Directory</div>')
                
                for file_path, rel_path, file_doc in sorted(files, key=lambda x: x[1]):
                    
                    safe_path = rel_path.replace('/', '_').replace('\\', '_')
                    file_html_path = os.path.join(html_dir, f"{safe_path}.html")
                    
                    
                    self._generate_file_html(file_path, file_doc, file_html_path)
                    
                    
                    description = self._generate_file_purpose(file_path, file_doc)
                    
                    first_paragraph = description.split('</p>')[0].replace('<p>', '') if '</p>' in description else description.replace('<p>', '').replace('</p>', '')
                    
                    
                    func_count = len(file_doc.functions)
                    class_count = len(file_doc.classes)
                    
                    f.write(f"""
                    <div class="accordion">
                        <div class="accordion-header">
                            <h3>{rel_path}</h3>
                            <div class="accordion-icon"></div>
                        </div>
                        <div class="accordion-content">
                            <div class="file-meta">
                                <span><i></i>Functions: {func_count}</span>
                                <span><i></i>Classes: {class_count}</span>
                            </div>
                            <div class="file-purpose">
                                {first_paragraph}
                            </div>
                            <a href="html/{os.path.basename(file_html_path)}" class="view-details">View detailed documentation</a>
                        </div>
                    </div>
                    """)
            
            f.write("""
                </div>
                <script src="script.js"></script>
            </body>
            </html>
            """)
        
        logger.info(f"Generated HTML documentation at {output_dir}")
    
    def _generate_folder_structure(self) -> str:
        """
        Generate a text representation of the project folder structure.
        
        Returns:
            String with the folder structure
        """
        structure = []
        
        def _add_to_structure(path, prefix=""):
            if os.path.isfile(path):
                filename = os.path.basename(path)
                if filename.endswith('.py'):
                    structure.append(f"{prefix}└── {filename}")
            else:
                dirname = os.path.basename(path)
                if dirname == os.path.basename(self.config.project_path):
                    structure.append(f"{dirname}/")
                    prefix = "  "
                else:
                    structure.append(f"{prefix}└── {dirname}/")
                    prefix = prefix + "    "
                
                items = sorted(os.listdir(path))
                dirs = [item for item in items if os.path.isdir(os.path.join(path, item)) and not item.startswith('.') and item != '__pycache__' and item != self.config.doc_output_path]
                files = [item for item in items if os.path.isfile(os.path.join(path, item)) and item.endswith('.py')]
                
                for d in dirs:
                    _add_to_structure(os.path.join(path, d), prefix)
                
                for f in files:
                    structure.append(f"{prefix}└── {f}")
        
        _add_to_structure(self.config.project_path)
        return "\n".join(structure)

    def _generate_api_endpoints_summary(self) -> str:
        """
        Generate a summary of FastAPI endpoints found in the project.
        
        Returns:
            HTML string with the API endpoints summary
        """
        endpoints = []
        
        
        for file_path, file_doc in self._documentation.files.items():
            
            has_fastapi_import = any(
                imp.module == 'fastapi' or 
                (imp.module.startswith('fastapi.') and 'APIRouter' in imp.names) or
                (imp.module == 'fastapi' and 'APIRouter' in imp.names)
                for imp in file_doc.imports
            )
            
            if not has_fastapi_import:
                continue
            
            
            for func_name, func_info in file_doc.functions.items():
                docstring = func_info.docstring or ""
                
                
                endpoint_info = self._extract_endpoint_info(func_name, func_info, docstring)
                if endpoint_info:
                    endpoints.append({
                        'file': os.path.relpath(file_path, self.config.project_path),
                        'function': func_name,
                        'method': endpoint_info.get('method', 'GET'),
                        'path': endpoint_info.get('path', '/'),
                        'description': endpoint_info.get('description', ''),
                        'parameters': endpoint_info.get('parameters', []),
                        'response': endpoint_info.get('response', {})
                    })
        
        if not endpoints:
            return "<p>No API endpoints found in the project.</p>"
        
        
        html = ""
        for endpoint in endpoints:
            html += f"""
            <div class="endpoint">
                <div>
                    <span class="endpoint-method">{endpoint['method']}</span> 
                    <span class="endpoint-path">{endpoint['path']}</span>
                </div>
                <div class="endpoint-description">
                    <p>{endpoint['description']}</p>
                    <p><strong>Function:</strong> {endpoint['function']} in {endpoint['file']}</p>
                </div>
            """
            
            if endpoint['parameters']:
                html += "<div><strong>Parameters:</strong><ul>"
                for param in endpoint['parameters']:
                    html += f"<li>{param}</li>"
                html += "</ul></div>"
            
            if endpoint['response']:
                html += f"""
                <div><strong>Response:</strong> {endpoint['response'].get('description', '')}</div>
                """
            
            html += "</div>"
        
        return html

    def _extract_endpoint_info(self, func_name: str, func_info: Any, docstring: str) -> Optional[Dict[str, Any]]:
        """
        Extract API endpoint information from a function.
        
        Args:
            func_name: Name of the function
            func_info: FunctionInfo object
            docstring: Function docstring
            
        Returns:
            Dictionary with endpoint information or None if not an endpoint
        """
        
        if not (func_name.startswith('get_') or 
                func_name.startswith('post_') or 
                func_name.startswith('put_') or 
                func_name.startswith('delete_') or 
                func_name.startswith('patch_') or 
                'route' in func_name or 
                'api' in func_name or 
                'endpoint' in func_name):
            return None
        
        
        method = 'GET'
        if func_name.startswith('post_'):
            method = 'POST'
        elif func_name.startswith('put_'):
            method = 'PUT'
        elif func_name.startswith('delete_'):
            method = 'DELETE'
        elif func_name.startswith('patch_'):
            method = 'PATCH'
        
        
        path = '/'
        if '_' in func_name:
            parts = func_name.split('_')[1:]
            if parts:
                path = '/' + '/'.join(parts)
        
        
        description = docstring.split('\n')[0] if docstring else f"Endpoint for {func_name}"
        
        
        parameters = []
        if func_info.params:
            for param in func_info.params:
                if param not in ['self', 'request', 'response']:
                    parameters.append(param)
        
        
        response = {}
        if func_info.return_type:
            response['type'] = func_info.return_type
            response['description'] = f"Returns {func_info.return_type}"
        
        return {
            'method': method,
            'path': path,
            'description': description,
            'parameters': parameters,
            'response': response
        }

    def _generate_file_html(self, file_path: str, file_doc: FileDocumentation, output_path: str) -> None:
        """
        Generate HTML documentation for a single file.
        
        Args:
            file_path: Path to the source file
            file_doc: FileDocumentation object
            output_path: Path to write the HTML file
        """
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        rel_path = os.path.relpath(file_path, self.config.project_path)
        

        file_purpose = self._generate_file_purpose(file_path, file_doc)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>File Documentation - {rel_path}</title>
                <link rel="stylesheet" href="../../style.css">
                <style>
                    body {{
                        background-color: #0d9488;
                        color: #333;
                    }}
                    .container {{
                        background-color: #f0fdfa;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        border-radius: 8px;
                        max-width: 1200px;
                        margin: 20px auto;
                        padding: 30px;
                    }}
                    .method-item, .param-item {{
                        margin-bottom: 15px;
                        padding: 15px;
                        background-color: #f8f9fa;
                        border-radius: 6px;
                        border-left: 3px solid #3498db;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
                    }}
                    .method-name {{
                        color: #2c3e50;
                        font-weight: 600;
                        font-size: 16px;
                        margin-bottom: 8px;
                    }}
                    .method-signature {{
                        font-family: 'Courier New', monospace;
                        background-color: #f1f1f1;
                        padding: 6px 10px;
                        border-radius: 4px;
                        margin: 8px 0;
                        display: inline-block;
                    }}
                    .method-description {{
                        margin-top: 10px;
                        line-height: 1.5;
                    }}
                    .code-tag {{
                        background-color: #e9f5ff;
                        color: #0366d6;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Courier New', monospace;
                        font-size: 90%;
                    }}
                    .inheritance {{
                        background-color: #f1f8ff;
                        border: 1px solid #c8e1ff;
                        border-radius: 6px;
                        padding: 10px 15px;
                        margin: 15px 0;
                        font-size: 14px;
                    }}
                    .section-divider {{
                        height: 1px;
                        background-color: #e1e4e8;
                        margin: 30px 0;
                    }}
                    .file-metadata {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 15px;
                        margin: 20px 0;
                    }}
                    .file-metadata-item {{
                        background-color: #f1f8ff;
                        border-radius: 20px;
                        padding: 5px 15px;
                        font-size: 14px;
                        color: #0366d6;
                    }}
                    .content-section {{
                        margin-bottom: 30px;
                        background-color: white;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                        padding: 20px;
                        border: 1px solid #e1e4e8;
                    }}
                    .content-section h2 {{
                        margin-top: 0;
                        padding-bottom: 10px;
                        border-bottom: 1px solid #eaecef;
                    }}
                    .accordion-content {{
                        padding: 0;
                    }}
                    .accordion-content.active {{
                        padding: 20px;
                    }}
                    .method-list {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    .method-list li {{
                        margin-bottom: 10px;
                    }}
                    .import-list {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    .import-list li {{
                        margin-bottom: 8px;
                        padding: 5px 10px;
                        background-color: #f6f8fa;
                        border-radius: 4px;
                        font-family: 'Courier New', monospace;
                    }}
                    .back-button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #0d9488;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: 500;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                        transition: all 0.2s ease;
                    }}
                    .back-button:hover {{
                        background-color: #0f766e;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                        transform: translateY(-2px);
                    }}
                    header {{
                        background-color: #f0fdfa;
                        border-radius: 8px;
                    }}
                    .accordion {{
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                        transition: all 0.3s ease;
                    }}
                    .accordion:hover {{
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="navigation">
                        <a href="../../index.html" class="back-button">← Back to Index</a>
                    </div>
                    
                    <header>
                        <h1>{rel_path}</h1>
                        <div class="file-metadata">
                            <span class="file-metadata-item">Classes: {len(file_doc.classes)}</span>
                            <span class="file-metadata-item">Functions: {len(file_doc.functions)}</span>
                            <span class="file-metadata-item">Imports: {len(file_doc.imports)}</span>
                        </div>
                    </header>
                    
                    <div class="content-section">
                        <h2>File Purpose and Overview</h2>
                        <div class="file-purpose">
                            {file_purpose}
                        </div>
                    </div>
                    
                    <div class="content-section">
                        <h2>File Structure</h2>
            """)
            
            # Imports
            if file_doc.imports:
                f.write('<h3>Imports</h3>')
                f.write('<ul class="import-list">')
                for imp in file_doc.imports:
                    if imp.names:
                        f.write(f'<li><code>from {imp.module} import {", ".join(imp.names)}</code></li>')
                    else:
                        f.write(f'<li><code>import {imp.module}</code></li>')
                f.write('</ul>')
            
            
            if file_doc.classes:
                f.write('<div class="section-divider"></div>')
                f.write('<h3>Classes</h3>')
                f.write('<ul>')
                for class_name, class_info in file_doc.classes.items():
                    class_purpose = self._generate_class_purpose(class_name, class_info)
                    f.write(f'<li><strong class="code-tag">{class_name}</strong>: {class_purpose}</li>')
                f.write('</ul>')
            
            
            if file_doc.functions:
                f.write('<div class="section-divider"></div>')
                f.write('<h3>Functions</h3>')
                f.write('<ul>')
                for func_name, func_info in file_doc.functions.items():
                    func_purpose = self._generate_function_purpose(func_name, func_info)
                    f.write(f'<li><strong class="code-tag">{func_name}</strong>: {func_purpose}</li>')
                f.write('</ul>')
            
            f.write('</div>')  
            
            
            if file_doc.classes:
                f.write('<div class="content-section">')
                f.write('<h2>Classes</h2>')
                for class_name, class_info in file_doc.classes.items():
                    f.write(f"""
                    <div class="accordion">
                        <div class="accordion-header">
                            <h3>{class_name}</h3>
                            <div class="accordion-icon"></div>
                        </div>
                        <div class="accordion-content">
                    """)
                    
                    
                    if class_info.docstring:
                        f.write(f'<div class="method-description">{class_info.docstring}</div>')
                    
                    
                    if class_info.base_classes:
                        base_classes_html = ""
                        for base in class_info.base_classes:
                            base_classes_html += f'<span class="code-tag">{base}</span>, '
                        base_classes_html = base_classes_html.rstrip(', ')
                        f.write(f'<div class="inheritance"><strong>Inherits from:</strong> {base_classes_html}</div>')
                    
                    # Class methods
                    if class_info.methods:
                        f.write('<h4>Methods</h4>')
                        f.write('<ul class="method-list">')
                        for method_name, method_info in class_info.methods.items():
                            f.write('<li class="method-item">')
                            f.write(f'<div class="method-name">{method_name}</div>')
                            
                            # Method signature
                            params = method_info.params or []
                            if params:
                                
                                if params[0] == 'self':
                                    params = params[1:]
                                
                                if params:
                                    f.write(f'<div class="method-signature">({", ".join(params)})</div>')
                                else:
                                    f.write('<div class="method-signature">()</div>')
                            
                            
                            if method_info.docstring:
                                f.write(f'<div class="method-description">{method_info.docstring}</div>')
                            
                            f.write('</li>')
                        f.write('</ul>')
                    
                    f.write('</div></div>')  
                f.write('</div>')  
            
            # Detailed function documentation
            if file_doc.functions:
                f.write('<div class="content-section">')
                f.write('<h2>Functions</h2>')
                for func_name, func_info in file_doc.functions.items():
                    f.write(f"""
                    <div class="accordion">
                        <div class="accordion-header">
                            <h3>{func_name}</h3>
                            <div class="accordion-icon"></div>
                        </div>
                        <div class="accordion-content">
                    """)
                    
                    
                    params = func_info.params or []
                    if params:
                        f.write(f'<div class="method-signature">({", ".join(params)})</div>')
                    else:
                        f.write('<div class="method-signature">()</div>')
                    
                   
                    if func_info.return_type and func_info.return_type != "None":
                        f.write(f'<div><strong>Returns:</strong> <span class="code-tag">{func_info.return_type}</span></div>')
                    
                    
                    if func_info.docstring:
                        f.write(f'<div class="method-description">{func_info.docstring}</div>')
                    
                    
                    if func_info.docstring and "Args:" in func_info.docstring:
                        args_section = func_info.docstring.split("Args:")[1].split("Returns:")[0] if "Returns:" in func_info.docstring else func_info.docstring.split("Args:")[1]
                        f.write('<div class="param-details"><h4>Parameters</h4>')
                        for line in args_section.strip().split('\n'):
                            if ':' in line:
                                param_name, param_desc = line.split(':', 1)
                                f.write(f'<div class="param-item"><strong>{param_name.strip()}</strong>: {param_desc.strip()}</div>')
                        f.write('</div>')
                    
                    f.write('</div></div>')  
                f.write('</div>')  
            
            f.write("""
                </div>
                <script src="../../script.js"></script>
            </body>
            </html>
            """)
    
    def _generate_file_purpose(self, file_path: str, file_doc: FileDocumentation) -> str:
        """
        Generate a description of the file's purpose based on its contents.
        
        Args:
            file_path: Path to the file
            file_doc: FileDocumentation object
            
        Returns:
            HTML string with the file purpose description
        """
        file_name = os.path.basename(file_path)
        
        
        if file_doc.module_docstring:
            return f"<p>{file_doc.module_docstring}</p>"
        
        
        purpose = f"<p>This file (<code>{file_name}</code>) "
        
        if file_doc.classes and file_doc.functions:
            purpose += f"defines {len(file_doc.classes)} classes and {len(file_doc.functions)} functions. "
            
            
            class_names = ", ".join([f"<code>{name}</code>" for name in file_doc.classes.keys()])
            func_names = ", ".join([f"<code>{name}</code>" for name in file_doc.functions.keys()])
            
            purpose += f"<p>Classes: {class_names}</p>"
            purpose += f"<p>Functions: {func_names}</p>"
            
        elif file_doc.classes:
            purpose += f"defines {len(file_doc.classes)} classes. "
            class_names = ", ".join([f"<code>{name}</code>" for name in file_doc.classes.keys()])
            purpose += f"<p>Classes: {class_names}</p>"
            
        elif file_doc.functions:
            purpose += f"contains {len(file_doc.functions)} functions. "
            func_names = ", ".join([f"<code>{name}</code>" for name in file_doc.functions.keys()])
            purpose += f"<p>Functions: {func_names}</p>"
            
        else:
            purpose += "is part of the application structure but doesn't define any classes or functions directly.</p>"
        
        
        if "test" in file_name.lower():
            purpose += "<p>This appears to be a test file that verifies the functionality of other components.</p>"
        elif "config" in file_name.lower():
            purpose += "<p>This appears to be a configuration file that defines settings and parameters for the application.</p>"
        elif "model" in file_name.lower() or "schema" in file_name.lower():
            purpose += "<p>This appears to be a data model file that defines the structure of data used in the application.</p>"
        elif "util" in file_name.lower():
            purpose += "<p>This appears to be a utility file that provides helper functions and tools for other components.</p>"
        elif "api" in file_name.lower() or "endpoint" in file_name.lower():
            purpose += "<p>This appears to be part of the API layer that handles external requests and responses.</p>"
        elif "service" in file_name.lower():
            purpose += "<p>This appears to be a service file that implements business logic for the application.</p>"
        elif "main" in file_name.lower():
            purpose += "<p>This appears to be the main entry point for the application.</p>"
        elif "router" in file_name.lower():
            purpose += "<p>This appears to be a router file that defines API routes and endpoints.</p>"
        
        
        has_fastapi_import = any(
            imp.module == 'fastapi' or imp.module.startswith('fastapi.')
            for imp in file_doc.imports
        )
        
        if has_fastapi_import:
            purpose += "<p>This file uses FastAPI and may define API endpoints.</p>"
        
        return purpose
    
    def _generate_class_purpose(self, class_name: str, class_info: Any) -> str:
        """
        Generate a description of a class's purpose based on its name and methods.
        
        Args:
            class_name: Name of the class
            class_info: ClassInfo object
            
        Returns:
            String with the class purpose description
        """
        if not class_info.methods:
            return f"The <code>{class_name}</code> class doesn't have any documented methods."
        
        
        has_init = "__init__" in class_info.methods
        has_str = "__str__" in class_info.methods
        has_repr = "__repr__" in class_info.methods
        has_eq = "__eq__" in class_info.methods
        
        purpose = f"The <code>{class_name}</code> class "
        
        if "Manager" in class_name or "Service" in class_name:
            purpose += f"manages operations related to {class_name.replace('Manager', '').replace('Service', '')}. "
        elif "Controller" in class_name:
            purpose += f"controls the flow of data for {class_name.replace('Controller', '')}. "
        elif "Model" in class_name:
            purpose += f"represents the data structure for {class_name.replace('Model', '')}. "
        elif "Factory" in class_name:
            purpose += f"creates instances of {class_name.replace('Factory', '')} objects. "
        elif "Repository" in class_name:
            purpose += f"handles data access for {class_name.replace('Repository', '')} entities. "
        else:
            purpose += f"provides functionality related to {class_name}. "
        
        if has_init:
            purpose += "It can be initialized with specific parameters. "
        
        if has_str or has_repr:
            purpose += "It has string representation methods. "
        
        if has_eq:
            purpose += "It supports equality comparison. "
        
        method_count = len(class_info.methods)
        if method_count > 0:
            purpose += f"It defines {method_count} methods to handle various operations."
        
        return purpose
    
    def _generate_function_purpose(self, func_name: str, func_info: Any) -> str:
        """
        Generate a description of a function's purpose based on its name and parameters.
        
        Args:
            func_name: Name of the function
            func_info: FunctionInfo object
            
        Returns:
            String with the function purpose description
        """
        purpose = f"The <code>{func_name}</code> function "
        
        if func_name.startswith("get_"):
            purpose += f"retrieves {func_name[4:]} data. "
        elif func_name.startswith("set_"):
            purpose += f"sets or updates {func_name[4:]} data. "
        elif func_name.startswith("create_"):
            purpose += f"creates a new {func_name[7:]} instance. "
        elif func_name.startswith("delete_"):
            purpose += f"removes {func_name[7:]} data. "
        elif func_name.startswith("update_"):
            purpose += f"updates existing {func_name[7:]} data. "
        elif func_name.startswith("is_") or func_name.startswith("has_"):
            purpose += f"checks if a condition related to {func_name[3:]} is true. "
        elif func_name.startswith("validate_"):
            purpose += f"validates {func_name[9:]} data. "
        elif func_name.startswith("parse_"):
            purpose += f"parses {func_name[6:]} data. "
        elif func_name.startswith("convert_"):
            purpose += f"converts {func_name[8:]} from one format to another. "
        elif func_name.startswith("generate_"):
            purpose += f"generates {func_name[9:]} data. "
        else:
            purpose += f"performs operations related to {func_name}. "
        
        params = func_info.params or []
        if params:
            purpose += f"It takes {len(params)} parameter(s) and "
        else:
            purpose += "It takes no parameters and "
        
        if func_info.return_type and func_info.return_type != "None":
            purpose += f"returns a {func_info.return_type} result."
        else:
            purpose += "doesn't return any value."
        
        return purpose

    def create_watcher(self):
        """
        Create and return a watcher for the project.
        This method is for compatibility with the API.
        
        Returns:
            self: Returns the DocGenerator instance itself
        """
        return self

    def document_file(self, file_path: str) -> Optional[DocumentationResult]:
        """
        Generate documentation for a single file.
        
        Args:
            file_path: Path to the file to document
            
        Returns:
            DocumentationResult object if successful, None otherwise
        """
        try:
            
            file_doc = self.parser.parse_file(file_path)
            if not file_doc:
                logger.warning(f"No documentation generated for {file_path}")
                return None
            
            
            if not self._documentation:
                self._documentation = ProjectDocumentation(
                    project_path=self.config.project_path,
                    structure=self.scanner.get_project_structure(),
                    config=self.config
                )
            self._documentation.files[file_path] = file_doc
            
            # Create documentation result
            result = DocumentationResult(
                project_path=file_path,
                total_files=1,  
                total_functions=len(file_doc.functions),
                total_classes=len(file_doc.classes),
                output_path=os.path.join(self.config.project_path, self.config.doc_output_path),
                timestamp=datetime.now()
            )
            
            logger.debug(f"Generated documentation for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error documenting {file_path}: {str(e)}")
            return None

    def _generate_json_docs(self, output_dir: str) -> None:
        """
        Generate JSON documentation files.
        
        Args:
            output_dir: Directory to write JSON files
        """
        json_dir = os.path.join(output_dir, "json")
        os.makedirs(json_dir, exist_ok=True)
        
        
        json_path = os.path.join(json_dir, "documentation.json")
        
        # Convert documentation to dict for JSON serialization
        doc_dict = {
            "project_path": self._documentation.project_path,
            "structure": self._documentation.structure.dict(),
            "files": {
                path: {
                    "module_docstring": doc.module_docstring,
                    "classes": {
                        class_name: {
                            "docstring": class_info.docstring,
                            "methods": {
                                method_name: {
                                    "docstring": method_info.docstring,
                                    "params": method_info.params,
                                    "return_type": method_info.return_type,
                                    "is_async": method_info.is_async
                                }
                                for method_name, method_info in class_info.methods.items()
                            }
                        }
                        for class_name, class_info in doc.classes.items()
                    },
                    "functions": {
                        func_name: {
                            "docstring": func_info.docstring,
                            "params": func_info.params,
                            "return_type": func_info.return_type,
                            "is_async": func_info.is_async
                        }
                        for func_name, func_info in doc.functions.items()
                    }
                }
                for path, doc in self._documentation.files.items()
            },
            "last_updated": self._documentation.last_updated.isoformat()
        }
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc_dict, f, indent=2, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o))
        
        logger.info(f"Generated JSON documentation at {json_dir}")