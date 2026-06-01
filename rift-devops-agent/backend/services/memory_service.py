"""
Memory Service
Vector database for storing and retrieving bug patterns
Uses ChromaDB for local storage
"""

import hashlib
import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BugPattern:
    """Bug pattern data class"""
    id: str
    bug_type: str
    pattern: str
    fix_template: str
    occurrence_count: int
    success_count: int
    success_rate: float
    file_extensions: List[str]
    example_files: List[str]
    created_at: str
    last_seen_at: str


class MemoryService:
    """
    Service for storing and retrieving bug patterns using vector database
    """
    
    def __init__(self):
        self.db_path = settings.CHROMA_DB_PATH
        self.embedding_model = None
        self.client = None
        self.collection = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.db_path
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="bug_patterns",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Memory service initialized")
            
        except Exception as e:
            logger.exception(f"Failed to initialize memory service: {e}")
            # Create in-memory fallback
            self.client = None
            self.collection = None
    
    async def health_check(self) -> str:
        """Check if memory service is healthy"""
        if self.collection is not None:
            return "healthy"
        return "unhealthy"
    
    async def store_pattern(
        self,
        bug_type: str,
        pattern: str,
        fix_template: str,
        file_extension: str = "",
        success: bool = True
    ) -> str:
        """
        Store a bug pattern
        
        Args:
            bug_type: Type of bug
            pattern: The bug pattern description
            fix_template: The fix template
            file_extension: File extension where bug was found
            success: Whether the fix was successful
            
        Returns:
            Pattern ID
        """
        if not self.collection:
            logger.warning("Memory service not initialized, skipping pattern storage")
            return ""
        
        try:
            # Generate ID from pattern
            pattern_id = str(uuid.uuid4())
            
            # Create embedding
            embedding_text = f"{bug_type}: {pattern}"
            embedding = self.embedding_model.encode(embedding_text).tolist()
            
            # Store in ChromaDB
            self.collection.add(
                ids=[pattern_id],
                embeddings=[embedding],
                metadatas=[{
                    "bug_type": bug_type,
                    "pattern": pattern,
                    "fix_template": fix_template,
                    "file_extension": file_extension,
                    "occurrence_count": 1,
                    "success_count": 1 if success else 0,
                    "success_rate": 1.0 if success else 0.0
                }],
                documents=[pattern]
            )
            
            logger.info(f"Stored pattern {pattern_id} for {bug_type}")
            return pattern_id
            
        except Exception as e:
            logger.exception(f"Failed to store pattern: {e}")
            return ""
    
    async def search_similar_patterns(
        self,
        bug_type: str,
        query: str,
        file_extension: str = "",
        limit: int = 5
    ) -> List[BugPattern]:
        """
        Search for similar bug patterns
        
        Args:
            bug_type: Type of bug to search for
            query: Query text
            file_extension: Optional file extension filter
            limit: Maximum number of results
            
        Returns:
            List of matching bug patterns
        """
        if not self.collection:
            return []
        
        try:
            # Create embedding for query
            embedding_text = f"{bug_type}: {query}"
            embedding = self.embedding_model.encode(embedding_text).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit,
                where={"bug_type": bug_type} if bug_type else None
            )
            
            patterns = []
            
            if results and results['ids']:
                for i, pattern_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    pattern = BugPattern(
                        id=pattern_id,
                        bug_type=metadata.get('bug_type', 'UNKNOWN'),
                        pattern=metadata.get('pattern', ''),
                        fix_template=metadata.get('fix_template', ''),
                        occurrence_count=metadata.get('occurrence_count', 1),
                        success_count=metadata.get('success_count', 0),
                        success_rate=metadata.get('success_rate', 0.0),
                        file_extensions=[metadata.get('file_extension', '')],
                        example_files=[],
                        created_at=metadata.get('created_at', ''),
                        last_seen_at=metadata.get('last_seen_at', '')
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.exception(f"Failed to search patterns: {e}")
            return []
    
    async def update_pattern_success(self, pattern_id: str, success: bool) -> None:
        """Update pattern success rate"""
        if not self.collection:
            return
        
        try:
            # Get current metadata
            result = self.collection.get(ids=[pattern_id])
            
            if result and result['metadatas']:
                metadata = result['metadatas'][0]
                
                occurrence_count = metadata.get('occurrence_count', 0) + 1
                success_count = metadata.get('success_count', 0) + (1 if success else 0)
                success_rate = success_count / occurrence_count
                
                # Update
                self.collection.update(
                    ids=[pattern_id],
                    metadatas=[{
                        **metadata,
                        "occurrence_count": occurrence_count,
                        "success_count": success_count,
                        "success_rate": success_rate
                    }]
                )
                
        except Exception as e:
            logger.exception(f"Failed to update pattern: {e}")
    
    async def store_run_patterns(self, run_id: str, run_data: Dict[str, Any]) -> None:
        """Store patterns from a completed run"""
        fixes = run_data.get('fixes', [])
        
        for fix in fixes:
            bug_type = fix.get('bug_type', 'LOGIC')
            description = fix.get('description', '')
            after_code = fix.get('after_code', '')
            file_path = fix.get('file_path', '')
            status = fix.get('status', '')
            
            file_extension = ''
            if '.' in file_path:
                file_extension = file_path.split('.')[-1]
            
            await self.store_pattern(
                bug_type=bug_type,
                pattern=description,
                fix_template=after_code,
                file_extension=file_extension,
                success=(status == 'verified')
            )
        
        logger.info(f"Stored {len(fixes)} patterns from run {run_id}")
    
    async def get_bug_patterns(
        self,
        bug_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get bug patterns, optionally filtered by type"""
        if not self.collection:
            return []
        
        try:
            where_filter = {"bug_type": bug_type} if bug_type else None
            
            results = self.collection.get(
                where=where_filter,
                limit=limit
            )
            
            patterns = []
            
            if results and results['ids']:
                for i, pattern_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    
                    patterns.append({
                        "id": pattern_id,
                        "bug_type": metadata.get('bug_type', 'UNKNOWN'),
                        "pattern": metadata.get('pattern', ''),
                        "fix_template": metadata.get('fix_template', ''),
                        "occurrence_count": metadata.get('occurrence_count', 1),
                        "success_count": metadata.get('success_count', 0),
                        "success_rate": metadata.get('success_rate', 0.0),
                        "file_extensions": [metadata.get('file_extension', '')]
                    })
            
            return patterns
            
        except Exception as e:
            logger.exception(f"Failed to get patterns: {e}")
            return []
    
    async def get_repository_tree(self, run_id: str) -> Dict[str, Any]:
        """Get repository file tree (placeholder - would be stored during analysis)"""
        return {
            "name": "repository",
            "type": "directory",
            "children": []
        }
    
    async def annotate_file_with_fixes(
        self,
        tree: Dict[str, Any],
        file_path: str,
        fix: Dict[str, Any]
    ) -> None:
        """Annotate file tree with fix information"""
        parts = file_path.split('/')
        
        current = tree
        for part in parts:
            if current.get('type') == 'directory' and 'children' in current:
                for child in current['children']:
                    if child['name'] == part:
                        current = child
                        break
        
        # Annotate the file
        if current.get('type') == 'file':
            current['has_errors'] = True
            current['error_count'] = current.get('error_count', 0) + 1
            if 'fixes' not in current:
                current['fixes'] = []
            current['fixes'].append(fix)
    
    async def generate_bug_heatmap(self, fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate bug heatmap data"""
        heatmap = {}
        
        for fix in fixes:
            file_path = fix.get('file_path', '')
            
            # Get directory
            directory = '/'.join(file_path.split('/')[:-1]) or 'root'
            
            if directory not in heatmap:
                heatmap[directory] = {
                    "path": directory,
                    "error_count": 0,
                    "fix_count": 0,
                    "files": set()
                }
            
            heatmap[directory]["error_count"] += 1
            heatmap[directory]["files"].add(file_path)
            
            if fix.get('status') == 'verified':
                heatmap[directory]["fix_count"] += 1
        
        # Convert to list and calculate intensity
        result = []
        max_errors = max((h["error_count"] for h in heatmap.values()), default=1)
        
        for directory, data in heatmap.items():
            result.append({
                "path": directory,
                "error_count": data["error_count"],
                "fix_count": data["fix_count"],
                "file_count": len(data["files"]),
                "intensity": data["error_count"] / max_errors
            })
        
        # Sort by error count
        result.sort(key=lambda x: x["error_count"], reverse=True)
        
        return result
