"""
Database configuration and models
"""

from datetime import datetime
from typing import AsyncGenerator, List, Optional

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, 
    Text, JSON, create_engine, select, desc
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

Base = declarative_base()


class RunModel(Base):
    """Database model for agent runs"""
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)
    repository_url = Column(String, nullable=False)
    team_name = Column(String, nullable=False)
    team_leader_name = Column(String, nullable=False)
    branch_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    total_failures = Column(Integer, default=0)
    total_fixes = Column(Integer, default=0)
    cicd_iterations = Column(Integer, default=0)
    final_cicd_status = Column(String, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # JSON data
    fixes = Column(JSON, default=list)
    score = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    pull_request_url = Column(String, nullable=True)
    commit_sha = Column(String, nullable=True)
    
    # Metadata
    metadata_json = Column(JSON, default=dict)


class BugPatternModel(Base):
    """Database model for learned bug patterns"""
    __tablename__ = "bug_patterns"
    
    id = Column(String, primary_key=True)
    bug_type = Column(String, nullable=False, index=True)
    pattern = Column(Text, nullable=False)
    fix_template = Column(Text, nullable=False)
    
    # Statistics
    occurrence_count = Column(Integer, default=1)
    success_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Context
    file_extensions = Column(JSON, default=list)
    example_files = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    
    # Vector embedding (stored as JSON for simplicity)
    embedding = Column(JSON, nullable=True)


class RepositoryCacheModel(Base):
    """Cache for repository analysis"""
    __tablename__ = "repository_cache"
    
    id = Column(String, primary_key=True)
    repo_url = Column(String, nullable=False, index=True)
    repo_hash = Column(String, nullable=False)
    
    # Analysis results
    file_tree = Column(JSON, default=dict)
    test_files = Column(JSON, default=list)
    dependencies = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=settings.DEBUG
)

# Create session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def save_run(session: AsyncSession, run_data: dict) -> RunModel:
    """Save run data to database"""
    run = RunModel(
        id=run_data.get("run_id"),
        repository_url=run_data.get("repository_url"),
        team_name=run_data.get("team_name"),
        team_leader_name=run_data.get("team_leader_name"),
        branch_name=run_data.get("branch_name"),
        status=run_data.get("status"),
        created_at=datetime.fromisoformat(run_data.get("created_at")) if run_data.get("created_at") else datetime.utcnow(),
        started_at=datetime.fromisoformat(run_data.get("started_at")) if run_data.get("started_at") else None,
        completed_at=datetime.fromisoformat(run_data.get("completed_at")) if run_data.get("completed_at") else None,
        total_failures=run_data.get("total_failures", 0),
        total_fixes=run_data.get("total_fixes", 0),
        cicd_iterations=run_data.get("cicd_iterations", 0),
        final_cicd_status=run_data.get("final_cicd_status"),
        duration_seconds=run_data.get("duration_seconds"),
        fixes=run_data.get("fixes", []),
        score=run_data.get("score"),
        error_message=run_data.get("error_message"),
        pull_request_url=run_data.get("pull_request_url"),
        commit_sha=run_data.get("commit_sha"),
        metadata_json=run_data.get("metadata", {})
    )
    
    session.add(run)
    await session.commit()
    return run


async def get_run_by_id(session: AsyncSession, run_id: str) -> Optional[RunModel]:
    """Get run by ID"""
    result = await session.execute(
        select(RunModel).where(RunModel.id == run_id)
    )
    return result.scalar_one_or_none()


async def list_runs(
    session: AsyncSession,
    limit: int = 10,
    offset: int = 0
) -> List[RunModel]:
    """List runs with pagination"""
    result = await session.execute(
        select(RunModel)
        .order_by(desc(RunModel.created_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def save_bug_pattern(session: AsyncSession, pattern_data: dict) -> BugPatternModel:
    """Save bug pattern to database"""
    pattern = BugPatternModel(
        id=pattern_data.get("id"),
        bug_type=pattern_data.get("bug_type"),
        pattern=pattern_data.get("pattern"),
        fix_template=pattern_data.get("fix_template"),
        occurrence_count=pattern_data.get("occurrence_count", 1),
        success_count=pattern_data.get("success_count", 0),
        success_rate=pattern_data.get("success_rate", 0.0),
        file_extensions=pattern_data.get("file_extensions", []),
        example_files=pattern_data.get("example_files", []),
        embedding=pattern_data.get("embedding")
    )
    
    session.add(pattern)
    await session.commit()
    return pattern


async def get_bug_patterns(
    session: AsyncSession,
    bug_type: Optional[str] = None,
    limit: int = 20
) -> List[BugPatternModel]:
    """Get bug patterns, optionally filtered by type"""
    query = select(BugPatternModel)
    
    if bug_type:
        query = query.where(BugPatternModel.bug_type == bug_type)
    
    query = query.order_by(desc(BugPatternModel.success_rate)).limit(limit)
    
    result = await session.execute(query)
    return result.scalars().all()
