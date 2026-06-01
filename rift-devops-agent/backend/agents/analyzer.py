"""
Analyzer Agent
Clones repository, analyzes structure, and detects issues
"""

import ast
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0,
)


class AnalyzerAgent:
    """
    Agent responsible for:
    1. Cloning the repository
    2. Analyzing repository structure
    3. Discovering test files
    4. Detecting code issues (linting, syntax, imports, etc.)
    """
    
    BUG_TYPES = {
        "LINTING": ["unused import", "unused variable", "line too long", "trailing whitespace"],
        "SYNTAX": ["missing colon", "invalid syntax", "indentation error", "unexpected EOF"],
        "TYPE_ERROR": ["type mismatch", "incompatible types", "missing type hint"],
        "IMPORT": ["missing import", "circular import", "import error"],
        "LOGIC": ["undefined variable", "name error", "attribute error"],
        "INDENTATION": ["indentation error", "mixed tabs and spaces"],
        "SECURITY": ["hardcoded password", "sql injection", "unsafe eval"]
    }
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        
        # Initialize prompt for issue detection
        self.issue_detection_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a code analysis expert. Analyze the provided code and identify issues.
For each issue, provide:
- bug_type: One of [LINTING, SYNTAX, TYPE_ERROR, IMPORT, LOGIC, INDENTATION, SECURITY]
- line_number: The line number where the issue occurs
- description: Clear description of the issue
- suggested_fix: The code to fix the issue

