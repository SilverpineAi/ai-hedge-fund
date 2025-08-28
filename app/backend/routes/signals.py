from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.backend.database import get_db
from app.backend.models.database_models import Signal, Company
from app.backend.models.schemas import (
    Signal as SignalSchema,
    SignalCreate,
    APIResponse,
    SignalTypeEnum
)

router = APIRouter(prefix="/signals")

@router.post("/", response_model=SignalSchema, status_code=status.HTTP_201_CREATED)
async def create_signal(
    signal: SignalCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new signal"""
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == signal.company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    db_signal = Signal(**signal.model_dump())
    db.add(db_signal)
    await db.commit()
    await db.refresh(db_signal)
    return db_signal

@router.get("/", response_model=List[SignalSchema])
async def get_signals(
    signal_type: Optional[SignalTypeEnum] = Query(None),
    company_id: Optional[int] = Query(None),
    min_relevance_score: Optional[float] = Query(None, ge=0, le=100),
    min_impact_score: Optional[float] = Query(None, ge=0, le=100),
    days_back: Optional[int] = Query(30, ge=1, le=365),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get signals with filtering and search"""
    query = select(Signal).options(selectinload(Signal.company))
    
    # Apply filters
    conditions = []
    
    if signal_type:
        conditions.append(Signal.signal_type == signal_type)
    
    if company_id:
        conditions.append(Signal.company_id == company_id)
    
    if min_relevance_score is not None:
        conditions.append(Signal.relevance_score >= min_relevance_score)
    
    if min_impact_score is not None:
        conditions.append(Signal.impact_score >= min_impact_score)
    
    # Filter by date range
    if days_back:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        conditions.append(Signal.signal_date >= cutoff_date)
    
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Signal.title.ilike(search_term),
                Signal.description.ilike(search_term),
                Signal.source.ilike(search_term)
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(
        Signal.relevance_score.desc(),
        Signal.signal_date.desc()
    )
    
    result = await db.execute(query)
    signals = result.scalars().all()
    return signals

@router.get("/{signal_id}", response_model=SignalSchema)
async def get_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific signal by ID"""
    result = await db.execute(
        select(Signal)
        .options(selectinload(Signal.company))
        .where(Signal.id == signal_id)
    )
    signal = result.scalar_one_or_none()
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    return signal

@router.delete("/{signal_id}", response_model=APIResponse)
async def delete_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a signal"""
    result = await db.execute(
        select(Signal).where(Signal.id == signal_id)
    )
    db_signal = result.scalar_one_or_none()
    
    if not db_signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found"
        )
    
    await db.delete(db_signal)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Signal deleted successfully"
    )

@router.get("/trending/types")
async def get_trending_signal_types(
    days_back: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get trending signal types in the last N days"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    result = await db.execute(
        select(Signal.signal_type, func.count(Signal.id).label('count'))
        .where(Signal.signal_date >= cutoff_date)
        .group_by(Signal.signal_type)
        .order_by(func.count(Signal.id).desc())
        .limit(limit)
    )
    
    trending_types = result.all()
    return [{"signal_type": signal_type, "count": count} for signal_type, count in trending_types]

@router.get("/stats/company/{company_id}")
async def get_company_signal_stats(
    company_id: int,
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get signal statistics for a specific company"""
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Get signal counts by type
    type_stats_result = await db.execute(
        select(Signal.signal_type, func.count(Signal.id))
        .where(
            and_(
                Signal.company_id == company_id,
                Signal.signal_date >= cutoff_date
            )
        )
        .group_by(Signal.signal_type)
    )
    type_stats = dict(type_stats_result.all())
    
    # Get overall stats
    overall_stats_result = await db.execute(
        select(
            func.count(Signal.id).label('total_signals'),
            func.avg(Signal.relevance_score).label('avg_relevance'),
            func.avg(Signal.impact_score).label('avg_impact'),
            func.avg(Signal.timing_score).label('avg_timing')
        )
        .where(
            and_(
                Signal.company_id == company_id,
                Signal.signal_date >= cutoff_date
            )
        )
    )
    overall_stats = overall_stats_result.first()
    
    return {
        "company_id": company_id,
        "days_back": days_back,
        "total_signals": overall_stats.total_signals or 0,
        "average_relevance_score": float(overall_stats.avg_relevance) if overall_stats.avg_relevance else 0,
        "average_impact_score": float(overall_stats.avg_impact) if overall_stats.avg_impact else 0,
        "average_timing_score": float(overall_stats.avg_timing) if overall_stats.avg_timing else 0,
        "signals_by_type": type_stats
    }

@router.get("/recent/high-impact")
async def get_recent_high_impact_signals(
    days_back: int = Query(7, ge=1, le=30),
    min_impact_score: float = Query(75, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get recent high-impact signals"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    result = await db.execute(
        select(Signal)
        .options(selectinload(Signal.company))
        .where(
            and_(
                Signal.signal_date >= cutoff_date,
                Signal.impact_score >= min_impact_score
            )
        )
        .order_by(Signal.impact_score.desc(), Signal.signal_date.desc())
        .limit(limit)
    )
    
    signals = result.scalars().all()
    return signals

@router.post("/detect/company/{company_id}", response_model=APIResponse)
async def detect_signals_for_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger signal detection for a specific company"""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # TODO: Trigger background signal detection job
    # This would typically:
    # - Search news APIs for company mentions
    # - Check for funding announcements
    # - Monitor leadership changes
    # - Track product launches
    # - Analyze hiring patterns
    
    return APIResponse(
        success=True,
        message="Signal detection queued for company"
    )

@router.get("/dashboard/summary")
async def get_signals_dashboard_summary(
    days_back: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get a summary of recent signals for dashboard"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Total signals
    total_result = await db.execute(
        select(func.count(Signal.id))
        .where(Signal.signal_date >= cutoff_date)
    )
    total_signals = total_result.scalar()
    
    # High-impact signals (score >= 80)
    high_impact_result = await db.execute(
        select(func.count(Signal.id))
        .where(
            and_(
                Signal.signal_date >= cutoff_date,
                Signal.impact_score >= 80
            )
        )
    )
    high_impact_signals = high_impact_result.scalar()
    
    # Signals by type
    type_result = await db.execute(
        select(Signal.signal_type, func.count(Signal.id))
        .where(Signal.signal_date >= cutoff_date)
        .group_by(Signal.signal_type)
        .order_by(func.count(Signal.id).desc())
    )
    signals_by_type = dict(type_result.all())
    
    # Companies with most signals
    company_result = await db.execute(
        select(Company.name, func.count(Signal.id))
        .join(Signal, Signal.company_id == Company.id)
        .where(Signal.signal_date >= cutoff_date)
        .group_by(Company.id, Company.name)
        .order_by(func.count(Signal.id).desc())
        .limit(5)
    )
    top_companies = [{"company": name, "signal_count": count} for name, count in company_result.all()]
    
    return {
        "days_back": days_back,
        "total_signals": total_signals or 0,
        "high_impact_signals": high_impact_signals or 0,
        "signals_by_type": signals_by_type,
        "top_companies": top_companies
    }