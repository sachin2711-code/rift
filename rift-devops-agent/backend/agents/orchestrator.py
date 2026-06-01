# """
# Agent Orchestrator using LangGraph
# Manages the multi-agent workflow for autonomous CI/CD healing
# """

# import asyncio
# import os
# import tempfile
# from datetime import datetime
# from typing import Any, Callable, Dict, List, Optional

# from langchain_openai import ChatOpenAI
# from langgraph.graph import StateGraph, END
# from langgraph.checkpoint.memory import MemorySaver

# from agents.state import AgentState, WorkflowState
# from agents.analyzer import AnalyzerAgent
# from agents.fixer import FixerAgent
# from agents.committer import CommitterAgent
# from agents.ci_watcher import CIWatcherAgent
# from agents.learner import LearnerAgent
# from services.github_service import GitHubService
# from services.memory_service import MemoryService
# from utils.logger import get_logger

# logger = get_logger(__name__)


# class AgentOrchestrator:
#     """
#     Orchestrates the multi-agent workflow using LangGraph
    
#     Workflow:
#     1. Analyzer Agent: Clone repo, analyze structure, detect issues
#     2. Learner Agent: Search memory for similar patterns
#     3. Fixer Agent: Generate and apply fixes
#     4. Committer Agent: Commit fixes and push to branch
#     5. CI Watcher Agent: Monitor CI/CD pipeline
#     6. (Loop back to Fixer if CI fails and retries < max)
#     7. Create PR if all tests pass
#     """
    
#     def __init__(
#         self,
#         run_id: str,
#         github_token: str,
#         openai_api_key: str,
#         broadcast_callback: Optional[Callable] = None
#     ):
#         self.run_id = run_id
#         self.github_token = github_token
#         self.openai_api_key = openai_api_key
#         self.broadcast_callback = broadcast_callback
        
#         # Initialize LLM
#         self.llm = ChatOpenAI(
#             model="gpt-4-turbo-preview",
#             temperature=0.1,
#             api_key=openai_api_key
#         )
        
#         # Initialize services
#         self.github_service = GitHubService(github_token)
#         self.memory_service = MemoryService()
        
#         # Initialize agents
#         self.analyzer = AnalyzerAgent(self.llm)
#         self.learner = LearnerAgent(self.llm, self.memory_service)
#         self.fixer = FixerAgent(self.llm)
#         self.committer = CommitterAgent(self.llm, self.github_service)
#         self.ci_watcher = CIWatcherAgent(self.llm, self.github_service)
        
#         # Build workflow graph
#         self.workflow = self._build_workflow()
        
#         logger.info(f"Orchestrator initialized for run {run_id}")
    
#     def _build_workflow(self) -> StateGraph:
#         """Build the LangGraph workflow"""
        
#         # Define the workflow graph
#         workflow = StateGraph(WorkflowState)
        
#         # Add nodes (agents)
#         workflow.add_node("analyzer", self._analyzer_node)
#         workflow.add_node("learner", self._learner_node)
#         workflow.add_node("fixer", self._fixer_node)
#         workflow.add_node("committer", self._committer_node)
#         workflow.add_node("ci_watcher", self._ci_watcher_node)
#         workflow.add_node("finalize", self._finalize_node)
        
#         # Add edges
#         workflow.set_entry_point("analyzer")
#         workflow.add_edge("analyzer", "learner")
#         workflow.add_edge("learner", "fixer")
#         workflow.add_edge("fixer", "committer")
#         workflow.add_edge("committer", "ci_watcher")
        
#         # Conditional edge from CI watcher
#         workflow.add_conditional_edges(
#             "ci_watcher",
#             self._should_continue_or_finish,
#             {
#                 "fix_more": "fixer",
#                 "finalize": "finalize"
#             }
#         )
        
#         workflow.add_edge("finalize", END)
        
#         return workflow.compile(checkpointer=MemorySaver())
    
#     async def _analyzer_node(self, state: WorkflowState) -> WorkflowState:
#         """Analyzer agent node"""
#         logger.info(f"[{self.run_id}] Analyzer node starting")
        
#         await self._broadcast("analyzing", "Analyzing repository structure", 10)
        
#         try:
#             agent_state = AgentState.from_dict(state)
            