Respond in JSON format with an "issues" array."""),
            ("human", "File: {file_path}\n\n```python\n{code}\n```\n\nAnalyze this code for issues.")
        ])
    
    async def analyze(self, state: AgentState) -> AgentState:
        """
        Analyze the repository and detect issues
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with analysis results
        """
        logger.info(f"[{state.run_id}] Analyzer starting analysis")
        
        repo_path = state.repo_path
        if not repo_path or not os.path.exists(repo_path):
            raise ValueError(f"Invalid repository path: {repo_path}")
        
        # Build file tree
        state.file_tree = self._build_file_tree(repo_path)
        
        # Discover test files
        state.test_files = self._discover_test_files(repo_path)
        
        # Detect issues in Python files
        state.detected_issues = await self._detect_issues(repo_path)
        
        logger.info(f"[{state.run_id}] Analyzer found {len(state.detected_issues)} issues")
        
        return state
    
    def _build_file_tree(self, repo_path: str) -> Dict[str, Any]:
        """Build hierarchical file tree of repository"""
        
        def build_tree(path: str, relative_path: str = "") -> Dict[str, Any]:
            name = os.path.basename(path)
            
            if os.path.isfile(path):
                return {
                    "name": name,
                    "path": relative_path or name,
                    "type": "file",
                    "size": os.path.getsize(path)
                }
            
            children = []
            try:
                for item in sorted(os.listdir(path)):
                    if item.startswith('.') and item != '.github':  # Skip hidden files
                        continue
                    
                    item_path = os.path.join(path, item)
                    item_relative = os.path.join(relative_path, item) if relative_path else item
                    children.append(build_tree(item_path, item_relative))
            except PermissionError:
                pass
            
            return {
                "name": name or os.path.basename(repo_path),
                "path": relative_path or ".",
                "type": "directory",
                "children": children
            }
        
        return build_tree(repo_path)
    
    def _discover_test_files(self, repo_path: str) -> List[str]:
        """Discover all test files in repository"""
        test_files = []
        
        test_patterns = [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'tests?/.*\.py$'
        ]
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-test directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                for pattern in test_patterns:
                    if re.match(pattern, relative_path):
                        test_files.append(relative_path)
                        break
        
        return test_files
    
    async def _detect_issues(self, repo_path: str) -> List[Dict[str, Any]]:
        """Detect issues in repository files"""
        issues = []
        
        # Run pylint for linting issues
        pylint_issues = await self._run_pylint(repo_path)
        issues.extend(pylint_issues)
        
        # Run flake8 for style issues
        flake8_issues = await self._run_flake8(repo_path)
        issues.extend(flake8_issues)
        
        # Run mypy for type issues
        mypy_issues = await self._run_mypy(repo_path)
        issues.extend(mypy_issues)
        
        # Run bandit for security issues
        bandit_issues = await self._run_bandit(repo_path)
        issues.extend(bandit_issues)
        
        # Check for syntax errors
        syntax_issues = await self._check_syntax_errors(repo_path)
        issues.extend(syntax_issues)
        
        # AI-powered analysis for complex issues
        ai_issues = await self._ai_analysis(repo_path)
        issues.extend(ai_issues)
        
        # Deduplicate issues
        issues = self._deduplicate_issues(issues)
        
        return issues
    
    async def _run_pylint(self, repo_path: str) -> List[Dict[str, Any]]:
        """Run pylint and parse output"""
        issues = []
        
        try:
            cmd = f"cd {repo_path} && pylint --output-format=json . 2>/dev/null || true"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            if result.stdout:
                import json
                try:
                    pylint_output = json.loads(result.stdout)
                    for item in pylint_output:
                        issue = {
                            "id": f"pylint-{item.get('message-id', 'unknown')}",
                            "file_path": item.get('path', ''),
                            "line_number": item.get('line', 0),
                            "column": item.get('column', 0),
                            "bug_type": self._categorize_pylint_message(item.get('message-id', '')),
                            "severity": item.get('type', 'warning'),
                            "message": item.get('message', ''),
                            "symbol": item.get('symbol', ''),
                            "source": "pylint"
                        }
                        issues.append(issue)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.warning(f"Pylint analysis failed: {e}")
        
        return issues
    
    async def _run_flake8(self, repo_path: str) -> List[Dict[str, Any]]:
        """Run flake8 and parse output"""
        issues = []
        
        try:
            cmd = f"cd {repo_path} && flake8 --format='%(path)s:%(row)d:%(col)d:%(code)s:%(text)s' . 2>/dev/null || true"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split(':', 4)
                if len(parts) >= 5:
                    issue = {
                        "id": f"flake8-{parts[3]}",
                        "file_path": parts[0],
                        "line_number": int(parts[1]) if parts[1].isdigit() else 0,
                        "column": int(parts[2]) if parts[2].isdigit() else 0,
                        "bug_type": self._categorize_flake8_code(parts[3]),
                        "severity": "warning",
                        "message": parts[4],
                        "symbol": parts[3],
                        "source": "flake8"
                    }
                    issues.append(issue)
        except Exception as e:
            logger.warning(f"Flake8 analysis failed: {e}")
        
        return issues
    
    async def _run_mypy(self, repo_path: str) -> List[Dict[str, Any]]:
        """Run mypy and parse output"""
        issues = []
        
        try:
            cmd = f"cd {repo_path} && mypy --show-column-numbers --show-error-codes . 2>/dev/null || true"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            for line in result.stdout.strip().split('\n'):
                if not line or ':' not in line:
                    continue
                
                # Parse mypy output format: file:line:col: error-type: message [error-code]
                match = re.match(r'(.+):(\d+):(\d+):\s*(\w+):\s*(.+)', line)
                if match:
                    file_path, line_num, col, error_type, message = match.groups()
                    
                    # Extract error code if present
                    error_code = ""
                    code_match = re.search(r'\[([\w-]+)\]$', message.strip())
                    if code_match:
                        error_code = code_match.group(1)
                        message = message[:code_match.start()].strip()
                    
                    issue = {
                        "id": f"mypy-{error_code or 'unknown'}",
                        "file_path": file_path.strip(),
                        "line_number": int(line_num),
                        "column": int(col),
                        "bug_type": "TYPE_ERROR",
                        "severity": "error" if error_type == "error" else "warning",
                        "message": message,
                        "symbol": error_code,
                        "source": "mypy"
                    }
                    issues.append(issue)
        except Exception as e:
            logger.warning(f"Mypy analysis failed: {e}")
        
        return issues
    
    async def _run_bandit(self, repo_path: str) -> List[Dict[str, Any]]:
        """Run bandit for security issues"""
        issues = []
        
        try:
            cmd = f"cd {repo_path} && bandit -r . -f json 2>/dev/null || true"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.stdout:
                import json
                try:
                    bandit_output = json.loads(result.stdout)
                    for item in bandit_output.get('results', []):
                        issue = {
                            "id": f"bandit-{item.get('test_id', 'unknown')}",
                            "file_path": item.get('filename', ''),
                            "line_number": item.get('line_number', 0),
                            "column": 0,
                            "bug_type": "SECURITY",
                            "severity": item.get('issue_severity', 'medium').lower(),
                            "message": item.get('issue_text', ''),
                            "symbol": item.get('test_name', ''),
                            "source": "bandit"
                        }
                        issues.append(issue)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.warning(f"Bandit analysis failed: {e}")
        
        return issues
    
    async def _check_syntax_errors(self, repo_path: str) -> List[Dict[str, Any]]:
        """Check for syntax errors in Python files"""
        issues = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    
                    try:
                        ast.parse(source)
                    except SyntaxError as e:
                        issue = {
                            "id": f"syntax-{relative_path}-{e.lineno}",
                            "file_path": relative_path,
                            "line_number": e.lineno or 1,
                            "column": e.offset or 0,
                            "bug_type": "SYNTAX",
                            "severity": "error",
                            "message": str(e),
                            "symbol": "syntax-error",
                            "source": "ast-parser"
                        }
                        issues.append(issue)
                except Exception as e:
                    logger.warning(f"Failed to check {file_path}: {e}")
        
        return issues
    
    async def _ai_analysis(self, repo_path: str) -> List[Dict[str, Any]]:
        """AI-powered analysis for complex issues"""
        issues = []
        
        # Only analyze files with potential complex issues
        files_to_analyze = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    # Skip very large files
                    if os.path.getsize(file_path) > 50000:  # 50KB
                        continue
                    
                    files_to_analyze.append((relative_path, file_path))
        
        # Limit to first 10 files to avoid rate limits
        for relative_path, file_path in files_to_analyze[:10]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Skip if file is too large
                if len(code) > 10000:
                    continue
                
                # Use LLM to analyze
                chain = self.issue_detection_prompt | self.llm
                response = await chain.ainvoke({
                    "file_path": relative_path,
                    "code": code
                })
                
                # Parse response
                try:
                    import json
                    content = response.content if hasattr(response, 'content') else str(response)
                    
                    # Extract JSON from response
                    json_match = re.search(r'```json\s*(.+?)\s*```', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(1)
                    
                    data = json.loads(content)
                    
                    for item in data.get('issues', []):
                        issue = {
                            "id": f"ai-{relative_path}-{item.get('line_number', 0)}",
                            "file_path": relative_path,
                            "line_number": item.get('line_number', 0),
                            "column": 0,
                            "bug_type": item.get('bug_type', 'LOGIC'),
                            "severity": "warning",
                            "message": item.get('description', ''),
                            "symbol": item.get('bug_type', 'unknown'),
                            "source": "ai-analysis",
                            "suggested_fix": item.get('suggested_fix', '')
                        }
                        issues.append(issue)
                        
                except Exception as e:
                    logger.warning(f"Failed to parse AI analysis for {relative_path}: {e}")
                    
            except Exception as e:
                logger.warning(f"AI analysis failed for {file_path}: {e}")
        
        return issues
    
    def _categorize_pylint_message(self, msg_id: str) -> str:
        """Categorize pylint message ID to bug type"""
        if msg_id.startswith('E'):
            return "SYNTAX"
        elif msg_id.startswith('F'):
            return "LOGIC"
        elif msg_id.startswith('W'):
            if 'import' in msg_id.lower():
                return "IMPORT"
            return "LINTING"
        elif msg_id.startswith('C'):
            return "LINTING"
        elif msg_id.startswith('R'):
            return "LINTING"
        return "LOGIC"
    
    def _categorize_flake8_code(self, code: str) -> str:
        """Categorize flake8 error code to bug type"""
        if code.startswith('E'):
            if code in ['E901', 'E902']:
                return "SYNTAX"
            return "LINTING"
        elif code.startswith('F'):
            if code in ['F401', 'F402', 'F403', 'F404']:
                return "IMPORT"
            return "LOGIC"
        elif code.startswith('W'):
            return "LINTING"
        elif code.startswith('I'):
            return "IMPORT"
        return "LINTING"
    
    def _deduplicate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate issues"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = (issue.get('file_path', ''), issue.get('line_number', 0), issue.get('message', ''))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues