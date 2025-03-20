"""
Functional pattern detection for quantum-accelerable code patterns.

This module provides a functional approach to detecting patterns in Python code
that could benefit from quantum acceleration.
"""
import ast
import inspect
import textwrap
from typing import Dict, Callable, Any, List, Optional, Union, Tuple

# Type alias for pattern detector functions
PatternDetector = Callable[[ast.AST, Callable], float]

def analyze_function(func: Union[Callable, ast.AST], 
                    detectors: Dict[str, PatternDetector]) -> Dict[str, float]:
    """
    Analyze a function to detect quantum-accelerable patterns.
    
    Args:
        func: Function to analyze or an AST node
        detectors: Dictionary mapping pattern names to detector functions
        
    Returns:
        Dictionary mapping pattern names to confidence scores (0-1)
    """
    # Determine if we have a function object or an AST
    if isinstance(func, ast.AST):
        tree = func
        # For AST nodes, we'll create a dummy function
        dummy_func = lambda: None
        
        # If it's a FunctionDef node, get the name
        if isinstance(func, ast.FunctionDef):
            dummy_func.__name__ = func.name
        elif hasattr(func, 'body') and func.body and isinstance(func.body[0], ast.FunctionDef):
            dummy_func.__name__ = func.body[0].name
        else:
            dummy_func.__name__ = "unknown_function"
            
        func_obj = dummy_func
    else:
        # It's a real function object
        try:
            # Get source code of the function
            source = inspect.getsource(func)
            
            # Fix for indentation error: dedent the source code
            source = textwrap.dedent(source)
            
            # Try module mode first
            try:
                tree = ast.parse(source)
            except SyntaxError:
                # If that fails, try to parse it as an expression
                try:
                    # Add 'def ' to the beginning to make it a valid statement
                    if not source.startswith('def '):
                        source = 'def ' + source
                    tree = ast.parse(source)
                except Exception as e:
                    # As a last resort, try to manually fix indentation
                    lines = source.split('\n')
                    # Find minimum indentation
                    min_indent = min((len(line) - len(line.lstrip())) for line in lines if line.strip())
                    # Remove that indentation from all lines
                    fixed_lines = [line[min_indent:] if line.strip() else line for line in lines]
                    source = '\n'.join(fixed_lines)
                    try:
                        tree = ast.parse(source)
                    except Exception:
                        # If all else fails, create a dummy AST
                        tree = ast.Module(body=[ast.FunctionDef(
                            name=func.__name__,
                            args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                            body=[ast.Pass()],
                            decorator_list=[]
                        )], type_ignores=[])
            
            func_obj = func
        except (OSError, TypeError) as e:
            # If we can't get the source (e.g., built-in function),
            # we can't analyze it
            return {}
    
    results = {}
    for pattern_name, detector in detectors.items():
        try:
            confidence = detector(tree, func_obj)
            if confidence > 0:
                results[pattern_name] = confidence
        except Exception as e:
            # If there's an error in pattern detection, log it but continue
            pass
    
    return results

def analyze_source(source_code: str, 
                 detectors: Dict[str, PatternDetector]) -> Dict[str, Dict[str, float]]:
    """
    Analyze source code to detect quantum-accelerable patterns.
    
    Args:
        source_code: Source code string
        detectors: Dictionary mapping pattern names to detector functions
        
    Returns:
        Dictionary mapping function names to pattern detection results
    """
    try:
        tree = ast.parse(source_code)
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        
        results = {}
        for func_node in functions:
            # Create a separate module for each function
            function_module = ast.Module(body=[func_node], type_ignores=[])
            
            # Analyze the function's AST directly
            function_results = analyze_function(function_module, detectors)
            
            if function_results:
                results[func_node.name] = function_results
                
        return results
    except SyntaxError:
        # If there's a syntax error in the source code
        return {}

def analyze_data_flow(ast_node, variables=None):
    """
    Track variable dependencies and transformations.
    
    Args:
        ast_node: AST node to analyze
        variables: Dictionary tracking variable states
        
    Returns:
        Updated variables dictionary
    """
    variables = variables or {}
    
    # Process different node types
    if isinstance(ast_node, ast.Assign):
        for target in ast_node.targets:
            if isinstance(target, ast.Name):
                variables[target.id] = _extract_operations(ast_node.value)
    
    # Recursively process children
    for child in ast.iter_child_nodes(ast_node):
        analyze_data_flow(child, variables)
        
    return variables

def _extract_operations(node):
    """Extract operations from an AST node."""
    operations = []
    
    if isinstance(node, ast.BinOp):
        operations.append(type(node.op).__name__)
        operations.extend(_extract_operations(node.left))
        operations.extend(_extract_operations(node.right))
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            operations.append(f"Call:{node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                operations.append(f"Call:{node.func.value.id}.{node.func.attr}")
    
    return operations