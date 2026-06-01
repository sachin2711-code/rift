"""
Learner Agent
Searches memory for similar bug patterns and learns from past fixes
"""

from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AgentState
from services.memory_service import MemoryService
from utils.logger import get_logger

logger = get_logger(__name__)


class LearnerAgent:
    """
    Agent responsible for:
    1. Searching vector memory for similar bug patterns
    2. Retrieving successful fixes from past runs
    3. Building context for the fixer agent
    4. Learning from new fixes to improve future performance
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI, memory_service: MemoryService):
        self.llm = llm
        self.memory_service = memory_service
    
    async def search_patterns(self, state: AgentState) -> AgentState:
        """
        Search memory for similar patterns to current issues
        
        Args:
            state: Current agent state with detected issues
            
        Returns:
            Updated state with similar patterns
        """
        logger.info(f"[{state.run_id}] Learner searching for similar patterns")
        
        similar_patterns = []
        
        for issue in state.detected_issues:
            bug_type = issue.get('bug_type', 'LOGIC')
            message = issue.get('message', '')
            file_path = issue.get('file_path', '')
            
            # Search for similar patterns
            patterns = await self.memory_service.search_similar_patterns(
                bug_type=bug_type,
                query=message,
                file_extension=self._get_file_extension(file_path),
                limit=3
            )
            
            for pattern in patterns:
                if pattern.success_rate > 0.7:  # Only high-success patterns
                    similar_patterns.append(pattern)
        
        # Remove duplicates
        seen_ids = set()
        unique_patterns = []
        for pattern in similar_patterns:
            if pattern.id not in seen_ids:
                seen_ids.add(pattern.id)
                unique_patterns.append(pattern)
        
        state.similar_patterns = unique_patterns[:10]  # Limit to top 10
        
        logger.info(f"[{state.run_id}] Learner found {len(state.similar_patterns)} similar patterns")
        
        return state
    
    async def learn_from_fix(
        self,
        bug_type: str,
        pattern: str,
        fix_template: str,
        file_path: str,
        success: bool
    ) -> None:
        """
        Learn from a new fix
        
        Args:
            bug_type: Type of bug
            pattern: The bug pattern
            fix_template: The fix that was applied
            file_path: File where fix was applied
            success: Whether the fix was successful
        """
        await self.memory_store.store_pattern(
            bug_type=bug_type,
            pattern=pattern,
            fix_template=fix_template,
            file_extension=self._get_file_extension(file_path),
            success=success
        )
        
        logger.info(f"Learner stored pattern for {bug_type} (success={success})")
    
    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension from path"""
        if '.' in file_path:
            return file_path.split('.')[-1].lower()
        return ""