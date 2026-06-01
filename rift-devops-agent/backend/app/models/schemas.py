"""
Pydantic models for API requests and responses
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class BugType(str, Enum):
    """Types of bugs that can be detected and fixed"""
    LINTING = "LINTING"
    SYNTAX = "SYNTAX"
    LOGIC = "LOGIC"
    TYPE_ERROR = "TYPE_ERROR"
    IMPORT = "IMPORT"
    INDENTATION = "INDENTATION"
    UNUSED = "UNUSED"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    TEST_FAILURE = "TEST_FAILURE"


class FixStatus(str, Enum):
    """Status of a fix"""
    PENDING = "pending"
    APPLIED = "applied"
    VERIFIED = "verified"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class CICDStatus(str, Enum):
    """CI/CD pipeline status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class RunStatus(str, Enum):
    """Agent run status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRunRequest(BaseModel):
    """Request to start an agent run"""
    repository_url: HttpUrl = Field(..., description="GitHub repository URL to analyze")
    team_name: str = Field(..., min_length=1, max_length=100, description="Team name")
    team_leader_name: str = Field(..., min_length=1, max_length=100, description="Team leader name")
    max_iterations: int = Field(default=5, ge=1, le=10, description="Maximum CI/CD retry iterations")
    github_token: Optional[str] = Field(default=None, description="Optional GitHub token")
    notify_slack: Optional[str] = Field(default=None, description="Slack webhook URL for notifications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repository_url": "https://github.com/example/repo",
                "team_name": "RIFT ORGANISERS",
                "team_leader_name": "Saiyam Kumar",
                "max_iterations": 5
            }
        }


class AgentRunResponse(BaseModel):
    """Response from starting an agent run"""
    run_id: str
    status: str
    message: str
    branch_name: str
    estimated_time: int = Field(description="Estimated time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "message": "Agent run started successfully",
                "branch_name": "RIFT_ORGANISERS_SAIYAM_KUMAR_AI_Fix",
                "estimated_time": 300
            }
        }


class FixRecord(BaseModel):
    """Record of a single fix applied"""
    id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    file_path: str
    bug_type: BugType
    line_number: int
    line_end: Optional[int] = None
    commit_message: str
    status: FixStatus
    description: str
    before_code: Optional[str] = None
    after_code: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "fix-001",
                "file_path": "src/utils.py",
                "bug_type": "LINTING",
                "line_number": 15,
                "commit_message": "[AI-AGENT] Fix LINTING error in src/utils.py line 15",
                "status": "verified",
                "description": "Remove unused import 'os'",
                "before_code": "import os\nimport sys",
                "after_code": "import sys"
            }
        }


class ScoreBreakdown(BaseModel):
    """Score breakdown for a run"""
    base_score: int = 100
    speed_bonus: int = 0
    efficiency_penalty: int = 0
    success_bonus: int = 0
    total_score: int
    time_taken_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_score": 100,
                "speed_bonus": 10,
                "efficiency_penalty": 0,
                "success_bonus": 20,
                "total_score": 130,
                "time_taken_seconds": 245.5
            }
        }


class CICDIteration(BaseModel):
    """Single CI/CD iteration"""
    iteration: int
    status: CICDStatus
    timestamp: datetime
    duration_seconds: Optional[float] = None
    test_failures: Optional[int] = None
    logs_url: Optional[str] = None


class RepositoryFile(BaseModel):
    """File in repository"""
    path: str
    name: str
    type: str  # file or directory
    size: Optional[int] = None
    has_errors: bool = False
    error_count: int = 0
    fixed: bool = False
    children: Optional[List["RepositoryFile"]] = None


class RepositoryAnalysis(BaseModel):
    """Repository analysis results"""
    total_files: int
    total_lines: int
    test_files: List[str]
    file_tree: RepositoryFile
    languages: Dict[str, int]
    dependencies: Dict[str, Any]


class BugPattern(BaseModel):
    """Learned bug pattern"""
    id: str
    bug_type: BugType
    pattern: str
    fix_template: str
    occurrence_count: int
    success_count: int
    success_rate: float
    file_extensions: List[str]
    example_files: List[str]
    created_at: datetime
    last_seen_at: datetime


class RunResults(BaseModel):
    """Complete run results"""
    run_id: str
    repository_url: str
    team_name: str
    team_leader_name: str
    branch_name: str
    status: RunStatus
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Results
    total_failures: int = 0
    total_fixes: int = 0
    cicd_iterations: int = 0
    final_cicd_status: Optional[CICDStatus] = None
    
    # Details
    fixes: List[FixRecord] = []
    score: Optional[ScoreBreakdown] = None
    
    # Links
    pull_request_url: Optional[str] = None
    commit_sha: Optional[str] = None
    
    # Error info
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "550e8400-e29b-41d4-a716-446655440000",
                "repository_url": "https://github.com/example/repo",
                "team_name": "RIFT ORGANISERS",
                "team_leader_name": "Saiyam Kumar",
                "branch_name": "RIFT_ORGANISERS_SAIYAM_KUMAR_AI_Fix",
                "status": "completed",
                "total_failures": 5,
                "total_fixes": 5,
                "cicd_iterations": 3,
                "final_cicd_status": "passed",
                "score": {
                    "base_score": 100,
                    "speed_bonus": 10,
                    "efficiency_penalty": 0,
                    "success_bonus": 20,
                    "total_score": 130,
                    "time_taken_seconds": 245.5
                }
            }
        }


class RunSummary(BaseModel):
    """Summary of a run for listing"""
    run_id: str
    repository_url: str
    team_name: str
    status: RunStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_fixes: int
    final_cicd_status: Optional[CICDStatus] = None
    total_score: Optional[int] = None


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]


class AgentStage(BaseModel):
    """Agent workflow stage"""
    name: str
    description: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    agent_name: Optional[str] = None


class AgentWorkflowState(BaseModel):
    """Current state of the agent workflow"""
    run_id: str
    current_stage: str
    stages: List[AgentStage]
    active_agents: List[str]
    messages: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HeatmapData(BaseModel):
    """Bug heatmap data point"""
    path: str
    error_count: int
    fix_count: int
    intensity: float  # 0-1


class ComparisonResult(BaseModel):
    """Run comparison result"""
    run1: RunSummary
    run2: RunSummary
    differences: Dict[str, Any]