#             # Clone repository
#             repo_path = await self._clone_repository(agent_state.repo_url)
#             agent_state.repo_path = repo_path
#             agent_state.repo_name = os.path.basename(repo_path).replace('.git', '')
            
#             # Analyze repository
#             result = await self.analyzer.analyze(agent_state)
            
#             # Update state
#             state.update({
#                 "repo_path": result.repo_path,
#                 "repo_name": result.repo_name,
#                 "file_tree": result.file_tree,
#                 "test_files": result.test_files,
#                 "detected_issues": result.detected_issues,
#                 "current_stage": "analysis_complete"
#             })
            
#             await self._broadcast(
#                 "analysis_complete",
#                 f"Found {len(result.detected_issues)} issues in {len(result.test_files)} test files",
#                 20
#             )
            
#         except Exception as e:
#             logger.exception(f"[{self.run_id}] Analyzer node failed")
#             state["error_message"] = str(e)
#             state["status"] = "failed"
        
#         return state
    
#     async def _learner_node(self, state: WorkflowState) -> WorkflowState:
#         """Learner agent node - search memory for similar patterns"""
#         logger.info(f"[{self.run_id}] Learner node starting")
        
#         await self._broadcast("learning", "Searching memory for similar patterns", 25)
        
#         try:
#             agent_state = AgentState.from_dict(state)
            
#             # Search for similar patterns
#             result = await self.learner.search_patterns(agent_state)
            
#             # Update state
#             state["similar_patterns"] = [
#                 {
#                     "pattern": p.pattern,
#                     "bug_type": p.bug_type,
#                     "success_rate": p.success_rate,
#                     "fix_template": p.fix_template
#                 }
#                 for p in result.similar_patterns
#             ]
#             state["current_stage"] = "learning_complete"
            
#             await self._broadcast(
#                 "learning_complete",
#                 f"Found {len(result.similar_patterns)} similar patterns from memory",
#                 30
#             )
            
#         except Exception as e:
#             logger.exception(f"[{self.run_id}] Learner node failed")
#             # Non-critical, continue without patterns
#             state["similar_patterns"] = []
        
#         return state
    
#     async def _fixer_node(self, state: WorkflowState) -> WorkflowState:
#         """Fixer agent node - generate and apply fixes"""
#         logger.info(f"[{self.run_id}] Fixer node starting")
        
#         await self._broadcast("fixing", "Generating and applying fixes", 35)
        
#         try:
#             agent_state = AgentState.from_dict(state)
            
#             # Generate fixes
#             result = await self.fixer.fix(agent_state)
            
#             # Update state
#             state["fixes"] = result.fixes
#             state["applied_fixes"] = result.applied_fixes
#             state["failed_fixes"] = result.failed_fixes
#             state["current_stage"] = "fixing_complete"
            
#             await self._broadcast(
#                 "fixing_complete",
#                 f"Applied {len(result.applied_fixes)} fixes, {len(result.failed_fixes)} failed",
#                 50
#             )
            
#         except Exception as e:
#             logger.exception(f"[{self.run_id}] Fixer node failed")
#             state["error_message"] = str(e)
#             state["status"] = "failed"
        
#         return state
    
#     async def _committer_node(self, state: WorkflowState) -> WorkflowState:
#         """Committer agent node - commit and push fixes"""
#         logger.info(f"[{self.run_id}] Committer node starting")
        
#         await self._broadcast("committing", "Committing and pushing fixes", 55)
        
#         try:
#             agent_state = AgentState.from_dict(state)
            
#             # Commit fixes
#             result = await self.committer.commit(agent_state)
            
#             # Update state
#             state["commit_sha"] = result.commit_sha
#             state["total_commits"] = result.total_commits
#             state["current_stage"] = "committing_complete"
            
#             await self._broadcast(
#                 "committing_complete",
#                 f"Created {result.total_commits} commits",
#                 60
#             )
            
#         except Exception as e:
#             logger.exception(f"[{self.run_id}] Committer node failed")
#             state["error_message"] = str(e)
#             state["status"] = "failed"
        
#         return state
    
