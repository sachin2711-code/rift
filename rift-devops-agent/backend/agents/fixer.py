"""
Fixer Agent
Generates and applies fixes for detected issues
"""

import os
import re
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from agents.state import AgentState, Fix
from utils.logger import get_logger

logger = get_logger(__name__)


class FixerAgent:
    """
    Agent responsible for:
    1. Generating fixes for detected issues
    2. Applying fixes to code files
    3. Verifying fixes don't break syntax
    4. Rolling back failed fixes
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        
        # Initialize prompts
        self.fix_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert code fixer. Given a code issue, generate a fix.
Respond in JSON format with:
- before_code: The original code to be replaced
- after_code: The fixed code
- explanation: Brief explanation of the fix

Only provide the exact code changes needed."""),
            ("human", """File: {file_path}
Line: {line_number}
Issue Type: {bug_type}
Issue: {issue_message}

```python
{code_context}
```

Generate the fix.""")
        ])
    
    async def fix(self, state: AgentState) -> AgentState:
        """
        Generate and apply fixes for detected issues
        
        Args:
            state: Current agent state with detected issues
            
        Returns:
            Updated state with applied fixes
        """
        logger.info(f"[{state.run_id}] Fixer starting to fix {len(state.detected_issues)} issues")
        
        state.fixes = []
        state.applied_fixes = []
        state.failed_fixes = []
        
        for issue in state.detected_issues:
            try:
                fix = await self._generate_fix(state, issue)
                
                if fix:
                    # Apply the fix
                    success = await self._apply_fix(state, fix)
                    
                    if success:
                        fix["status"] = "applied"
                        state.applied_fixes.append(fix)
                    else:
                        fix["status"] = "failed"
                        fix["error_message"] = "Failed to apply fix"
                        state.failed_fixes.append(fix)
                
            except Exception as e:
                logger.exception(f"[{state.run_id}] Failed to fix issue: {issue}")
                state.failed_fixes.append({
                    "id": f"fix-{issue.get('id', 'unknown')}",
                    "file_path": issue.get('file_path', ''),
                    "bug_type": issue.get('bug_type', 'LOGIC'),
                    "line_number": issue.get('line_number', 0),
                    "description": issue.get('message', ''),
                    "commit_message": f"[AI-AGENT] Fix {issue.get('bug_type', 'LOGIC')} error",
                    "status": "failed",
                    "error_message": str(e),
                    "before_code": None,
                    "after_code": None
                })
        
        logger.info(f"[{state.run_id}] Fixer applied {len(state.applied_fixes)} fixes, {len(state.failed_fixes)} failed")
        
        return state
    
    async def _generate_fix(self, state: AgentState, issue: Dict[str, Any]) -> Optional[Fix]:
        """Generate a fix for an issue"""
        file_path = issue.get('file_path', '')
        line_number = issue.get('line_number', 0)
        bug_type = issue.get('bug_type', 'LOGIC')
        message = issue.get('message', '')
        
        # Get code context
        code_context = await self._get_code_context(state, file_path, line_number)
        
        # Try to use similar patterns from memory
        similar_fix = self._find_similar_fix(state, issue)
        
        if similar_fix:
            # Use the similar fix as template
            fix = Fix(
                id=f"fix-{issue.get('id', 'unknown')}",
                file_path=file_path,
                bug_type=bug_type,
                line_number=line_number,
                description=message,
                before_code=similar_fix.get('before_code', ''),
                after_code=similar_fix.get('after_code', ''),
                commit_message=self._generate_commit_message(file_path, line_number, bug_type, message),
                status="pending",
                error_message=None
            )
            return fix
        
        # Generate fix using LLM
        try:
            chain = self.fix_generation_prompt | self.llm
            response = await chain.ainvoke({
                "file_path": file_path,
                "line_number": line_number,
                "bug_type": bug_type,
                "issue_message": message,
                "code_context": code_context
            })
            
            # Parse response
            import json
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON
            json_match = re.search(r'```json\s*(.+?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            data = json.loads(content)
            
            fix = Fix(
                id=f"fix-{issue.get('id', 'unknown')}",
                file_path=file_path,
                bug_type=bug_type,
                line_number=line_number,
                description=message,
                before_code=data.get('before_code', ''),
                after_code=data.get('after_code', ''),
                commit_message=self._generate_commit_message(file_path, line_number, bug_type, message),
                status="pending",
                error_message=None
            )
            
            return fix
            
        except Exception as e:
            logger.warning(f"Failed to generate fix with LLM: {e}")
            
            # Try rule-based fix
            return await self._generate_rule_based_fix(state, issue)
    
    async def _generate_rule_based_fix(self, state: AgentState, issue: Dict[str, Any]) -> Optional[Fix]:
        """Generate a fix using predefined rules"""
        file_path = issue.get('file_path', '')
        line_number = issue.get('line_number', 0)
        bug_type = issue.get('bug_type', 'LOGIC')
        message = issue.get('message', '')
        
        full_path = os.path.join(state.repo_path, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_number > len(lines):
                return None
            
            original_line = lines[line_number - 1]
            fixed_line = original_line
            
            # Apply rule-based fixes
            if bug_type == "LINTING":
                if "unused import" in message.lower():
                    # Remove the import line
                    fixed_line = ""
                elif "trailing whitespace" in message.lower():
                    fixed_line = original_line.rstrip() + "\n"
                elif "line too long" in message.lower():
                    # Try to split the line
                    fixed_line = self._split_long_line(original_line)
            
            elif bug_type == "IMPORT":
                if "missing import" in message.lower():
                    # This is harder to fix automatically
                    return None
            
            elif bug_type == "SYNTAX":
                if "missing colon" in message.lower():
                    fixed_line = original_line.rstrip()
                    if not fixed_line.endswith(':'):
                        fixed_line = fixed_line + ":\n"
            
            elif bug_type == "INDENTATION":
                # Fix mixed tabs and spaces
                fixed_line = original_line.replace('\t', '    ')
            
            if fixed_line != original_line:
                return Fix(
                    id=f"fix-{issue.get('id', 'unknown')}",
                    file_path=file_path,
                    bug_type=bug_type,
                    line_number=line_number,
                    description=message,
                    before_code=original_line,
                    after_code=fixed_line,
                    commit_message=self._generate_commit_message(file_path, line_number, bug_type, message),
                    status="pending",
                    error_message=None
                )
        
        except Exception as e:
            logger.warning(f"Rule-based fix failed: {e}")
        
        return None
    
    async def _apply_fix(self, state: AgentState, fix: Fix) -> bool:
        """Apply a fix to the file"""
        file_path = os.path.join(state.repo_path, fix["file_path"])
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            line_number = fix["line_number"]
            before_code = fix["before_code"]
            after_code = fix["after_code"]
            
            # Handle multi-line fixes
            if '\n' in before_code:
                # Multi-line replacement
                before_lines = before_code.strip().split('\n')
                after_lines = after_code.strip().split('\n')
                
                # Find and replace
                for i in range(len(lines) - len(before_lines) + 1):
                    match = all(
                        lines[i + j].rstrip() == before_lines[j].rstrip()
                        for j in range(len(before_lines))
                    )
                    if match:
                        lines[i:i + len(before_lines)] = after_lines
                        break
            else:
                # Single line replacement
                if line_number <= len(lines):
                    original_line = lines[line_number - 1]
                    
                    # If before_code is empty, just replace the whole line
                    if not before_code or before_code.strip() == original_line.strip():
                        lines[line_number - 1] = after_code.rstrip('\n')
                    else:
                        # Try to find and replace within the line
                        lines[line_number - 1] = original_line.replace(
                            before_code.strip(),
                            after_code.strip()
                        )
            
            # Write back
            new_content = '\n'.join(lines)
            
            # Verify syntax is still valid
            if file_path.endswith('.py'):
                try:
                    import ast
                    ast.parse(new_content)
                except SyntaxError:
                    logger.warning(f"Fix would break syntax in {file_path}")
                    return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            logger.exception(f"Failed to apply fix: {e}")
            return False
    
    async def _get_code_context(
        self,
        state: AgentState,
        file_path: str,
        line_number: int,
        context_lines: int = 5
    ) -> str:
        """Get code context around a line"""
        full_path = os.path.join(state.repo_path, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            
            context = []
            for i in range(start, end):
                line_num = i + 1
                prefix = ">>> " if i == line_number - 1 else "    "
                context.append(f"{prefix}{line_num:4d}: {lines[i]}")
            
            return ''.join(context)
            
        except Exception as e:
            logger.warning(f"Failed to get code context: {e}")
            return ""
    
    def _find_similar_fix(self, state: AgentState, issue: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Find a similar fix from memory patterns"""
        bug_type = issue.get('bug_type', 'LOGIC')
        message = issue.get('message', '')
        
        for pattern in state.similar_patterns:
            if pattern.bug_type == bug_type:
                # Check if message similarity
                if self._message_similarity(message, pattern.pattern) > 0.7:
                    return {
                        'before_code': '',  # Would need to extract from pattern
                        'after_code': pattern.fix_template
                    }
        
        return None
    
    def _message_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate simple similarity between two messages"""
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _generate_commit_message(
        self,
        file_path: str,
        line_number: int,
        bug_type: str,
        message: str
    ) -> str:
        """Generate a commit message for a fix"""
        # Truncate message if too long
        short_message = message[:50] + "..." if len(message) > 50 else message
        
        return f"[AI-AGENT] Fix {bug_type} in {file_path}:{line_number} - {short_message}"
    
    def _split_long_line(self, line: str, max_length: int = 88) -> str:
        """Split a long line into multiple lines"""
        if len(line) <= max_length:
            return line
        
        # Try to split at a comma or operator
        split_points = [', ', ' + ', ' - ', ' * ', ' / ', ' // ']
        
        for point in split_points:
            idx = line.rfind(point, 0, max_length)
            if idx > 0:
                indent = len(line) - len(line.lstrip())
                return line[:idx + len(point)] + '\\n' + ' ' * (indent + 4) + line[idx + len(point):]
        
        # If no good split point, just wrap
        return line[:max_length] + '\\n' + line[max_length:]