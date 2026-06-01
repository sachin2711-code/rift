"""
Committer Agent
Commits fixes and pushes to branch
"""

import os
import subprocess
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AgentState
from services.github_service import GitHubService
from utils.logger import get_logger

logger = get_logger(__name__)


class CommitterAgent:
    """
    Agent responsible for:
    1. Creating a new branch
    2. Committing fixes with proper messages
    3. Pushing to remote
    4. Creating pull requests
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI, github_service: GitHubService):
        self.llm = llm
        self.github_service = github_service
    
    async def commit(self, state: AgentState) -> AgentState:
        """
        Commit and push fixes
        
        Args:
            state: Current agent state with applied fixes
            
        Returns:
            Updated state with commit info
        """
        logger.info(f"[{state.run_id}] Committer starting to commit {len(state.applied_fixes)} fixes")
        
        if not state.applied_fixes:
            logger.info(f"[{state.run_id}] No fixes to commit")
            state.commit_sha = None
            state.total_commits = 0
            return state
        
        try:
            # Configure git
            await self._configure_git(state)
            
            # Create and checkout branch
            await self._create_branch(state)
            
            # Stage changes
            await self._stage_changes(state)
            
            # Commit fixes
            commit_sha = await self._commit_fixes(state)
            state.commit_sha = commit_sha
            state.total_commits = len(state.applied_fixes)
            
            # Push to remote
            await self._push_branch(state)
            
            logger.info(f"[{state.run_id}] Committer created {state.total_commits} commits")
            
        except Exception as e:
            logger.exception(f"[{state.run_id}] Committer failed")
            state.error_message = f"Failed to commit: {str(e)}"
            raise
        
        return state
    
    async def _configure_git(self, state: AgentState) -> None:
        """Configure git user"""
        repo_path = state.repo_path
        
        cmds = [
            f"cd {repo_path} && git config user.email 'rift-agent@example.com'",
            f"cd {repo_path} && git config user.name 'RIFT DevOps Agent'"
        ]
        
        for cmd in cmds:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Git config command failed: {result.stderr}")
    
    async def _create_branch(self, state: AgentState) -> None:
        """Create and checkout new branch"""
        repo_path = state.repo_path
        branch_name = state.branch_name
        
        # Create and checkout branch
        cmd = f"cd {repo_path} && git checkout -b {branch_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Failed to create branch: {result.stderr}")
        
        logger.info(f"[{state.run_id}] Created branch: {branch_name}")
    
    async def _stage_changes(self, state: AgentState) -> None:
        """Stage all changes"""
        repo_path = state.repo_path
        
        cmd = f"cd {repo_path} && git add -A"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Failed to stage changes: {result.stderr}")
    
    async def _commit_fixes(self, state: AgentState) -> str:
        """Commit all fixes"""
        repo_path = state.repo_path
        
        # Group fixes by file for better commit messages
        fixes_by_file: Dict[str, List[Dict]] = {}
        for fix in state.applied_fixes:
            file_path = fix["file_path"]
            if file_path not in fixes_by_file:
                fixes_by_file[file_path] = []
            fixes_by_file[file_path].append(fix)
        
        # Commit each file's fixes
        for file_path, fixes in fixes_by_file.items():
            # Generate commit message
            if len(fixes) == 1:
                commit_message = fixes[0]["commit_message"]
            else:
                bug_types = set(f["bug_type"] for f in fixes)
                commit_message = f"[AI-AGENT] Fix {len(fixes)} issues in {file_path} ({', '.join(bug_types)})"
            
            # Stage specific file
            cmd = f"cd {repo_path} && git add '{file_path}'"
            subprocess.run(cmd, shell=True, capture_output=True)
            
            # Commit
            commit_message_escaped = commit_message.replace('"', '\\"')
            cmd = f'cd {repo_path} && git commit -m "{commit_message_escaped}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Failed to commit {file_path}: {result.stderr}")
        
        # Get the last commit SHA
        cmd = f"cd {repo_path} && git rev-parse HEAD"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        
        return ""
    
    async def _push_branch(self, state: AgentState) -> None:
        """Push branch to remote"""
        repo_path = state.repo_path
        branch_name = state.branch_name
        
        # Push to origin
        cmd = f"cd {repo_path} && git push -u origin {branch_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Try with force in case branch exists
            cmd = f"cd {repo_path} && git push -f -u origin {branch_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to push branch: {result.stderr}")
        
        logger.info(f"[{state.run_id}] Pushed branch: {branch_name}")