"""
GitHub Service
Handles all GitHub API interactions
"""

import re
from typing import Any, Dict, List, Optional

from github import Github
from github.GithubException import GithubException

from utils.logger import get_logger

logger = get_logger(__name__)


class GitHubService:
    """
    Service for interacting with GitHub API
    """
    
    def __init__(self, token: str):
        self.token = token
        self.github = Github(token) if token else None
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub URL to get owner and repo name"""
        # Handle different URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'github\.com:([^/]+)/([^/]+?)(?:\.git)?/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1), match.group(2)
        
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    async def get_repository(self, repo_url: str):
        """Get repository object from URL"""
        if not self.github:
            raise ValueError("GitHub token not provided")
        
        owner, repo_name = self._parse_repo_url(repo_url)
        return self.github.get_repo(f"{owner}/{repo_name}")
    
    async def create_pull_request(
        self,
        repo_url: str,
        branch_name: str,
        title: str,
        body: str,
        base_branch: str = "main"
    ) -> Optional[str]:
        """
        Create a pull request
        
        Args:
            repo_url: Repository URL
            branch_name: Branch to merge from
            title: PR title
            body: PR body
            base_branch: Branch to merge into
            
        Returns:
            PR URL if successful
        """
        try:
            repo = await self.get_repository(repo_url)
            
            # Try to get default branch if not specified
            if base_branch == "main":
                try:
                    base_branch = repo.default_branch
                except:
                    pass
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base_branch
            )
            
            logger.info(f"Created PR: {pr.html_url}")
            return pr.html_url
            
        except GithubException as e:
            if e.status == 422 and "A pull request already exists" in str(e):
                # PR already exists, find it
                try:
                    repo = await self.get_repository(repo_url)
                    pulls = repo.get_pulls(head=branch_name, state="open")
                    for pr in pulls:
                        return pr.html_url
                except:
                    pass
            
            logger.error(f"Failed to create PR: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    async def get_workflow_status(self, repo_url: str, branch: str) -> str:
        """
        Get workflow run status for a branch
        
        Returns:
            "queued", "waiting", "in_progress", "completed", "failed"
        """
        try:
            repo = await self.get_repository(repo_url)
            
            # Get workflow runs for the branch
            runs = repo.get_workflow_runs(branch=branch)
            
            if runs.totalCount == 0:
                return "waiting"  # No runs yet
            
            # Get the most recent run
            latest_run = runs[0]
            
            status_map = {
                "queued": "queued",
                "waiting": "waiting",
                "in_progress": "running",
                "completed": "completed",
                "action_required": "failed",
                "cancelled": "failed",
                "failure": "failed",
                "neutral": "completed",
                "skipped": "completed",
                "stale": "failed",
                "startup_failure": "failed",
                "success": "completed",
                "timed_out": "failed"
            }
            
            return status_map.get(latest_run.status, "running")
            
        except Exception as e:
            logger.warning(f"Failed to get workflow status: {e}")
            return "waiting"
    
    async def get_check_runs_status(self, repo_url: str, commit_sha: str) -> str:
        """
        Get check runs status for a commit
        
        Returns:
            "passed", "failed", "pending"
        """
        try:
            repo = await self.get_repository(repo_url)
            
            # Get check runs for the commit
            check_runs = repo.get_commit(commit_sha).get_check_runs()
            
            if check_runs.totalCount == 0:
                return "pending"
            
            # Check all check runs
            all_passed = True
            any_failed = False
            
            for check in check_runs:
                if check.conclusion not in ["success", "neutral", "skipped"]:
                    all_passed = False
                if check.conclusion in ["failure", "cancelled", "timed_out", "action_required"]:
                    any_failed = True
            
            if any_failed:
                return "failed"
            elif all_passed:
                return "passed"
            else:
                return "pending"
                
        except Exception as e:
            logger.warning(f"Failed to get check runs status: {e}")
            return "pending"
    
    async def get_test_failure_count(self, repo_url: str, commit_sha: str) -> int:
        """Get number of test failures from check runs"""
        try:
            repo = await self.get_repository(repo_url)
            check_runs = repo.get_commit(commit_sha).get_check_runs()
            
            total_failures = 0
            
            for check in check_runs:
                if check.conclusion == "failure":
                    # Try to get annotations
                    try:
                        annotations = check.get_annotations()
                        total_failures += annotations.totalCount
                    except:
                        total_failures += 1
            
            return total_failures
            
        except Exception as e:
            logger.warning(f"Failed to get test failure count: {e}")
            return 0
    
    async def get_file_content(self, repo_url: str, file_path: str, ref: str = "main") -> str:
        """Get file content from repository"""
        try:
            repo = await self.get_repository(repo_url)
            
            # Try to get content
            content = repo.get_contents(file_path, ref=ref)
            
            if content:
                import base64
                return base64.b64decode(content.content).decode('utf-8')
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to get file content: {e}")
            return ""
    
    async def create_issue_comment(
        self,
        repo_url: str,
        issue_number: int,
        body: str
    ) -> bool:
        """Create a comment on an issue or PR"""
        try:
            repo = await self.get_repository(repo_url)
            issue = repo.get_issue(issue_number)
            issue.create_comment(body)
            return True
        except Exception as e:
            logger.error(f"Failed to create comment: {e}")
            return False
    
    async def get_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """Get repository information"""
        try:
            repo = await self.get_repository(repo_url)
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "default_branch": repo.default_branch,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "private": repo.private
            }
            
        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            return {}