#     async def _ci_watcher_node(self, state: WorkflowState) -> WorkflowState:
#         """CI Watcher agent node - monitor CI/CD pipeline"""
#         logger.info(f"[{self.run_id}] CI Watcher node starting")
        
#         await self._broadcast("watching_ci", "Monitoring CI/CD pipeline", 65)
        
#         try:
#             agent_state = AgentState.from_dict(state)
            
#             # Monitor CI/CD
#             result = await self.ci_watcher.watch(agent_state)
            
#             # Update state
#             state["cicd_iterations"] = [
#                 {
#                     "iteration": i.iteration,
#                     "status": i.status,
#                     "timestamp": i.timestamp,
#                     "duration_seconds": i.duration_seconds,
#                     "test_failures": i.test_failures
#                 }
#                 for i in result.cicd_iterations
#             ]
#             state["current_iteration"] = result.current_iteration
#             state["final_cicd_status"] = result.final_cicd_status
#             state["current_stage"] = "ci_watching_complete"
            
#             await self._broadcast(
#                 "ci_watching_complete",
#                 f"CI/CD status: {result.final_cicd_status} (iteration {result.current_iteration})",
#                 80
#             )
            
#         except Exception as e:
#             logger.exception(f"[{self.run_id}] CI Watcher node failed")
#             state["error_message"] = str(e)
#             state["status"] = "failed"
        
#         return state
    
#     async def _finalize_node(self, state: WorkflowState) -> WorkflowState:
#         """Finalize node - create PR and complete"""
#         logger.info(f"[{self.run_id}] Finalize node starting")
        
#         await self._broadcast("finalizing", "Creating pull request and finalizing", 90)
        
#         try:
#             agent_state = AgentState.from_dict(state)
            
#             # Create PR if CI passed
#             if agent_state.final_cicd_status == "passed":
#                 pr_url = await self.github_service.create_pull_request(
#                     repo_url=agent_state.repo_url,
#                     branch_name=agent_state.branch_name,
#                     title=f"[AI-AGENT] Automated fixes for {agent_state.repo_name}",
#                     body=self._generate_pr_description(agent_state)
#                 )
#                 state["pull_request_url"] = pr_url
            
#             # Update final state
#             state["status"] = "completed"
#             state["success"] = agent_state.final_cicd_status == "passed"
#             state["completed_at"] = datetime.utcnow().isoformat()
#             state["current_stage"] = "completed"
            
#             await self._broadcast(
#                 "completed",
#                 f"Agent run completed. Status: {'SUCCESS' if state['success'] else 'FAILED'}",
#                 100
#             )
            
#         except Exception as e:
#             logger.exception(f"[{self.run_id}] Finalize node failed")
#             state["error_message"] = str(e)
#             state["status"] = "failed"
        
#         return state
    
#     def _should_continue_or_finish(self, state: WorkflowState) -> str:
#         """Decide whether to continue fixing or finish"""
        
#         # If failed, finish
#         if state.get("status") == "failed":
#             return "finalize"
        
#         # If CI passed, finish
#         if state.get("final_cicd_status") == "passed":
#             return "finalize"
        
#         # If max iterations reached, finish
#         if state.get("current_iteration", 0) >= state.get("max_iterations", 5):
#             return "finalize"
        
#         # Continue fixing
#         return "fix_more"
    
#     async def _clone_repository(self, repo_url: str) -> str:
#         """Clone repository to temporary directory"""
#         import subprocess
        
#         repo_name = repo_url.split('/')[-1].replace('.git', '')
#         repo_path = os.path.join(tempfile.gettempdir(), f"rift-{self.run_id}-{repo_name}")
        
#         # Remove if exists
#         if os.path.exists(repo_path):
#             import shutil
#             shutil.rmtree(repo_path)
        
#         # Clone
#         cmd = f"git clone {repo_url} {repo_path}"
#         result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
#         if result.returncode != 0:
#             raise Exception(f"Failed to clone repository: {result.stderr}")
        
#         logger.info(f"Cloned repository to {repo_path}")
#         return repo_path
    
#     async def _broadcast(self, stage: str, message: str, progress: int):
#         """Broadcast update via WebSocket"""
#         if self.broadcast_callback:
#             await self.broadcast_callback(self.run_id, {
#                 "stage": stage,
#                 "message": message,
#                 "progress": progress
#             })
    
#     def _generate_pr_description(self, state: AgentState) -> str:
#         """Generate PR description"""
#         fixes_summary = "\n".join([
#             f"- **{fix['file_path']}**: {fix['description']} ({fix['bug_type']})"
#             for fix in state.applied_fixes[:10]  # Limit to first 10
#         ])
        
#         if len(state.applied_fixes) > 10:
#             fixes_summary += f"\n- ... and {len(state.applied_fixes) - 10} more fixes"
        
#         return f"""# 🤖 AI-AGENT Automated Fixes

# This pull request contains automated fixes generated by the RIFT DevOps Agent.

# ## Summary
# - **Total Fixes Applied**: {len(state.applied_fixes)}
# - **CI/CD Status**: {state.final_cicd_status.upper()}
# - **Iterations**: {state.current_iteration}

# ## Fixes Applied
# {fixes_summary}

# ## Details
# - Branch: `{state.branch_name}`
# - Commit: `{state.commit_sha[:8] if state.commit_sha else 'N/A'}`

# ---
# *Generated by RIFT DevOps Agent*
# """
    
#     async def execute(
#         self,
#         repo_url: str,
#         team_name: str,
#         team_leader_name: str,
#         branch_name: str,
#         max_iterations: int = 5
#     ) -> Dict[str, Any]:
#         """
#         Execute the full agent workflow
        
#         Args:
#             repo_url: GitHub repository URL
#             team_name: Team name
#             team_leader_name: Team leader name
#             branch_name: Branch name to create
#             max_iterations: Maximum CI/CD retry iterations
            
#         Returns:
#             Dictionary with execution results
#         """
#         logger.info(f"[{self.run_id}] Starting execution for {repo_url}")
        
#         # Initialize state
#         initial_state: WorkflowState = {
#             "run_id": self.run_id,
#             "repo_url": repo_url,
#             "repo_path": None,
#             "repo_name": None,
#             "branch_name": branch_name,
#             "team_name": team_name,
#             "team_leader_name": team_leader_name,
#             "file_tree": {},
#             "test_files": [],
#             "detected_issues": [],
#             "fixes": [],
#             "applied_fixes": [],
#             "failed_fixes": [],
#             "cicd_iterations": [],
#             "current_iteration": 0,
#             "max_iterations": max_iterations,
#             "final_cicd_status": "pending",
#             "commit_sha": None,
#             "pull_request_url": None,
#             "status": "running",
#             "current_stage": "initializing",
#             "error_message": None,
#             "started_at": datetime.utcnow().isoformat(),
#             "completed_at": None,
#             "similar_patterns": [],
#             "success": False,
#             "total_commits": 0
#         }
        
#         # Execute workflow
#         config = {"configurable": {"thread_id": self.run_id}}
#         result = await self.workflow.ainvoke(initial_state, config)
        
#         # Convert to result dictionary
#         return {
#             "success": result.get("success", False),
#             "run_id": self.run_id,
#             "total_failures": len(result.get("detected_issues", [])),
#             "total_fixes": len(result.get("applied_fixes", [])),
#             "total_commits": result.get("total_commits", 0),
#             "cicd_iterations": result.get("current_iteration", 0),
#             "cicd_status": result.get("final_cicd_status"),
#             "fixes": result.get("applied_fixes", []),
#             "commit_sha": result.get("commit_sha"),
#             "pull_request_url": result.get("pull_request_url"),
#             "error_message": result.get("error_message"),
#             "duration_seconds": None  # Calculated by caller
#         }
"""
Agent Orchestrator using LangGraph
Manages the multi-agent workflow for autonomous CI/CD healing
"""

