# # """
# # Agent state management for LangGraph workflow
# # """

# # from dataclasses import dataclass, field
# # from typing import Any, Dict, List, Optional, TypedDict
# # from datetime import datetime
# # from enum import Enum


# # class AgentStatus(str, Enum):
# #     PENDING = "pending"
# #     RUNNING = "running"
# #     COMPLETED = "completed"
# #     FAILED = "failed"


# # class Fix(TypedDict):
# #     id: str
# #     file_path: str
# #     bug_type: str
# #     line_number: int
# #     description: str
# #     before_code: str
# #     after_code: str
# #     commit_message: str
# #     status: str
# #     error_message: Optional[str]


# # class CICDIteration(TypedDict):
# #     iteration: int
# #     status: str
# #     timestamp: str
# #     duration_seconds: Optional[float]
# #     test_failures: Optional[int]


# # @dataclass
# # class AgentState:
# #     """State shared across all agents in the workflow"""
    
# #     # Run identification
# #     run_id: str
    
# #     # Repository info
# #     repo_url: str
# #     repo_path: Optional[str] = None
# #     repo_name: Optional[str] = None
# #     branch_name: Optional[str] = None
    
# #     # Team info
# #     team_name: str = ""
# #     team_leader_name: str = ""
    
# #     # Analysis results
# #     file_tree: Dict[str, Any] = field(default_factory=dict)
# #     test_files: List[str] = field(default_factory=list)
# #     detected_issues: List[Dict[str, Any]] = field(default_factory=list)
    
# #     # Fixes
# #     fixes: List[Fix] = field(default_factory=list)
# #     applied_fixes: List[Fix] = field(default_factory=list)
# #     failed_fixes: List[Fix] = field(default_factory=list)
    
# #     # CI/CD tracking
# #     cicd_iterations: List[CICDIteration] = field(default_factory=list)
# #     current_iteration: int = 0
# #     max_iterations: int = 5
# #     final_cicd_status: str = "pending"
    
# #     # Git info
# #     commit_sha: Optional[str] = None
# #     pull_request_url: Optional[str] = None
    
# #     # Status
# #     status: str = "pending"
# #     current_stage: str = "initializing"
# #     error_message: Optional[str] = None
    
# #     # Timing
# #     started_at: Optional[str] = None
# #     completed_at: Optional[str] = None
    
# #     # Memory
# #     similar_patterns: List[Dict[str, Any]] = field(default_factory=list)
    
# #     # Results
# #     success: bool = False
# #     total_commits: int = 0
    
# #     def to_dict(self) -> Dict[str, Any]:
# #         """Convert state to dictionary"""
# #         return {
# #             "run_id": self.run_id,
# #             "repo_url": self.repo_url,
# #             "repo_path": self.repo_path,
# #             "repo_name": self.repo_name,
# #             "branch_name": self.branch_name,
# #             "team_name": self.team_name,
# #             "team_leader_name": self.team_leader_name,
# #             "file_tree": self.file_tree,
# #             "test_files": self.test_files,
# #             "detected_issues": self.detected_issues,
# #             "fixes": self.fixes,
# #             "applied_fixes": self.applied_fixes,
# #             "failed_fixes": self.failed_fixes,
# #             "cicd_iterations": self.cicd_iterations,
# #             "current_iteration": self.current_iteration,
# #             "max_iterations": self.max_iterations,
# #             "final_cicd_status": self.final_cicd_status,
# #             "commit_sha": self.commit_sha,
# #             "pull_request_url": self.pull_request_url,
# #             "status": self.status,
# #             "current_stage": self.current_stage,
# #             "error_message": self.error_message,
# #             "started_at": self.started_at,
# #             "completed_at": self.completed_at,
# #             "similar_patterns": self.similar_patterns,
# #             "success": self.success,
# #             "total_commits": self.total_commits
# #         }
    
