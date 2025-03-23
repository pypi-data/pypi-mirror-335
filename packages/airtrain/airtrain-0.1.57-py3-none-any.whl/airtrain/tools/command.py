"""
Command execution tools for AirTrain agents.

This module provides tools for executing shell commands in a controlled environment.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional

from .registry import StatelessTool, register_tool


@register_tool("execute_command")
class ExecuteCommandTool(StatelessTool):
    """Tool for executing shell commands."""
    
    def __init__(self):
        self.name = "execute_command"
        self.description = "Execute a shell command and return its output"
        self.parameters = {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory for the command"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds"
                },
                "env_vars": {
                    "type": "object",
                    "description": "Environment variables to set for the command"
                }
            },
            "required": ["command"]
        }
        
        # List of disallowed commands for security
        self.disallowed_commands = [
            "rm -rf", "sudo", "su", "chown", "chmod", "mkfs",
            "dd", "shred", ">", ">>", "|", "perl -e", "python -c",
            "ruby -e", ":(){ :|:& };:", "eval", "exec", "`"
        ]
    
    def __call__(
        self, 
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[float] = 30.0,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute a shell command and return its output."""
        try:
            # Security check
            for disallowed in self.disallowed_commands:
                if disallowed in command:
                    return {
                        "success": False,
                        "error": f"Command contains disallowed pattern: {disallowed}"
                    }
            
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=timeout,
                env=env
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command: {str(e)}"
            }
    
    def to_dict(self):
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


@register_tool("find_files")
class FindFilesTool(StatelessTool):
    """Tool for finding files matching patterns."""
    
    def __init__(self):
        self.name = "find_files"
        self.description = "Find files matching the specified pattern"
        self.parameters = {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to search in"
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match (e.g., *.txt, **/*.py)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return"
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Whether to include hidden files (starting with .)"
                }
            },
            "required": ["directory", "pattern"]
        }
    
    def __call__(
        self,
        directory: str,
        pattern: str,
        max_results: int = 100,
        show_hidden: bool = False
    ) -> Dict[str, Any]:
        """Find files matching the specified pattern."""
        try:
            import glob
            from pathlib import Path
            
            directory = os.path.expanduser(directory)
            if not os.path.exists(directory):
                return {
                    "success": False,
                    "error": f"Directory '{directory}' does not exist"
                }
                
            if not os.path.isdir(directory):
                return {
                    "success": False,
                    "error": f"Path '{directory}' is not a directory"
                }
            
            # Construct search path
            search_path = os.path.join(directory, pattern)
            
            # Find matching files
            files = []
            for file_path in glob.glob(search_path, recursive=True):
                if not show_hidden and os.path.basename(file_path).startswith('.'):
                    continue
                    
                file_info = {
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "type": "dir" if os.path.isdir(file_path) else "file",
                    "size": os.path.getsize(file_path) if os.path.isfile(file_path) else None
                }
                files.append(file_info)
                
                if len(files) >= max_results:
                    break
            
            return {
                "success": True,
                "directory": directory,
                "pattern": pattern,
                "files": files,
                "count": len(files),
                "truncated": len(files) >= max_results
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error finding files: {str(e)}"
            }
    
    def to_dict(self):
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        } 