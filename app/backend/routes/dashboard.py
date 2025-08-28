from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.backend.database import get_db
from app.backend.models.database_models import (
    Project, Contact, Company, Signal, Task, UploadBatch,
    ContactGrade, TaskStatus, SignalType
)
from app.backend.models.schemas import (
    ProjectDashboard,
    ContactStats,
    APIResponse
)

router = APIRouter(prefix="/dashboard")

@router.get("/project/{project_id}")
async def get_project_dashboard(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard data for a project"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get contact statistics
    contact_stats_result = await db.execute(
        select(
            func.count(Contact.id).label('total_contacts'),
            func.count(Contact.contact_grade).label('graded_contacts'),
            func.count(Contact.prospect_score).label('scored_contacts'),
            func.sum(
                func.case(
                    (Contact.enrichment_status == 'completed', 1),
                    else_=0
                )
            ).label('enriched_contacts'),
            func.avg(Contact.prospect_score).label('avg_prospect_score'),
            func.avg(Contact.data_quality_score).label('avg_data_quality'),
        ).where(Contact.project_id == project_id)
    )
    stats = contact_stats_result.first()
    
    # Get grade distribution
    grade_result = await db.execute(
        select(Contact.contact_grade, func.count(Contact.id))
        .where(Contact.project_id == project_id)
        .where(Contact.contact_grade.is_not(None))
        .group_by(Contact.contact_grade)
    )
    grade_distribution = {str(grade): count for grade, count in grade_result.all()}
    
    # Get recent signals for companies in this project
    recent_signals_result = await db.execute(
        select(Signal)
        .options(selectinload(Signal.company))
        .join(Contact, Signal.company_id == Contact.company_id)
        .where(Contact.project_id == project_id)
        .where(Signal.signal_date >= datetime.now() - timedelta(days=30))
        .order_by(Signal.relevance_score.desc(), Signal.signal_date.desc())
        .limit(10)
    )
    recent_signals = recent_signals_result.scalars().all()
    
    # Get pending tasks
    pending_tasks_result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.contact).selectinload(Contact.company)
        )
        .join(Contact, Task.contact_id == Contact.id)
        .where(Contact.project_id == project_id)
        .where(Task.status.in_(['pending', 'in_progress']))
        .order_by(Task.priority.desc(), Task.recommended_date.asc().nulls_last())
        .limit(10)
    )
    pending_tasks = pending_tasks_result.scalars().all()
    
    # Get top prospects
    top_prospects_result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.company))
        .where(Contact.project_id == project_id)
        .where(Contact.prospect_score.is_not(None))
        .order_by(Contact.prospect_score.desc())
        .limit(10)
    )
    top_prospects = top_prospects_result.scalars().all()
    
    # Build contact stats
    contact_stats = ContactStats(
        total_contacts=stats.total_contacts or 0,
        graded_contacts=stats.graded_contacts or 0,
        scored_contacts=stats.scored_contacts or 0,
        enriched_contacts=stats.enriched_contacts or 0,
        grade_distribution=grade_distribution,
        average_prospect_score=float(stats.avg_prospect_score) if stats.avg_prospect_score else None,
        average_data_quality=float(stats.avg_data_quality) if stats.avg_data_quality else None
    )
    
    return {
        "project": project,
        "contact_stats": contact_stats,
        "recent_signals": recent_signals,
        "pending_tasks": pending_tasks,
        "top_prospects": top_prospects
    }