# #     @classmethod
# #     def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
# #         """Create state from dictionary"""
# #         return cls(
# #             run_id=data.get("run_id", ""),
# #             repo_url=data.get("repo_url", ""),
# #             repo_path=data.get("repo_path"),
# #             repo_name=data.get("repo_name"),
# #             branch_name=data.get("branch_name"),
# #             team_name=data.get("team_name", ""),
# #             team_leader_name=data.get("team_leader_name", ""),
# #             file_tree=data.get("file_tree", {}),
# #             test_files=data.get("test_files", []),
# #             detected_issues=data.get("detected_issues", []),
# #             fixes=data.get("fixes", []),
# #             applied_fixes=data.get("applied_fixes", []),
# #             failed_fixes=data.get("failed_fixes", []),
# #             cicd_iterations=data.get("cicd_iterations", []),
# #             current_iteration=data.get("current_iteration", 0),
# #             max_iterations=data.get("max_iterations", 5),
# #             final_cicd_status=data.get("final_cicd_status", "pending"),
# #             commit_sha=data.get("commit_sha"),
# #             pull_request_url=data.get("pull_request_url"),
# #             status=data.get("status", "pending"),
# #             current_stage=data.get("current_stage", "initializing"),
# #             error_message=data.get("error_message"),
# #             started_at=data.get("started_at"),
# #             completed_at=data.get("completed_at"),
# #             similar_patterns=data.get("similar_patterns", []),
# #             success=data.get("success", False),
# #             total_commits=data.get("total_commits", 0)
# #         )


# # class WorkflowState(TypedDict):
# #     """TypedDict for LangGraph state"""
# #     run_id: str
# #     repo_url: str
# #     repo_path: Optional[str]
# #     repo_name: Optional[str]
# #     branch_name: Optional[str]
# #     team_name: str
# #     team_leader_name: str
# #     file_tree: Dict[str, Any]
# #     test_files: List[str]
# #     detected_issues: List[Dict[str, Any]]
# #     fixes: List[Fix]
# #     applied_fixes: List[Fix]
# #     failed_fixes: List[Fix]
# #     cicd_iterations: List[CICDIteration]
# #     current_iteration: int
# #     max_iterations: int
# #     final_cicd_status: str
# #     commit_sha: Optional[str]
# #     pull_request_url: Optional[str]
# #     status: str
# #     current_stage: str
# #     error_message: Optional[str]
# #     started_at: Optional[str]
# #     completed_at: Optional[str]
# #     similar_patterns: List[Dict[str, Any]]
# #     success: bool
# #     total_commits: int
# """
# Agent state management for LangGraph workflow
# """

# from dataclasses import dataclass, field
# from typing import Any, Dict, List, Optional, TypedDict
# from datetime import datetime
# from enum import Enum


# class AgentStatus(str, Enum):
#     PENDING = "pending"
#     RUNNING = "running"
#     COMPLETED = "completed"
#     FAILED = "failed"


# class Fix(TypedDict):
#     id: str
#     file_path: str
#     bug_type: str
#     line_number: int
#     description: str
#     before_code: str
#     after_code: str
#     commit_message: str
#     status: str
#     error_message: Optional[str]


# class CICDIteration(TypedDict):
#     iteration: int
#     status: str
#     timestamp: str
#     duration_seconds: Optional[float]
#     test_failures: Optional[int]


# @dataclass
# class AgentState:
#     """State shared across all agents in the workflow"""

#     # Run identification
#     run_id: str

#     # Repository info
#     repo_url: str
#     repo_path: Optional[str] = None
#     repo_name: Optional[str] = None
#     branch_name: Optional[str] = None

#     # Team info
#     team_name: str = ""
#     team_leader_name: str = ""

#     # Analysis results
#     file_tree: Dict[str, Any] = field(default_factory=dict)
#     test_files: List[str] = field(default_factory=list)
#     detected_issues: List[Dict[str, Any]] = field(default_factory=list)

#     # Fixes
#     fixes: List[Fix] = field(default_factory=list)
#     applied_fixes: List[Fix] = field(default_factory=list)
#     failed_fixes: List[Fix] = field(default_factory=list)

#     # CI/CD tracking
#     cicd_iterations: List[CICDIteration] = field(default_factory=list)
#     current_iteration: int = 0
#     max_iterations: int = 5
#     final_cicd_status: str = "pending"

#     # Git info
#     commit_sha: Optional[str] = None
#     pull_request_url: Optional[str] = None

#     # Status
#     status: str = "pending"
#     current_stage: str = "initializing"
#     error_message: Optional[str] = None

#     # Timing
#     started_at: Optional[str] = None
#     completed_at: Optional[str] = None

#     # Memory
#     similar_patterns: List[Dict[str, Any]] = field(default_factory=list)

#     # Results
#     success: bool = False
#     total_commits: int = 0

#     # Score (calculated after run completes)  ✅
#     score: Optional[Dict[str, Any]] = None

