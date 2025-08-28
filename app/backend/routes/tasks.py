from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.backend.database import get_db
from app.backend.models.database_models import Task, Contact, Company
from app.backend.models.schemas import (
    Task as TaskSchema,
    TaskCreate,
    TaskUpdate,
    APIResponse,
    TaskStatusEnum,
    TaskChannelEnum
)

router = APIRouter(prefix="/tasks")

@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    # Verify contact exists
    result = await db.execute(select(Contact).where(Contact.id == task.contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    db_task = Task(**task.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    contact_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    status: Optional[TaskStatusEnum] = Query(None),
    channel: Optional[TaskChannelEnum] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=5),
    overdue_only: Optional[bool] = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get tasks with filtering"""
    query = select(Task).options(
        selectinload(Task.contact).selectinload(Contact.company)
    )
    
    # Apply filters
    conditions = []
    
    if contact_id:
        conditions.append(Task.contact_id == contact_id)
    
    if project_id:
        # Join with contacts to filter by project
        query = query.join(Contact, Task.contact_id == Contact.id)
        conditions.append(Contact.project_id == project_id)
    
    if status:
        conditions.append(Task.status == status)
    
    if channel:
        conditions.append(Task.channel == channel)
    
    if priority:
        conditions.append(Task.priority == priority)
    
    if overdue_only:
        now = datetime.now()
        conditions.append(
            and_(
                Task.due_date < now,
                Task.status.in_([TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS])
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(
        Task.priority.desc(),
        Task.recommended_date.asc().nulls_last(),
        Task.created_at.desc()
    )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task by ID"""
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.contact).selectinload(Contact.company)
        )
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Handle status change to completed
    if update_data.get('status') == TaskStatusEnum.COMPLETED and db_task.status != TaskStatusEnum.COMPLETED:
        update_data['completed_date'] = datetime.now()
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a task"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(db_task)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Task deleted successfully"
    )

@router.post("/{task_id}/complete", response_model=TaskSchema)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark a task as completed"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db_task.status = TaskStatusEnum.COMPLETED
    db_task.completed_date = datetime.now()
    
    await db.commit()
    await db.refresh(db_task)
    return db_task

@router.post("/contact/{contact_id}/generate", response_model=APIResponse)
async def generate_tasks_for_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Generate recommended tasks for a contact"""
    # Verify contact exists
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.company))
        .where(Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # TODO: Implement AI-powered task generation logic
    # This would analyze:
    # - Contact's profile and role
    # - Company signals
    # - Previous interactions
    # - Best practices for outreach
    
    # For now, create some basic tasks based on available data
    tasks_created = 0
    
    # Email task if email is available
    if contact.email:
        email_task = Task(
            contact_id=contact_id,
            title="Send personalized email",
            description=f"Send initial outreach email to {contact.full_name}",
            channel=TaskChannelEnum.EMAIL,
            priority=3,
            recommended_date=datetime.now() + timedelta(days=1)
        )
        db.add(email_task)
        tasks_created += 1
    
    # LinkedIn task if LinkedIn profile is available
    if contact.linkedin_url:
        linkedin_task = Task(
            contact_id=contact_id,
            title="Connect on LinkedIn",
            description=f"Send LinkedIn connection request to {contact.full_name}",
            channel=TaskChannelEnum.LINKEDIN,
            priority=2,
            recommended_date=datetime.now()
        )
        db.add(linkedin_task)
        tasks_created += 1
    
    # Phone task if phone is available and contact is high priority
    if contact.phone and contact.prospect_score and contact.prospect_score > 75:
        phone_task = Task(
            contact_id=contact_id,
            title="Schedule phone call",
            description=f"Schedule discovery call with {contact.full_name}",
            channel=TaskChannelEnum.PHONE,
            priority=4,
            recommended_date=datetime.now() + timedelta(days=3)
        )
        db.add(phone_task)
        tasks_created += 1
    
    await db.commit()
    
    return APIResponse(
        success=True,
        message=f"Generated {tasks_created} tasks for contact"
    )

@router.get("/project/{project_id}/pending")
async def get_pending_tasks_for_project(
    project_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get pending tasks for a project"""
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.contact).selectinload(Contact.company)
        )
        .join(Contact, Task.contact_id == Contact.id)
        .where(
            and_(
                Contact.project_id == project_id,
                Task.status.in_([TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS])
            )
        )
        .order_by(Task.priority.desc(), Task.recommended_date.asc().nulls_last())
        .limit(limit)
    )
    
    tasks = result.scalars().all()
    return tasks

@router.get("/dashboard/stats")
async def get_task_dashboard_stats(
    project_id: Optional[int] = Query(None),
    days_back: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get task statistics for dashboard"""
    base_query = select(Task)
    
    if project_id:
        base_query = base_query.join(Contact, Task.contact_id == Contact.id).where(Contact.project_id == project_id)
    
    # Total tasks
    total_result = await db.execute(
        base_query.with_only_columns(func.count(Task.id))
    )
    total_tasks = total_result.scalar()
    
    # Tasks by status
    status_query = base_query.with_only_columns(Task.status, func.count(Task.id)).group_by(Task.status)
    status_result = await db.execute(status_query)
    tasks_by_status = dict(status_result.all())
    
    # Tasks by channel
    channel_query = base_query.with_only_columns(Task.channel, func.count(Task.id)).group_by(Task.channel)
    channel_result = await db.execute(channel_query)
    tasks_by_channel = dict(channel_result.all())
    
    # Overdue tasks
    now = datetime.now()
    overdue_query = base_query.with_only_columns(func.count(Task.id)).where(
        and_(
            Task.due_date < now,
            Task.status.in_([TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS])
        )
    )
    overdue_result = await db.execute(overdue_query)
    overdue_tasks = overdue_result.scalar()
    
    # Completed tasks in last N days
    cutoff_date = datetime.now() - timedelta(days=days_back)
    completed_query = base_query.with_only_columns(func.count(Task.id)).where(
        and_(
            Task.status == TaskStatusEnum.COMPLETED,
            Task.completed_date >= cutoff_date
        )
    )
    completed_result = await db.execute(completed_query)
    recent_completed = completed_result.scalar()
    
    return {
        "total_tasks": total_tasks or 0,
        "tasks_by_status": tasks_by_status,
        "tasks_by_channel": tasks_by_channel,
        "overdue_tasks": overdue_tasks or 0,
        "recent_completed": recent_completed or 0,
        "days_back": days_back
    }

@router.get("/upcoming/today")
async def get_todays_tasks(
    project_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get tasks scheduled for today"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    query = select(Task).options(
        selectinload(Task.contact).selectinload(Contact.company)
    )
    
    conditions = [
        Task.status.in_([TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS]),
        or_(
            and_(
                Task.recommended_date >= datetime.combine(today, datetime.min.time()),
                Task.recommended_date < datetime.combine(tomorrow, datetime.min.time())
            ),
            and_(
                Task.due_date >= datetime.combine(today, datetime.min.time()),
                Task.due_date < datetime.combine(tomorrow, datetime.min.time())
            )
        )
    ]
    
    if project_id:
        query = query.join(Contact, Task.contact_id == Contact.id)
        conditions.append(Contact.project_id == project_id)
    
    query = query.where(and_(*conditions)).order_by(Task.priority.desc())
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks