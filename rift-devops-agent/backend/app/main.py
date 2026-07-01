"""
RIFT 2026 DevOps Agent - Main Application
Autonomous CI/CD Healing Agent with Multi-Agent Architecture
UPDATED: Full GitHub OAuth support — no server GITHUB_TOKEN needed
FIXED: CORS credentials bug, Render port/env handling, persistent results dir
"""

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests as http_requests
import socketio
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, get_db
from app.models.schemas import (
    AgentRunRequest, AgentRunResponse, RunStatus, FixRecord,
    ScoreBreakdown, CICDStatus, RepositoryAnalysis, BugPattern
)
from agents.orchestrator import AgentOrchestrator
from services.github_service import GitHubService
from services.memory_service import MemoryService
from services.report_service import ReportService
from utils.logger import get_logger

logger = get_logger(__name__)

# ─── Environment / OAuth Config ───────────────────────────────────────────────
GITHUB_CLIENT_ID     = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL          = os.getenv("FRONTEND_URL", "http://localhost:5173")

# CORS: comma-separated list of allowed origins, e.g.
# "https://rift-frontend.onrender.com,http://localhost:5173"
CORS_ORIGINS = settings.CORS_ORIGINS

# Where run results / PDFs get written. Point this at a Render persistent
# disk mount path (e.g. /var/data/results) if you want results to survive
# restarts/redeploys. Defaults to /tmp for local dev.
RESULTS_DIR = os.getenv("RESULTS_DIR", "/tmp/rift-results")

ENV = os.getenv("ENV", "development")

# Store active runs
active_runs: Dict[str, Any] = {}
run_results: Dict[str, Any] = {}

# Socket.IO for real-time updates
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=CORS_ORIGINS if CORS_ORIGINS else "*",
    logger=True,
    engineio_logger=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting RIFT DevOps Agent...")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    await init_db()
    yield
    logger.info("Shutting down RIFT DevOps Agent...")

app = FastAPI(
    title="RIFT DevOps Agent API",
    description="Autonomous CI/CD Healing Agent with Multi-Agent Architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# CORS Middleware
# NOTE: allow_origins=["*"] together with allow_credentials=True is invalid —
# browsers reject wildcard origins whenever credentials are involved, which
# silently breaks CORS in production. Use explicit origins from CORS_ORIGINS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
memory_service = MemoryService()
report_service = ReportService()


# ─── Socket.IO Events ────────────────────────────────────────────────────────

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit('connected', {'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def subscribe_run(sid, data):
    """Subscribe to updates for a specific run"""
    run_id = data.get('run_id')
    if run_id:
        await sio.enter_room(sid, f"run_{run_id}")
        logger.info(f"Client {sid} subscribed to run {run_id}")
        await sio.emit('subscribed', {'run_id': run_id}, room=sid)


async def broadcast_run_update(run_id: str, data: dict):
    """Broadcast update to all clients subscribed to a run"""
    await sio.emit('run_update', {
        'run_id': run_id,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }, room=f"run_{run_id}")


# ─── GitHub OAuth Endpoints ───────────────────────────────────────────────────

@app.get("/auth/github")
async def github_login():
    """Redirect user to GitHub OAuth page"""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

    oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=repo,user"
        f"&allow_signup=true"
    )
    return RedirectResponse(oauth_url)


@app.get("/auth/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback, exchange code for token"""
    try:
        # Exchange code for access token
        token_response = http_requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
            },
            headers={"Accept": "application/json"},
            timeout=10
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            logger.error(f"No access token in response: {token_data}")
            return RedirectResponse(f"{FRONTEND_URL}?error=oauth_failed")

        # Get user info
        user_response = http_requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        user = user_response.json()
        username = user.get("login", "unknown")
        avatar_url = user.get("avatar_url", "")

        logger.info(f"OAuth successful for user: {username}")

        # Redirect to frontend with token and user info
        return RedirectResponse(
            f"{FRONTEND_URL}?token={access_token}&username={username}&avatar={avatar_url}"
        )

    except Exception as e:
        logger.exception("GitHub OAuth callback failed")
        return RedirectResponse(f"{FRONTEND_URL}?error=oauth_failed&reason={str(e)}")


@app.get("/auth/user")
async def get_current_user(token: str):
    """Get current user info from token (for frontend to verify token)"""
    try:
        user_response = http_requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        user = user_response.json()
        return {
            "username": user.get("login"),
            "name": user.get("name"),
            "avatar_url": user.get("avatar_url"),
            "email": user.get("email")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


# ─── Core Endpoints ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "RIFT DevOps Agent API",
        "version": "1.0.0",
        "status": "running",
        "environment": ENV,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "run": "/api/v1/run",
            "status": "/api/v1/status/{run_id}",
            "results": "/api/v1/results/{run_id}",
            "runs": "/api/v1/runs",
            "github_login": "/auth/github",
            "github_callback": "/auth/github/callback"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "memory": await memory_service.health_check(),
            "github": "available",
            "oauth": "configured" if GITHUB_CLIENT_ID else "not_configured"
        }
    }


@app.post("/api/v1/run", response_model=AgentRunResponse)
async def start_agent_run(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new agent run to analyze and fix a repository.
    Pass github_token from OAuth for user-scoped PRs.
    """
    run_id = str(uuid.uuid4())

    # Resolve which token to use — user's OAuth token takes priority,
    # falling back to a server-configured token if present.
    effective_token = request.github_token or settings.GITHUB_TOKEN

    if not effective_token:
        raise HTTPException(
            status_code=400,
            detail="No GitHub token available. Sign in with GitHub or configure a server-side GITHUB_TOKEN."
        )

    # Create branch name
    branch_name = (
        f"{request.team_name.upper().replace(' ', '_')}_"
        f"{request.team_leader_name.upper().replace(' ', '_')}_AI_Fix"
    )

    # Initialize run data
    run_data = {
        "run_id": run_id,
        "status": "pending",
        "repository_url": str(request.repository_url),
        "team_name": request.team_name,
        "team_leader_name": request.team_leader_name,
        "branch_name": branch_name,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "progress": 0,
        "current_stage": "initializing",
        "fixes": [],
        "errors": [],
        "cicd_iterations": 0,
        "score": None,
        "user_authenticated": bool(request.github_token)  # track if user used OAuth
    }

    active_runs[run_id] = run_data

    # Start background task
    background_tasks.add_task(
        execute_agent_run,
        run_id=run_id,
        request=request,
        branch_name=branch_name,
        effective_token=effective_token
    )

    return AgentRunResponse(
        run_id=run_id,
        status="pending",
        message="Agent run started successfully",
        branch_name=branch_name,
        estimated_time=300
    )


async def execute_agent_run(
    run_id: str,
    request: AgentRunRequest,
    branch_name: str,
    effective_token: str
):
    """
    Execute the agent run with multi-agent orchestration.
    Uses effective_token (user OAuth or fallback to env token).
    """
    start_time = datetime.utcnow()
    run_data = active_runs[run_id]
    run_data["started_at"] = start_time.isoformat()
    run_data["status"] = "running"
    run_data["current_stage"] = "cloning_repository"

    await broadcast_run_update(run_id, {
        "stage": "cloning_repository",
        "message": f"Cloning repository: {request.repository_url}",
        "progress": 5
    })

    try:
        # Initialize orchestrator with the resolved token
        orchestrator = AgentOrchestrator(
            run_id=run_id,
            github_token=effective_token,
            gemini_api_key=settings.GEMINI_API_KEY,
            broadcast_callback=broadcast_run_update
        )

        # Execute the full workflow
        result = await orchestrator.execute(
            repo_url=str(request.repository_url),
            team_name=request.team_name,
            team_leader_name=request.team_leader_name,
            branch_name=branch_name,
            max_iterations=request.max_iterations or 5
        )

        # Update run data with results
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        run_data.update({
            "status": "completed" if result["success"] else "failed",
            "completed_at": end_time.isoformat(),
            "duration_seconds": duration,
            "progress": 100,
            "current_stage": "completed",
            "fixes": result.get("fixes", []),
            "total_failures": result.get("total_failures", 0),
            "total_fixes": result.get("total_fixes", 0),
            "cicd_iterations": result.get("cicd_iterations", 0),
            "final_cicd_status": result.get("cicd_status", "unknown"),
            "score": calculate_score(result, duration),
            "pull_request_url": result.get("pull_request_url"),
            "commit_sha": result.get("commit_sha"),
            "error_message": result.get("error_message")
        })

        # Store in memory for pattern learning
        await memory_service.store_run_patterns(run_id, run_data)

        # Generate results.json
        await save_results_json(run_id, run_data)

        await broadcast_run_update(run_id, {
            "stage": "completed",
            "message": "Agent run completed successfully" if result["success"] else "Agent run failed",
            "progress": 100,
            "result": run_data
        })

    except Exception as e:
        logger.exception(f"Error in agent run {run_id}")
        run_data.update({
            "status": "failed",
            "completed_at": datetime.utcnow().isoformat(),
            "error_message": str(e),
            "current_stage": "error"
        })

        await broadcast_run_update(run_id, {
            "stage": "error",
            "message": f"Error: {str(e)}",
            "progress": 100,
            "error": str(e)
        })


def calculate_score(result: dict, duration: float) -> dict:
    """Calculate the score based on the results"""
    base_score = 100
    speed_bonus = 10 if duration < 300 else 0
    commits = result.get("total_commits", 0)
    efficiency_penalty = max(0, (commits - 20) * 2)
    success_bonus = 20 if result.get("cicd_status") == "passed" else 0
    total_score = base_score + speed_bonus - efficiency_penalty + success_bonus

    return {
        "base_score": base_score,
        "speed_bonus": speed_bonus,
        "efficiency_penalty": efficiency_penalty,
        "success_bonus": success_bonus,
        "total_score": max(0, total_score),
        "time_taken_seconds": duration
    }


async def save_results_json(run_id: str, run_data: dict):
    """Save results to JSON file"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    filepath = os.path.join(RESULTS_DIR, f"{run_id}_results.json")
    with open(filepath, 'w') as f:
        json.dump(run_data, f, indent=2, default=str)
    return filepath


# ─── Status / Results Endpoints ──────────────────────────────────────────────

@app.get("/api/v1/status/{run_id}")
async def get_run_status(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return active_runs[run_id]


@app.get("/api/v1/results/{run_id}")
async def get_run_results(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    run_data = active_runs[run_id]
    return {
        "run_id": run_id,
        "repository_url": run_data.get("repository_url"),
        "team_name": run_data.get("team_name"),
        "team_leader_name": run_data.get("team_leader_name"),
        "branch_name": run_data.get("branch_name"),
        "status": run_data.get("status"),
        "total_failures": run_data.get("total_failures", 0),
        "total_fixes": run_data.get("total_fixes", 0),
        "cicd_iterations": run_data.get("cicd_iterations", 0),
        "final_cicd_status": run_data.get("final_cicd_status"),
        "score": run_data.get("score"),
        "fixes": run_data.get("fixes", []),
        "duration_seconds": run_data.get("duration_seconds"),
        "pull_request_url": run_data.get("pull_request_url"),
        "started_at": run_data.get("started_at"),
        "completed_at": run_data.get("completed_at")
    }


@app.get("/api/v1/runs")
async def list_runs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    runs = list(active_runs.values())
    runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    total = len(runs)
    paginated_runs = runs[offset:offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "runs": paginated_runs}


@app.get("/api/v1/runs/{run_id}/fixes")
async def get_run_fixes(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run_id": run_id, "fixes": active_runs[run_id].get("fixes", [])}


@app.get("/api/v1/runs/{run_id}/diff/{fix_id}")
async def get_fix_diff(run_id: str, fix_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    fixes = active_runs[run_id].get("fixes", [])
    fix = next((f for f in fixes if f.get("id") == fix_id), None)
    if not fix:
        raise HTTPException(status_code=404, detail="Fix not found")
    return {
        "fix_id": fix_id,
        "before": fix.get("before_code"),
        "after": fix.get("after_code"),
        "file_path": fix.get("file_path"),
        "line_numbers": fix.get("line_numbers")
    }


@app.get("/api/v1/runs/{run_id}/report")
async def generate_run_report(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    run_data = active_runs[run_id]
    pdf_path = await report_service.generate_pdf_report(run_id, run_data)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"rift_report_{run_id}.pdf")


@app.get("/api/v1/runs/{run_id}/tree")
async def get_repository_tree(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    run_data = active_runs[run_id]
    tree = await memory_service.get_repository_tree(run_id)
    fixes = run_data.get("fixes", [])
    for fix in fixes:
        file_path = fix.get("file_path", "")
        await memory_service.annotate_file_with_fixes(tree, file_path, fix)
    return {"run_id": run_id, "tree": tree}


@app.get("/api/v1/bug-patterns")
async def get_bug_patterns(
    bug_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    patterns = await memory_service.get_bug_patterns(bug_type, limit)
    return {"patterns": patterns, "total": len(patterns)}


@app.get("/api/v1/runs/{run_id1}/compare/{run_id2}")
async def compare_runs(run_id1: str, run_id2: str):
    if run_id1 not in active_runs:
        raise HTTPException(status_code=404, detail=f"Run {run_id1} not found")
    if run_id2 not in active_runs:
        raise HTTPException(status_code=404, detail=f"Run {run_id2} not found")
    run1 = active_runs[run_id1]
    run2 = active_runs[run_id2]
    return {
        "run1": {
            "run_id": run_id1,
            "repository_url": run1.get("repository_url"),
            "total_fixes": run1.get("total_fixes", 0),
            "duration_seconds": run1.get("duration_seconds", 0),
            "score": run1.get("score", {}).get("total_score", 0),
            "cicd_status": run1.get("final_cicd_status")
        },
        "run2": {
            "run_id": run_id2,
            "repository_url": run2.get("repository_url"),
            "total_fixes": run2.get("total_fixes", 0),
            "duration_seconds": run2.get("duration_seconds", 0),
            "score": run2.get("score", {}).get("total_score", 0),
            "cicd_status": run2.get("final_cicd_status")
        },
        "differences": {
            "fixes_difference": run2.get("total_fixes", 0) - run1.get("total_fixes", 0),
            "time_difference": run2.get("duration_seconds", 0) - run1.get("duration_seconds", 0),
            "score_difference": (
                run2.get("score", {}).get("total_score", 0) -
                run1.get("score", {}).get("total_score", 0)
            )
        }
    }


@app.get("/api/v1/runs/{run_id}/heatmap")
async def get_bug_heatmap(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    run_data = active_runs[run_id]
    fixes = run_data.get("fixes", [])
    heatmap_data = await memory_service.generate_bug_heatmap(fixes)
    return {"run_id": run_id, "heatmap": heatmap_data}


@app.delete("/api/v1/runs/{run_id}")
async def delete_run(run_id: str):
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    del active_runs[run_id]
    return {"message": f"Run {run_id} deleted successfully"}


# Mount static files for results
os.makedirs(RESULTS_DIR, exist_ok=True)
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    reload_enabled = ENV == "development"

    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,
        log_level="info"
    )