#     def to_dict(self) -> Dict[str, Any]:
#         """Convert state to dictionary"""
#         return {
#             "run_id": self.run_id,
#             "repo_url": self.repo_url,
#             "repo_path": self.repo_path,
#             "repo_name": self.repo_name,
#             "branch_name": self.branch_name,
#             "team_name": self.team_name,
#             "team_leader_name": self.team_leader_name,
#             "file_tree": self.file_tree,
#             "test_files": self.test_files,
#             "detected_issues": self.detected_issues,
#             "fixes": self.fixes,
#             "applied_fixes": self.applied_fixes,
#             "failed_fixes": self.failed_fixes,
#             "cicd_iterations": self.cicd_iterations,
#             "current_iteration": self.current_iteration,
#             "max_iterations": self.max_iterations,
#             "final_cicd_status": self.final_cicd_status,
#             "commit_sha": self.commit_sha,
#             "pull_request_url": self.pull_request_url,
#             "status": self.status,
#             "current_stage": self.current_stage,
#             "error_message": self.error_message,
#             "started_at": self.started_at,
#             "completed_at": self.completed_at,
#             "similar_patterns": self.similar_patterns,
#             "success": self.success,
#             "total_commits": self.total_commits,
#             "score": self.score,  # ✅
#         }

#     @classmethod
#     def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
#         """Create state from dictionary"""
#         return cls(
#             run_id=data.get("run_id", ""),
#             repo_url=data.get("repo_url", ""),
#             repo_path=data.get("repo_path"),
#             repo_name=data.get("repo_name"),
#             branch_name=data.get("branch_name"),
#             team_name=data.get("team_name", ""),
#             team_leader_name=data.get("team_leader_name", ""),
#             file_tree=data.get("file_tree", {}),
#             test_files=data.get("test_files", []),
#             detected_issues=data.get("detected_issues", []),
#             fixes=data.get("fixes", []),
#             applied_fixes=data.get("applied_fixes", []),
#             failed_fixes=data.get("failed_fixes", []),
#             cicd_iterations=data.get("cicd_iterations", []),
#             current_iteration=data.get("current_iteration", 0),
#             max_iterations=data.get("max_iterations", 5),
#             final_cicd_status=data.get("final_cicd_status", "pending"),
#             commit_sha=data.get("commit_sha"),
#             pull_request_url=data.get("pull_request_url"),
#             status=data.get("status", "pending"),
#             current_stage=data.get("current_stage", "initializing"),
#             error_message=data.get("error_message"),
#             started_at=data.get("started_at"),
#             completed_at=data.get("completed_at"),
#             similar_patterns=data.get("similar_patterns", []),
#             success=data.get("success", False),
#             total_commits=data.get("total_commits", 0),
#             score=data.get("score", None),  # ✅
#         )


