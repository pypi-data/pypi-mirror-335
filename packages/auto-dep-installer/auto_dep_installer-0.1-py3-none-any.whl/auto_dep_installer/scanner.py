# auto_dep_installer/auto_dep_installer/scanner.py

import ast
import os
from pathlib import Path

class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""
    
    def __init__(self):
        self.imports = set()
    
    def visit_Import(self, node):
        """Visit an Import node."""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit an ImportFrom node."""
        if node.level == 0:  # absolute import
            self.imports.add(node.module)
        self.generic_visit(node)

def extract_imports_from_file(file_path):
    """Extract import statements from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
            visitor = ImportVisitor()
            visitor.visit(tree)
            return visitor.imports
        except SyntaxError:
            print(f"Syntax error in {file_path}, skipping...")
            return set()

def scan_directory_for_imports(directory_path):
    """Recursively scan a directory for Python files and extract imports."""
    imports = set()
    directory = Path(directory_path)
    
    for item in directory.glob('**/*.py'):
        if item.is_file():
            print(f"Scanning {item}")
            file_imports = extract_imports_from_file(item)
            imports.update(file_imports)
    
    print(f"Found {len(imports)} unique imported modules.")
    return imports