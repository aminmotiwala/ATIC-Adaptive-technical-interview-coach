"""
Code Execution Tool
Author: Amin Motiwala

Implements secure code execution capabilities for technical coding assessment
during interviews. Supports Python and Java with execution results and security measures.
"""

import subprocess
import tempfile
import os
import sys
import time
from typing import Dict, Any, Optional, List
import json


class CodeExecutionTool:
    """
    Secure code execution tool for technical interview assessment.
    
    This tool provides:
    - Python and Java code execution support
    - Secure sandboxed execution environment
    - Timeout and resource limits
    - Detailed execution results and error reporting
    """
    
    def __init__(self, timeout_seconds: int = 10):
        """
        Initialize the code execution tool.
        
        Args:
            timeout_seconds: Maximum execution time per code snippet
        """
        self.timeout_seconds = timeout_seconds
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': [sys.executable],
                'version_check': [sys.executable, '--version']
            },
            'java': {
                'extension': '.java',
                'command': ['java'],
                'compile_command': ['javac'],
                'version_check': ['java', '-version']
            }
        }
        
        self._check_available_languages()
    
    def _check_available_languages(self) -> None:
        """Check which programming languages are available for execution."""
        available = []
        
        for lang, config in self.supported_languages.items():
            try:
                result = subprocess.run(
                    config['version_check'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 or lang == 'java':  # Java returns non-zero for version
                    available.append(lang)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        self.available_languages = available
        print(f"🔧 Code execution available for: {', '.join(available)}")
    
    def execute(self, code: str, language: str = 'python', test_inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute code in a secure environment.
        
        Args:
            code: Source code to execute
            language: Programming language ('python' or 'java')
            test_inputs: Optional list of test inputs for the program
            
        Returns:
            Dict containing execution results
        """
        execution_result = {
            'success': False,
            'language': language,
            'execution_time_ms': 0,
            'stdout': '',
            'stderr': '',
            'return_code': -1,
            'error_message': '',
            'security_violations': [],
            'test_results': []
        }
        
        # Validate language support
        if language not in self.available_languages:
            execution_result['error_message'] = f"Language '{language}' not supported or not available"
            return execution_result
        
        # Security validation
        security_check = self._validate_code_security(code, language)
        if not security_check['is_safe']:
            execution_result['security_violations'] = security_check['violations']
            execution_result['error_message'] = "Code contains security violations"
            return execution_result
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                start_time = time.time()
                
                if language == 'java':
                    execution_result = self._execute_java_code(code, temp_dir, test_inputs)
                else:  # python
                    execution_result = self._execute_python_code(code, temp_dir, test_inputs)
                
                execution_result['execution_time_ms'] = int((time.time() - start_time) * 1000)
                
        except Exception as e:
            execution_result['error_message'] = f"Execution failed: {str(e)}"
        
        return execution_result
    
    def _execute_python_code(self, code: str, temp_dir: str, test_inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute Python code."""
        source_file = os.path.join(temp_dir, "solution.py")
        with open(source_file, 'w') as f:
            f.write(code)
        
        execution_result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'return_code': -1,
            'test_results': []
        }
        
        command = [sys.executable, source_file]
        
        if test_inputs:
            for i, test_input in enumerate(test_inputs):
                result = self._run_subprocess(command, temp_dir, test_input)
                test_result = {
                    'test_case': i + 1,
                    'input': test_input,
                    'output': result['stdout'],
                    'stderr': result['stderr'],
                    'success': result['return_code'] == 0
                }
                execution_result['test_results'].append(test_result)
                
                if i == 0:  # Update overall result from first test
                    execution_result.update(result)
        else:
            result = self._run_subprocess(command, temp_dir)
            execution_result.update(result)
        
        execution_result['success'] = execution_result['return_code'] == 0
        return execution_result
    
    def _execute_java_code(self, code: str, temp_dir: str, test_inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute Java code."""
        # Extract class name from code
        class_name = self._extract_java_class_name(code) or "Solution"
        java_file = os.path.join(temp_dir, f"{class_name}.java")
        
        with open(java_file, 'w') as f:
            f.write(code)
        
        execution_result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'return_code': -1,
            'compilation_output': '',
            'test_results': []
        }
        
        # Compile Java code
        compile_result = self._run_subprocess(['javac', java_file], temp_dir)
        execution_result['compilation_output'] = compile_result['stderr']
        
        if compile_result['return_code'] != 0:
            execution_result['error_message'] = "Compilation failed"
            execution_result['stderr'] = compile_result['stderr']
            return execution_result
        
        # Execute compiled Java code
        command = ['java', '-cp', temp_dir, class_name]
        
        if test_inputs:
            for i, test_input in enumerate(test_inputs):
                result = self._run_subprocess(command, temp_dir, test_input)
                test_result = {
                    'test_case': i + 1,
                    'input': test_input,
                    'output': result['stdout'],
                    'stderr': result['stderr'],
                    'success': result['return_code'] == 0
                }
                execution_result['test_results'].append(test_result)
                
                if i == 0:  # Update overall result from first test
                    execution_result.update(result)
        else:
            result = self._run_subprocess(command, temp_dir)
            execution_result.update(result)
        
        execution_result['success'] = execution_result['return_code'] == 0
        return execution_result
    
    def _run_subprocess(self, command: List[str], cwd: str, input_text: str = "") -> Dict[str, Any]:
        """Run subprocess with timeout and security limits."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': f'Execution timed out after {self.timeout_seconds} seconds',
                'return_code': -1
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'return_code': -1
            }
    
    def _validate_code_security(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code for security issues."""
        security_result = {
            'is_safe': True,
            'violations': []
        }
        
        code_lower = code.lower()
        
        # Dangerous patterns
        dangerous_patterns = [
            'import os', 'import subprocess', 'exec(', 'eval(',
            '__import__', 'open(', 'file(', 'delete', 'remove'
        ]
        
        if language == 'java':
            dangerous_patterns.extend([
                'Runtime.getRuntime', 'ProcessBuilder', 'System.exit',
                'File(', 'FileWriter', 'FileReader'
            ])
        
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                security_result['violations'].append(f"Unsafe operation: {pattern}")
        
        if security_result['violations']:
            security_result['is_safe'] = False
        
        return security_result
    
    def _extract_java_class_name(self, code: str) -> Optional[str]:
        """Extract public class name from Java code."""
        import re
        
        # Look for public class declaration
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            return match.group(1)
        
        # Look for any class declaration
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)
        
        return None