import asyncio
import os
import tempfile
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.state import AgentState, WorkflowState
from agents.analyzer import AnalyzerAgent
from agents.fixer import FixerAgent
from agents.committer import CommitterAgent
from agents.ci_watcher import CIWatcherAgent
from agents.learner import LearnerAgent
from services.github_service import GitHubService
from services.memory_service import MemoryService
from utils.logger import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow using LangGraph

    Workflow:
    1. Analyzer Agent: Clone repo, analyze structure, detect issues
    2. Learner Agent: Search memory for similar patterns
    3. Fixer Agent: Generate and apply fixes
    4. Committer Agent: Commit fixes and push to branch
    5.  Broadcast results_ready — frontend unlocks here
    6. CI Watcher Agent: Monitor CI/CD pipeline (background)
    7. (Loop back to Fixer if CI fails and retries < max)
    8. Create PR and finalize
    """

    def __init__(
        self,
        run_id: str,
        github_token: str,
        gemini_api_key: str,
        broadcast_callback: Optional[Callable] = None
    ):
        self.run_id = run_id
        self.github_token = github_token
        # self.openai_api_key = openai_api_key
        self.broadcast_callback = broadcast_callback

        # Initialize LLM
        # self.llm = ChatOpenAI(
        #     model="gpt-4-turbo-preview",
        #     temperature=0.1,
        #     api_key=openai_api_key
        # )
        self.gemini_api_key = gemini_api_key
        self.llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1,
        google_api_key=gemini_api_key    )

        # Initialize services
        self.github_service = GitHubService(github_token)
        self.memory_service = MemoryService()

        # Initialize agents
        self.analyzer = AnalyzerAgent(self.llm)
        self.learner = LearnerAgent(self.llm, self.memory_service)
        self.fixer = FixerAgent(self.llm)
        self.committer = CommitterAgent(self.llm, self.github_service)
        self.ci_watcher = CIWatcherAgent(self.llm, self.github_service)

        # Build workflow graph
        self.workflow = self._build_workflow()

        logger.info(f"Orchestrator initialized for run {run_id}")

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""

        workflow = StateGraph(WorkflowState)

        # Add nodes (agents)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("learner", self._learner_node)
        workflow.add_node("fixer", self._fixer_node)
        workflow.add_node("committer", self._committer_node)
        workflow.add_node("ci_watcher", self._ci_watcher_node)
        workflow.add_node("finalize", self._finalize_node)

        # Add edges
        workflow.set_entry_point("analyzer")
        workflow.add_edge("analyzer", "learner")
        workflow.add_edge("learner", "fixer")
        workflow.add_edge("fixer", "committer")
        workflow.add_edge("committer", "ci_watcher")

        # Conditional edge from CI watcher
        workflow.add_conditional_edges(
            "ci_watcher",
            self._should_continue_or_finish,
            {
                "fix_more": "fixer",
                "finalize": "finalize"
            }
        )

        workflow.add_edge("finalize", END)

        return workflow.compile(checkpointer=MemorySaver())

    async def _analyzer_node(self, state: WorkflowState) -> WorkflowState:
        """Analyzer agent node"""
        logger.info(f"[{self.run_id}] Analyzer node starting")

        await self._broadcast("analyzing", "Analyzing repository structure", 10)

        try:
            agent_state = AgentState.from_dict(state)

            # Clone repository
            repo_path = await self._clone_repository(agent_state.repo_url)
            agent_state.repo_path = repo_path
            agent_state.repo_name = os.path.basename(repo_path).replace('.git', '')

            # Analyze repository
            result = await self.analyzer.analyze(agent_state)

            # Update state
            state.update({
                "repo_path": result.repo_path,
                "repo_name": result.repo_name,
                "file_tree": result.file_tree,
                "test_files": result.test_files,
                "detected_issues": result.detected_issues,
                "current_stage": "analysis_complete"
            })

            await self._broadcast(
                "analysis_complete",
                f"Found {len(result.detected_issues)} issues in {len(result.test_files)} test files",
                20
            )

        except Exception as e:
            logger.exception(f"[{self.run_id}] Analyzer node failed")
            state["error_message"] = str(e)
            state["status"] = "failed"
            await self._broadcast("error", f"Analyzer failed: {str(e)}", 0)

        return state

    async def _learner_node(self, state: WorkflowState) -> WorkflowState:
        """Learner agent node - search memory for similar patterns"""
        logger.info(f"[{self.run_id}] Learner node starting")

        await self._broadcast("learning", "Searching memory for similar patterns", 25)

        try:
            agent_state = AgentState.from_dict(state)

            # Search for similar patterns
            result = await self.learner.search_patterns(agent_state)

            # Update state
            state["similar_patterns"] = [
                {
                    "pattern": p.pattern,
                    "bug_type": p.bug_type,
                    "success_rate": p.success_rate,
                    "fix_template": p.fix_template
                }
                for p in result.similar_patterns
            ]
            state["current_stage"] = "learning_complete"

            await self._broadcast(
                "learning_complete",
                f"Found {len(result.similar_patterns)} similar patterns from memory",
                30
            )

        except Exception as e:
            logger.exception(f"[{self.run_id}] Learner node failed")
            # Non-critical, continue without patterns
            state["similar_patterns"] = []

        return state

    async def _fixer_node(self, state: WorkflowState) -> WorkflowState:
        """Fixer agent node - generate and apply fixes"""
        logger.info(f"[{self.run_id}] Fixer node starting")

        await self._broadcast("fixing", "Generating and applying fixes", 35)

        try:
            agent_state = AgentState.from_dict(state)

            # Generate fixes
            result = await self.fixer.fix(agent_state)

            # Update state
            state["fixes"] = result.fixes
            state["applied_fixes"] = result.applied_fixes
            state["failed_fixes"] = result.failed_fixes
            state["current_stage"] = "fixing_complete"

            await self._broadcast(
                "fixing_complete",
                f"Applied {len(result.applied_fixes)} fixes, {len(result.failed_fixes)} failed",
                50
            )

        except Exception as e:
            logger.exception(f"[{self.run_id}] Fixer node failed")
            state["error_message"] = str(e)
            state["status"] = "failed"
            await self._broadcast("error", f"Fixer failed: {str(e)}", 0)

        return state

    async def _committer_node(self, state: WorkflowState) -> WorkflowState:
        """Committer agent node - commit and push fixes"""
        logger.info(f"[{self.run_id}] Committer node starting")

        await self._broadcast("committing", "Committing and pushing fixes", 55)

        try:
            agent_state = AgentState.from_dict(state)

            # Commit fixes
            result = await self.committer.commit(agent_state)

            # Update state
            state["commit_sha"] = result.commit_sha
            state["total_commits"] = result.total_commits
            state["current_stage"] = "committing_complete"

            await self._broadcast(
                "committing_complete",
                f"Created {result.total_commits} commits",
                60
            )

            #  CRITICAL: Broadcast all results NOW before CI watcher blocks
            # Frontend unlocks here — users see everything immediately
            await self._broadcast_with_result(
                "results_ready",
                f" {len(state.get('applied_fixes', []))} fixes committed to branch '{state.get('branch_name')}'. CI/CD monitoring running in background...",
                75,
                state
            )

        except Exception as e:
            logger.exception(f"[{self.run_id}] Committer node failed")
            state["error_message"] = str(e)
            state["status"] = "failed"
            await self._broadcast("error", f"Committer failed: {str(e)}", 0)

        return state

    async def _ci_watcher_node(self, state: WorkflowState) -> WorkflowState:
        """CI Watcher agent node - monitor CI/CD pipeline"""
        logger.info(f"[{self.run_id}] CI Watcher node starting")

        await self._broadcast("watching_ci", "Monitoring CI/CD pipeline in background...", 80)

        try:
            agent_state = AgentState.from_dict(state)

            # Monitor CI/CD — this can take up to 10 mins but frontend is already showing results
            result = await self.ci_watcher.watch(agent_state)

            # Update state
            state["cicd_iterations"] = [
                {
                    "iteration": i.iteration,
                    "status": i.status,
                    "timestamp": i.timestamp,
                    "duration_seconds": i.duration_seconds,
                    "test_failures": i.test_failures
                }
                for i in result.cicd_iterations
            ]
            state["current_iteration"] = result.current_iteration
            state["final_cicd_status"] = result.final_cicd_status
            state["current_stage"] = "ci_watching_complete"

            await self._broadcast(
                "ci_watching_complete",
                f"CI/CD status: {result.final_cicd_status} (iteration {result.current_iteration})",
                85
            )

        except Exception as e:
            logger.exception(f"[{self.run_id}] CI Watcher node failed")
            # Non-critical — don't fail the whole run just because CI watcher errored
            state["final_cicd_status"] = "unknown"
            state["cicd_iterations"] = state.get("cicd_iterations", [])
            await self._broadcast(
                "ci_watching_complete",
                f"CI/CD monitoring failed: {str(e)}",
                85
            )

        return state

    async def _finalize_node(self, state: WorkflowState) -> WorkflowState:
        """Finalize node - create PR and complete"""
        logger.info(f"[{self.run_id}] Finalize node starting")

        await self._broadcast("finalizing", "Creating pull request and finalizing", 90)

        try:
            agent_state = AgentState.from_dict(state)

            # Create PR regardless of CI status (let devs review)
            pr_url = await self.github_service.create_pull_request(
                repo_url=agent_state.repo_url,
                branch_name=agent_state.branch_name,
                title=f"[AI-AGENT] Automated fixes for {agent_state.repo_name}",
                body=self._generate_pr_description(agent_state)
            )
            state["pull_request_url"] = pr_url

            # Update final state
            ci_status = state.get("final_cicd_status", "unknown")
            state["status"] = "completed"
            state["success"] = ci_status == "passed"
            state["completed_at"] = datetime.utcnow().isoformat()
            state["current_stage"] = "completed"

            #  Final broadcast with complete data including cicd results
            await self._broadcast_with_result(
                "completed",
                f"🎉 Agent run complete! CI/CD: {ci_status.upper()}. PR created.",
                100,
                state
            )

        except Exception as e:
            logger.exception(f"[{self.run_id}] Finalize node failed")
            state["error_message"] = str(e)
            state["status"] = "failed"
            await self._broadcast("error", f"Finalize failed: {str(e)}", 0)

        return state

    def _should_continue_or_finish(self, state: WorkflowState) -> str:
        """Decide whether to continue fixing or finish"""

        # If failed, finish
        if state.get("status") == "failed":
            return "finalize"

        # If CI passed, finish
        if state.get("final_cicd_status") == "passed":
            return "finalize"

        # If CI is unknown/timeout, don't keep retrying — just finalize
        if state.get("final_cicd_status") in ("timeout", "unknown"):
            return "finalize"

        # If max iterations reached, finish
        if state.get("current_iteration", 0) >= state.get("max_iterations", 5):
            return "finalize"

        # CI failed and we have retries left — fix more
        return "fix_more"

    async def _clone_repository(self, repo_url: str) -> str:
        """Clone repository to temporary directory"""
        import subprocess

        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(tempfile.gettempdir(), f"rift-{self.run_id}-{repo_name}")

        # Remove if exists
        if os.path.exists(repo_path):
            import shutil
            shutil.rmtree(repo_path)

        # Clone with token auth if available
        if self.github_token:
            # Inject token into URL for auth
            auth_url = repo_url.replace("https://", f"https://{self.github_token}@")
            cmd = f"git clone {auth_url} {repo_path}"
        else:
            cmd = f"git clone {repo_url} {repo_path}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to clone repository: {result.stderr}")

        logger.info(f"Cloned repository to {repo_path}")
        return repo_path

    async def _broadcast(self, stage: str, message: str, progress: int):
        """Broadcast a simple status update via WebSocket"""
        if self.broadcast_callback:
            await self.broadcast_callback(self.run_id, {
                "stage": stage,
                "message": message,
                "progress": progress,
                "result": {}
            })

    async def _broadcast_with_result(self, stage: str, message: str, progress: int, state: dict):
        """
        Broadcast update with full result data attached.
        Used at results_ready and completed stages so frontend
        can render everything without waiting for CI watcher.
        """
        if self.broadcast_callback:
            await self.broadcast_callback(self.run_id, {
                "stage": stage,
                "message": message,
                "progress": progress,
                "result": {
                    # Core fix data
                    "fixes": state.get("fixes", []),
                    "applied_fixes": state.get("applied_fixes", []),
                    "failed_fixes": state.get("failed_fixes", []),

                    # Repository info
                    "file_tree": state.get("file_tree", {}),
                    "repo_name": state.get("repo_name"),
                    "repo_url": state.get("repo_url"),
                    "detected_issues": state.get("detected_issues", []),

                    # Commit info
                    "commit_sha": state.get("commit_sha"),
                    "branch_name": state.get("branch_name"),
                    "total_commits": state.get("total_commits", 0),
                    "pull_request_url": state.get("pull_request_url"),

                    # Team info
                    "team_name": state.get("team_name"),
                    "team_leader_name": state.get("team_leader_name"),

                    # CI/CD data (populated after ci_watcher completes)
                    "cicd_iterations": state.get("cicd_iterations", []),
                    "final_cicd_status": state.get("final_cicd_status", "pending"),
                    "current_iteration": state.get("current_iteration", 0),

                    # Run metadata
                    "status": state.get("status"),
                    "success": state.get("success", False),
                    "started_at": state.get("started_at"),
                    "completed_at": state.get("completed_at"),
                    "error_message": state.get("error_message"),

                    # Score (if your fixer/analyzer produces this)
                    "score": state.get("score"),
                }
            })

    def _generate_pr_description(self, state: AgentState) -> str:
        """Generate PR description"""
        fixes_summary = "\n".join([
            f"- **{fix['file_path']}**: {fix['description']} ({fix['bug_type']})"
            for fix in state.applied_fixes[:10]
        ])

        if len(state.applied_fixes) > 10:
            fixes_summary += f"\n- ... and {len(state.applied_fixes) - 10} more fixes"

        ci_emoji = {
            "passed": "✅",
            "failed": "❌",
            "timeout": "⏱️",
            "unknown": "❓",
            "pending": "🔄"
        }.get(state.final_cicd_status, "❓")

        return f"""# 🤖 AI-AGENT Automated Fixes