@router.get("/overview")
async def get_dashboard_overview(
    project_id: Optional[int] = Query(None),
    days_back: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get high-level dashboard overview"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Base conditions
    conditions = []
    if project_id:
        conditions.append(Contact.project_id == project_id)
    
    # Contact metrics
    contact_query = select(
        func.count(Contact.id).label('total_contacts'),
        func.avg(Contact.prospect_score).label('avg_prospect_score'),
        func.sum(
            func.case(
                (Contact.contact_grade == ContactGrade.A, 1),
                else_=0
            )
        ).label('a_grade_contacts'),
        func.sum(
            func.case(
                (Contact.enrichment_status == 'completed', 1),
                else_=0
            )
        ).label('enriched_contacts')
    )
    
    if conditions:
        contact_query = contact_query.where(and_(*conditions))
    
    contact_result = await db.execute(contact_query)
    contact_metrics = contact_result.first()
    
    # Signal metrics
    signal_conditions = [Signal.signal_date >= cutoff_date]
    if project_id:
        signal_conditions.extend([
            Signal.company_id == Contact.company_id,
            Contact.project_id == project_id
        ])
        signal_query = select(
            func.count(Signal.id).label('total_signals'),
            func.avg(Signal.relevance_score).label('avg_relevance'),
            func.sum(
                func.case(
                    (Signal.impact_score >= 80, 1),
                    else_=0
                )
            ).label('high_impact_signals')
        ).select_from(Signal.join(Contact, Signal.company_id == Contact.company_id))
    else:
        signal_query = select(
            func.count(Signal.id).label('total_signals'),
            func.avg(Signal.relevance_score).label('avg_relevance'),
            func.sum(
                func.case(
                    (Signal.impact_score >= 80, 1),
                    else_=0
                )
            ).label('high_impact_signals')
        )
    
    signal_query = signal_query.where(and_(*signal_conditions))
    signal_result = await db.execute(signal_query)
    signal_metrics = signal_result.first()
    
    # Task metrics
    task_conditions = []
    if project_id:
        task_conditions.extend([
            Task.contact_id == Contact.id,
            Contact.project_id == project_id
        ])
        task_query = select(
            func.count(Task.id).label('total_tasks'),
            func.sum(
                func.case(
                    (Task.status == TaskStatus.PENDING, 1),
                    else_=0
                )
            ).label('pending_tasks'),
            func.sum(
                func.case(
                    (and_(Task.due_date < datetime.now(), Task.status.in_(['pending', 'in_progress'])), 1),
                    else_=0
                )
            ).label('overdue_tasks')
        ).select_from(Task.join(Contact, Task.contact_id == Contact.id))
    else:
        task_query = select(
            func.count(Task.id).label('total_tasks'),
            func.sum(
                func.case(
                    (Task.status == TaskStatus.PENDING, 1),
                    else_=0
                )
            ).label('pending_tasks'),
            func.sum(
                func.case(
                    (and_(Task.due_date < datetime.now(), Task.status.in_(['pending', 'in_progress'])), 1),
                    else_=0
                )
            ).label('overdue_tasks')
        )
    
    if task_conditions:
        task_query = task_query.where(and_(*task_conditions))
    
    task_result = await db.execute(task_query)
    task_metrics = task_result.first()
    
    return {
        "period_days": days_back,
        "project_id": project_id,
        "contacts": {
            "total": contact_metrics.total_contacts or 0,
            "average_prospect_score": float(contact_metrics.avg_prospect_score) if contact_metrics.avg_prospect_score else 0,
            "a_grade_count": contact_metrics.a_grade_contacts or 0,
            "enriched_count": contact_metrics.enriched_contacts or 0
        },
        "signals": {
            "total_recent": signal_metrics.total_signals or 0,
            "average_relevance": float(signal_metrics.avg_relevance) if signal_metrics.avg_relevance else 0,
            "high_impact_count": signal_metrics.high_impact_signals or 0
        },
        "tasks": {
            "total": task_metrics.total_tasks or 0,
            "pending": task_metrics.pending_tasks or 0,
            "overdue": task_metrics.overdue_tasks or 0
        }
    }

@router.get("/activity/recent")
async def get_recent_activity(
    project_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity across the platform"""
    activities = []
    
    # Recent uploads
    upload_query = select(UploadBatch).order_by(UploadBatch.created_at.desc()).limit(5)
    if project_id:
        upload_query = upload_query.where(UploadBatch.project_id == project_id)
    
    upload_result = await db.execute(upload_query)
    uploads = upload_result.scalars().all()
    
    for upload in uploads:
        activities.append({
            "type": "upload",
            "timestamp": upload.created_at,
            "description": f"Uploaded {upload.filename} with {upload.total_records} contacts",
            "data": {"batch_id": upload.id, "filename": upload.filename}
        })
    
    # Recent signals
    signal_query = select(Signal).options(selectinload(Signal.company)).order_by(Signal.detected_at.desc()).limit(5)
    if project_id:
        signal_query = signal_query.join(Contact, Signal.company_id == Contact.company_id).where(Contact.project_id == project_id)
    
    signal_result = await db.execute(signal_query)
    signals = signal_result.scalars().all()
    
    for signal in signals:
        activities.append({
            "type": "signal",
            "timestamp": signal.detected_at,
            "description": f"New {signal.signal_type.value} signal for {signal.company.name if signal.company else 'Unknown Company'}",
            "data": {"signal_id": signal.id, "company": signal.company.name if signal.company else None}
        })
    
    # Recent task completions
    task_query = select(Task).options(
        selectinload(Task.contact)
    ).where(Task.status == TaskStatus.COMPLETED).order_by(Task.completed_date.desc()).limit(5)
    
    if project_id:
        task_query = task_query.join(Contact, Task.contact_id == Contact.id).where(Contact.project_id == project_id)
    
    task_result = await db.execute(task_query)
    tasks = task_result.scalars().all()
    
    for task in tasks:
        activities.append({
            "type": "task_completed",
            "timestamp": task.completed_date,
            "description": f"Completed {task.channel.value} task for {task.contact.full_name}",
            "data": {"task_id": task.id, "contact": task.contact.full_name}
        })
    
    # Sort all activities by timestamp and limit
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]

@router.get("/metrics/trends")
async def get_trend_metrics(
    project_id: Optional[int] = Query(None),
    days_back: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db)
):
    """Get trend metrics over time"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Daily contact additions
    contact_conditions = [Contact.created_at >= cutoff_date]
    if project_id:
        contact_conditions.append(Contact.project_id == project_id)
    
    contact_trend_result = await db.execute(
        select(
            func.date(Contact.created_at).label('date'),
            func.count(Contact.id).label('count')
        )
        .where(and_(*contact_conditions))
        .group_by(func.date(Contact.created_at))
        .order_by(func.date(Contact.created_at))
    )
    contact_trends = [{"date": str(date), "contacts_added": count} for date, count in contact_trend_result.all()]
    
    # Daily signal detections
    signal_conditions = [Signal.detected_at >= cutoff_date]
    if project_id:
        signal_conditions.extend([
            Signal.company_id == Contact.company_id,
            Contact.project_id == project_id
        ])
        signal_trend_query = select(
            func.date(Signal.detected_at).label('date'),
            func.count(Signal.id).label('count')
        ).select_from(Signal.join(Contact, Signal.company_id == Contact.company_id))
    else:
        signal_trend_query = select(
            func.date(Signal.detected_at).label('date'),
            func.count(Signal.id).label('count')
        )
    
    signal_trend_result = await db.execute(
        signal_trend_query
        .where(and_(*signal_conditions))
        .group_by(func.date(Signal.detected_at))
        .order_by(func.date(Signal.detected_at))
    )
    signal_trends = [{"date": str(date), "signals_detected": count} for date, count in signal_trend_result.all()]
    
    # Daily task completions
    task_conditions = [
        Task.completed_date >= cutoff_date,
        Task.status == TaskStatus.COMPLETED
    ]
    if project_id:
        task_conditions.extend([
            Task.contact_id == Contact.id,
            Contact.project_id == project_id
        ])
        task_trend_query = select(
            func.date(Task.completed_date).label('date'),
            func.count(Task.id).label('count')
        ).select_from(Task.join(Contact, Task.contact_id == Contact.id))
    else:
        task_trend_query = select(
            func.date(Task.completed_date).label('date'),
            func.count(Task.id).label('count')
        )
    
    task_trend_result = await db.execute(
        task_trend_query
        .where(and_(*task_conditions))
        .group_by(func.date(Task.completed_date))
        .order_by(func.date(Task.completed_date))
    )
    task_trends = [{"date": str(date), "tasks_completed": count} for date, count in task_trend_result.all()]
    
    return {
        "days_back": days_back,
        "contact_trends": contact_trends,
        "signal_trends": signal_trends,
        "task_trends": task_trends
    }

@router.get("/leaderboard/prospects")
async def get_prospect_leaderboard(
    project_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard of top prospects"""
    query = select(Contact).options(selectinload(Contact.company))
    
    conditions = [Contact.prospect_score.is_not(None)]
    if project_id:
        conditions.append(Contact.project_id == project_id)
    
    query = query.where(and_(*conditions)).order_by(Contact.prospect_score.desc()).limit(limit)
    
    result = await db.execute(query)
    prospects = result.scalars().all()
    
    return [
        {
            "rank": i + 1,
            "contact": contact,
            "prospect_score": contact.prospect_score,
            "contact_grade": contact.contact_grade,
            "company": contact.company
        }
        for i, contact in enumerate(prospects)
    ]