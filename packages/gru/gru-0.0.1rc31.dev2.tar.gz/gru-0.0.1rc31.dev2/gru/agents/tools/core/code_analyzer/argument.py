from gru.agents.tools.core.code_analyzer.base import CodeAnalyzer
import ast
from typing import List


class ArgumentAnalyzer(CodeAnalyzer):
    """Python code analyzer that extracts command-line arguments."""
    
    class _ArgumentVisitor(ast.NodeVisitor):
        """AST visitor for extracting command-line arguments from Python code."""
        
        def __init__(self, tree, results_list):
            """
            Initialize visitor with the AST tree and a results list.
            
            Args:
                tree: The AST tree to analyze
                results_list: A list to which the visitor will append results
            """
            self.tree = tree
            self.results_list = results_list
        
        def is_argparse_constructor(self, node):
            """Check if a node is an argparse.ArgumentParser constructor."""
            return (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "argparse"
                and node.func.attr == "ArgumentParser"
            )

        def extract_argument_values(self, node):
            """Extract argument values from a Call node's arguments."""
            return [arg.value for arg in node.args if isinstance(arg, ast.Constant)]

        def collect_add_arguments(self, tree):
            """Collect all add_argument calls in the AST tree."""
            for parent in ast.walk(tree):
                if (
                    isinstance(parent, ast.Call)
                    and isinstance(parent.func, ast.Attribute)
                    and parent.func.attr == "add_argument"
                ):
                    args = self.extract_argument_values(parent)
                    if args:
                        self.results_list.extend(args)

        def visit_Call(self, node):
            """Visit a Call node and check if it's an argparse constructor."""
            if self.is_argparse_constructor(node):
                self.collect_add_arguments(self.tree)
    
    def analyze(self, source_code: str) -> List[str]:
        """
        Analyze Python source code to extract command-line arguments.
        
        Args:
            source_code: Python source code as a string
            
        Returns:
            List of command-line arguments found in the code
        """
        tree = ast.parse(source_code)
        argparse_details = []
        
        visitor = self._ArgumentVisitor(tree, argparse_details)
        visitor.visit(tree)
        
        return argparse_details
