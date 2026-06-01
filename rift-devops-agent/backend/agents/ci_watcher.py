"""
CI Watcher Agent
Monitors CI/CD pipeline and decides whether to continue fixing
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AgentState, CICDIteration
from services.github_service import GitHubService
from utils.logger import get_logger

logger = get_logger(__name__)


class CIWatcherAgent:
    """
    Agent responsible for:
    1. Monitoring CI/CD pipeline status
    2. Waiting for pipeline completion
    3. Deciding whether to continue fixing or finish
    4. Tracking iteration count
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI, github_service: GitHubService):
        self.llm = llm
        self.github_service = github_service
    
    async def watch(self, state: AgentState) -> AgentState:
        """
        Monitor CI/CD pipeline
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with CI/CD status
        """
        logger.info(f"[{state.run_id}] CI Watcher starting monitoring")
        
        state.current_iteration += 1
        
        iteration = CICDIteration(
            iteration=state.current_iteration,
            status="running",
            timestamp=datetime.utcnow().isoformat(),
            duration_seconds=None,
            test_failures=None
        )
        
        # Poll CI/CD status
        max_wait_time = 600  # 10 minutes
        poll_interval = 30   # 30 seconds
        elapsed = 0
        
        start_time = time.time()
        
        while elapsed < max_wait_time:
            try:
                # Check CI/CD status
                status = await self._check_ci_status(state)
                
                if status == "completed":
                    # Check if tests passed
                    test_status = await self._check_test_status(state)
                    
                    iteration["status"] = test_status
                    iteration["duration_seconds"] = time.time() - start_time
                    
                    if test_status == "passed":
                        state.final_cicd_status = "passed"
                        logger.info(f"[{state.run_id}] CI/CD passed!")
                    else:
                        state.final_cicd_status = "failed"
                        # Get test failures for next iteration
                        iteration["test_failures"] = await self._get_test_failure_count(state)
                        logger.info(f"[{state.run_id}] CI/CD failed, {iteration['test_failures']} test failures")
                    
                    break
                
                elif status == "failed":
                    iteration["status"] = "failed"
                    iteration["duration_seconds"] = time.time() - start_time
                    state.final_cicd_status = "failed"
                    logger.info(f"[{state.run_id}] CI/CD pipeline failed")
                    break
                
                # Still running, wait and poll again
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                
            except Exception as e:
                logger.exception(f"[{state.run_id}] Error checking CI status: {e}")
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
        
        if elapsed >= max_wait_time:
            iteration["status"] = "timeout"
            iteration["duration_seconds"] = max_wait_time
            state.final_cicd_status = "timeout"
            logger.warning(f"[{state.run_id}] CI/CD monitoring timed out")
        
        state.cicd_iterations.append(iteration)
        
        logger.info(f"[{state.run_id}] CI Watcher completed iteration {state.current_iteration}: {state.final_cicd_status}")
        
        return state
    
    async def _check_ci_status(self, state: AgentState) -> str:
        """Check CI/CD pipeline status"""
        try:
            # Try to get GitHub Actions status
            status = await self.github_service.get_workflow_status(
                state.repo_url,
                state.branch_name
            )
            return status
        except Exception as e:
            logger.warning(f"Failed to check CI status: {e}")
            
            # Fallback: check if we can detect CI status from repo
            return await self._fallback_ci_check(state)
    
    async def _fallback_ci_check(self, state: AgentState) -> str:
        """Fallback CI check using local test run"""
        import subprocess
        
        repo_path = state.repo_path
        
        # Check for common CI files
        ci_files = [
            '.github/workflows',
            '.gitlab-ci.yml',
            'azure-pipelines.yml',
            'Jenkinsfile'
        ]
        
        has_ci = any(
            subprocess.run(f"test -e {repo_path}/{f}", shell=True).returncode == 0
            for f in ci_files
        )
        
        if not has_ci:
            # No CI configured, run tests locally
            logger.info(f"[{state.run_id}] No CI detected, running local tests")
            return await self._run_local_tests(state)
        
        # Has CI but we can't check status, assume running
        return "running"
    
    async def _run_local_tests(self, state: AgentState) -> str:
        """Run tests locally as fallback"""
        import subprocess
        
        repo_path = state.repo_path
        
        # Try different test commands
        test_commands = [
            "python -m pytest --tb=short -q",
            "python -m unittest discover -v",
            "python setup.py test",
            "make test"
        ]
        
        for cmd in test_commands:
            full_cmd = f"cd {repo_path} && {cmd} 2>&1"
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return "completed"
            elif result.returncode != 0 and ("pytest" in cmd or "unittest" in cmd):
                # Tests ran but failed
                return "completed"
        
        return "failed"
    
    async def _check_test_status(self, state: AgentState) -> str:
        """Check if tests passed"""
        try:
            # Try GitHub API first
            return await self.github_service.get_check_runs_status(
                state.repo_url,
                state.commit_sha
            )
        except Exception as e:
            logger.warning(f"Failed to check test status: {e}")
            
            # Fallback to local test run
            result = await self._run_local_tests(state)
            return "passed" if result == "completed" else "failed"
    
    async def _get_test_failure_count(self, state: AgentState) -> int:
        """Get number of test failures"""
        try:
            # Try to get from GitHub API
            return await self.github_service.get_test_failure_count(
                state.repo_url,
                state.commit_sha
            )
        except Exception as e:
            logger.warning(f"Failed to get test failure count: {e}")
            
            # Fallback: run tests and count failures
            return await self._count_local_test_failures(state)
    
    async def _count_local_test_failures(self, state: AgentState) -> int:
        """Count local test failures"""
        import subprocess
        import re
        
        repo_path = state.repo_path
        
        cmd = f"cd {repo_path} && python -m pytest --tb=no -q 2>&1 || true"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        # Parse output for failure count
        output = result.stdout + result.stderr
        
        # Look for patterns like "5 failed" or "FAILED (failures=5)"
        match = re.search(r'(\d+)\s+failed', output)
        if match:
            return int(match.group(1))
        
        match = re.search(r'failures=(\d+)', output)
        if match:
            return int(match.group(1))
        
        return 0