This pull request contains automated fixes generated by the RIFT DevOps Agent.

## Summary
- **Total Fixes Applied**: {len(state.applied_fixes)}
- **CI/CD Status**: {ci_emoji} {state.final_cicd_status.upper()}
- **Iterations**: {state.current_iteration}
- **Team**: {state.team_name}

## Fixes Applied
{fixes_summary}

## Details
- Branch: `{state.branch_name}`
- Commit: `{state.commit_sha[:8] if state.commit_sha else 'N/A'}`

---
*Generated by RIFT DevOps Agent*
"""

    async def execute(
        self,
        repo_url: str,
        team_name: str,
        team_leader_name: str,
        branch_name: str,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the full agent workflow

        Args:
            repo_url: GitHub repository URL
            team_name: Team name
            team_leader_name: Team leader name
            branch_name: Branch name to create
            max_iterations: Maximum CI/CD retry iterations

        Returns:
            Dictionary with execution results
        """
        logger.info(f"[{self.run_id}] Starting execution for {repo_url}")

        # Initialize state
        initial_state: WorkflowState = {
            "run_id": self.run_id,
            "repo_url": repo_url,
            "repo_path": None,
            "repo_name": None,
            "branch_name": branch_name,
            "team_name": team_name,
            "team_leader_name": team_leader_name,
            "file_tree": {},
            "test_files": [],
            "detected_issues": [],
            "fixes": [],
            "applied_fixes": [],
            "failed_fixes": [],
            "cicd_iterations": [],
            "current_iteration": 0,
            "max_iterations": max_iterations,
            "final_cicd_status": "pending",
            "commit_sha": None,
            "pull_request_url": None,
            "status": "running",
            "current_stage": "initializing",
            "error_message": None,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "similar_patterns": [],
            "success": False,
            "total_commits": 0,
            "score": None,
        }

        # Execute workflow
        config = {"configurable": {"thread_id": self.run_id}}
        result = await self.workflow.ainvoke(initial_state, config)

        # Convert to result dictionary
        return {
            "success": result.get("success", False),
            "run_id": self.run_id,
            "total_failures": len(result.get("detected_issues", [])),
            "total_fixes": len(result.get("applied_fixes", [])),
            "total_commits": result.get("total_commits", 0),
            "cicd_iterations": result.get("current_iteration", 0),
            "cicd_status": result.get("final_cicd_status"),
            "fixes": result.get("applied_fixes", []),
            "file_tree": result.get("file_tree", {}),
            "commit_sha": result.get("commit_sha"),
            "branch_name": result.get("branch_name"),
            "pull_request_url": result.get("pull_request_url"),
            "error_message": result.get("error_message"),
            "score": result.get("score"),
            "duration_seconds": None  # Calculated by caller
        }