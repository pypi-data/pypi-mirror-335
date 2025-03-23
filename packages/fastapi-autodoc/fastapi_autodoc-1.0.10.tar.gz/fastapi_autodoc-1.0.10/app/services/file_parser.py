import ast
import os
import inspect
import importlib.util
from typing import Dict, List, Optional, Any, Set, Tuple
import logging
from datetime import datetime

from app.core.schemas import FileDocumentation, FunctionInfo, ClassInfo, MethodInfo, ImportInfo

logger = logging.getLogger("autodoc.parser")

class FileParser:
    """Parser for Python files to extract documentation."""
    
    def __init__(self, include_private: bool = False, include_source_code: bool = False):
        """
        Initialize the file parser.
        
        Args:
            include_private: Whether to include private members (starting with _)
            include_source_code: Whether to include source code in the documentation
        """
        self.include_private = include_private
        self.include_source_code = include_source_code
    
    def parse_file(self, file_path: str) -> Optional[FileDocumentation]:
        """
        Parse a Python file and extract documentation.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            FileDocumentation object containing the parsed information
        """
        try:
            logger.debug(f"Parsing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            logger.debug(f"File content length: {len(file_content)}")
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            tree = ast.parse(file_content)
            logger.debug(f"AST parsed successfully")
            
            module_docstring = ast.get_docstring(tree)
            logger.debug(f"Module docstring: {module_docstring}")
            
            imports = self._extract_imports(tree)
            logger.debug(f"Found {len(imports)} imports")
            
            functions = {}
            classes = {}
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    if not self.include_private and node.name.startswith('_'):
                        logger.debug(f"Skipping private function: {node.name}")
                        continue
                    
                    logger.debug(f"Processing function: {node.name}")
                    functions[node.name] = self._extract_function_info(node, file_content)
                
                elif isinstance(node, ast.ClassDef):
                    if not self.include_private and node.name.startswith('_'):
                        logger.debug(f"Skipping private class: {node.name}")
                        continue
                    
                    logger.debug(f"Processing class: {node.name}")
                    classes[node.name] = self._extract_class_info(node, file_content)
            
            logger.debug(f"Found {len(functions)} functions and {len(classes)} classes")
            
            return FileDocumentation(
                file_path=file_path,
                module_docstring=module_docstring,
                classes=classes,
                functions=functions,
                imports=imports,
                last_modified=last_modified
            )
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _extract_imports(self, tree: ast.Module) -> List[ImportInfo]:
        """Extract import information from the AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(ImportInfo(
                        module=name.name,
                        alias=name.asname
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                names = [n.name for n in node.names]
                aliases = {n.name: n.asname for n in node.names if n.asname}
                
                imports.append(ImportInfo(
                    module=module,
                    names=names,
                    alias=None  
                ))
        
        return imports
    
    def _extract_function_info(self, node: ast.FunctionDef, source: str) -> FunctionInfo:
        """Extract information about a function from its AST node."""
        
        docstring = ast.get_docstring(node)
        
        
        params = [arg.arg for arg in node.args.args]
        
        
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return_type = self._get_attribute_name(node.returns)
        
        
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        
        source_code = None
        if self.include_source_code:
            source_code = self._get_source_segment(source, node)
        
        
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        return FunctionInfo(
            name=node.name,
            docstring=docstring,
            params=params,
            return_type=return_type,
            decorators=decorators,
            line_number=node.lineno,
            source_code=source_code,
            is_async=is_async
        )
    
    def _extract_class_info(self, node: ast.ClassDef, source: str) -> ClassInfo:
        """Extract information about a class from its AST node."""
        
        docstring = ast.get_docstring(node)
        
        
        methods = {}
        class_variables = {}
        
        for class_node in node.body:
            
            if isinstance(class_node, ast.FunctionDef) or isinstance(class_node, ast.AsyncFunctionDef):
                if not self.include_private and class_node.name.startswith('_') and class_node.name != '__init__':
                    continue
                
                method_info = self._extract_function_info(class_node, source)
                
                methods[class_node.name] = MethodInfo(**method_info.dict())
            
            
            elif isinstance(class_node, ast.Assign):
                for target in class_node.targets:
                    if isinstance(target, ast.Name):
                        
                        value = self._extract_value(class_node.value)
                        class_variables[target.id] = value
        
       
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._get_attribute_name(base))
        
        
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        
        source_code = None
        if self.include_source_code:
            source_code = self._get_source_segment(source, node)
        
        return ClassInfo(
            name=node.name,
            docstring=docstring,
            methods=methods,
            base_classes=base_classes,
            decorators=decorators,
            line_number=node.lineno,
            source_code=source_code,
            class_variables=class_variables
        )
    
    def _get_decorator_name(self, decorator_node) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator_node, ast.Call):
            if isinstance(decorator_node.func, ast.Name):
                return decorator_node.func.id
            elif isinstance(decorator_node.func, ast.Attribute):
                return self._get_attribute_name(decorator_node.func)
        elif isinstance(decorator_node, ast.Name):
            return decorator_node.id
        elif isinstance(decorator_node, ast.Attribute):
            return self._get_attribute_name(decorator_node)
        return "unknown"
    
    def _get_attribute_name(self, attribute_node) -> str:
        """Get full attribute name (e.g., package.module.attribute)."""
        parts = []
        node = attribute_node
        
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
            
        if isinstance(node, ast.Name):
            parts.append(node.id)
            
        return '.'.join(reversed(parts))
    
    def _get_source_segment(self, source: str, node: ast.AST) -> str:
        """Extract the source code segment for a node."""
        try:
            start_line = node.lineno - 1  
            end_line = None
            
            
            for child in ast.iter_child_nodes(node):
                if hasattr(child, 'lineno'):
                    if end_line is None or child.lineno > end_line:
                        end_line = child.lineno
            
            if end_line is None:
                end_line = start_line + 1
            
            
            lines = source.splitlines()
            return '\n'.join(lines[start_line:end_line])
        except Exception as e:
            logger.error(f"Error extracting source segment: {str(e)}")
            return "Unable to extract source code"
    
    def _extract_value(self, node) -> Any:
        """Extract a Python value from an AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Dict):
            keys = [self._extract_value(k) for k in node.keys]
            values = [self._extract_value(v) for v in node.values]
            return dict(zip(keys, values))
        elif isinstance(node, ast.Name):
            
            return f"<{node.id}>"
        elif isinstance(node, ast.Call):
            
            if isinstance(node.func, ast.Name):
                return f"<call to {node.func.id}>"
            elif isinstance(node.func, ast.Attribute):
                return f"<call to {self._get_attribute_name(node.func)}>"
            return "<function call>"
        
        return "<complex value>"