# class WorkflowState(TypedDict):
#     """TypedDict for LangGraph state"""
#     run_id: str
#     repo_url: str
#     repo_path: Optional[str]
#     repo_name: Optional[str]
#     branch_name: Optional[str]
#     team_name: str
#     team_leader_name: str
#     file_tree: Dict[str, Any]
#     test_files: List[str]
#     detected_issues: List[Dict[str, Any]]
#     fixes: List[Fix]
#     applied_fixes: List[Fix]
#     failed_fixes: List[Fix]
#     cicd_iterations: List[CICDIteration]
#     current_iteration: int
#     max_iterations: int
#     final_cicd_status: str
#     commit_sha: Optional[str]
#     pull_request_url: Optional[str]
#     status: str
#     current_stage: str
#     error_message: Optional[str]
#     started_at: Optional[str]
#     completed_at: Optional[str]
#     similar_patterns: List[Dict[str, Any]]
#     success: bool
#     total_commits: int
#     score: Optional[Dict[str, Any]]  # this was missing — caused the InvalidUpdateError
"""
Agent state management for LangGraph workflow
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Fix(TypedDict):
    id: str
    file_path: str
    bug_type: str
    line_number: int
    description: str
    before_code: str
    after_code: str
    commit_message: str
    status: str
    error_message: Optional[str]


class CICDIteration(TypedDict):
    iteration: int
    status: str
    timestamp: str
    duration_seconds: Optional[float]
    test_failures: Optional[int]


@dataclass
class AgentState:
    """State shared across all agents in the workflow"""

    # Run identification
    run_id: str

    # Repository info
    repo_url: str
    repo_path: Optional[str] = None
    repo_name: Optional[str] = None
    branch_name: Optional[str] = None

    # Team info
    team_name: str = ""
    team_leader_name: str = ""

    # Analysis results
    file_tree: Dict[str, Any] = field(default_factory=dict)
    test_files: List[str] = field(default_factory=list)
    detected_issues: List[Dict[str, Any]] = field(default_factory=list)

    # Fixes
    fixes: List[Fix] = field(default_factory=list)
    applied_fixes: List[Fix] = field(default_factory=list)
    failed_fixes: List[Fix] = field(default_factory=list)

    # CI/CD tracking
    cicd_iterations: List[CICDIteration] = field(default_factory=list)
    current_iteration: int = 0
    max_iterations: int = 5
    final_cicd_status: str = "pending"

    # Git info
    commit_sha: Optional[str] = None
    pull_request_url: Optional[str] = None

    # Status
    status: str = "pending"
    current_stage: str = "initializing"
    error_message: Optional[str] = None

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Memory
    similar_patterns: List[Dict[str, Any]] = field(default_factory=list)

    # Results
    success: bool = False
    total_commits: int = 0

    # Score
    score: Optional[Dict[str, Any]] = None

    # ── GitHub OAuth fields (NEW) ──────────────────────────────────────────
    # User's OAuth token — used to push branch directly to original repo
    # and create PR attributed to the user
    user_github_token: Optional[str] = None

    # Set to True after we verify the user has write access to the repo
    has_write_access: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "run_id": self.run_id,
            "repo_url": self.repo_url,
            "repo_path": self.repo_path,
            "repo_name": self.repo_name,
            "branch_name": self.branch_name,
            "team_name": self.team_name,
            "team_leader_name": self.team_leader_name,
            "file_tree": self.file_tree,
            "test_files": self.test_files,
            "detected_issues": self.detected_issues,
            "fixes": self.fixes,
            "applied_fixes": self.applied_fixes,
            "failed_fixes": self.failed_fixes,
            "cicd_iterations": self.cicd_iterations,
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "final_cicd_status": self.final_cicd_status,
            "commit_sha": self.commit_sha,
            "pull_request_url": self.pull_request_url,
            "status": self.status,
            "current_stage": self.current_stage,
            "error_message": self.error_message,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "similar_patterns": self.similar_patterns,
            "success": self.success,
            "total_commits": self.total_commits,
            "score": self.score,
            "user_github_token": self.user_github_token,
            "has_write_access": self.has_write_access,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create state from dictionary"""
        return cls(
            run_id=data.get("run_id", ""),
            repo_url=data.get("repo_url", ""),
            repo_path=data.get("repo_path"),
            repo_name=data.get("repo_name"),
            branch_name=data.get("branch_name"),
            team_name=data.get("team_name", ""),
            team_leader_name=data.get("team_leader_name", ""),
            file_tree=data.get("file_tree", {}),
            test_files=data.get("test_files", []),
            detected_issues=data.get("detected_issues", []),
            fixes=data.get("fixes", []),
            applied_fixes=data.get("applied_fixes", []),
            failed_fixes=data.get("failed_fixes", []),
            cicd_iterations=data.get("cicd_iterations", []),
            current_iteration=data.get("current_iteration", 0),
            max_iterations=data.get("max_iterations", 5),
            final_cicd_status=data.get("final_cicd_status", "pending"),
            commit_sha=data.get("commit_sha"),
            pull_request_url=data.get("pull_request_url"),
            status=data.get("status", "pending"),
            current_stage=data.get("current_stage", "initializing"),
            error_message=data.get("error_message"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            similar_patterns=data.get("similar_patterns", []),
            success=data.get("success", False),
            total_commits=data.get("total_commits", 0),
            score=data.get("score", None),
            user_github_token=data.get("user_github_token", None),
            has_write_access=data.get("has_write_access", False),
        )


class WorkflowState(TypedDict):
    """TypedDict for LangGraph state"""
    run_id: str
    repo_url: str
    repo_path: Optional[str]
    repo_name: Optional[str]
    branch_name: Optional[str]
    team_name: str
    team_leader_name: str
    file_tree: Dict[str, Any]
    test_files: List[str]
    detected_issues: List[Dict[str, Any]]
    fixes: List[Fix]
    applied_fixes: List[Fix]
    failed_fixes: List[Fix]
    cicd_iterations: List[CICDIteration]
    current_iteration: int
    max_iterations: int
    final_cicd_status: str
    commit_sha: Optional[str]
    pull_request_url: Optional[str]
    status: str
    current_stage: str
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    similar_patterns: List[Dict[str, Any]]
    success: bool
    total_commits: int
    score: Optional[Dict[str, Any]]
    # ── OAuth fields (NEW) ──
    user_github_token: Optional[str]
    has_write_access: bool