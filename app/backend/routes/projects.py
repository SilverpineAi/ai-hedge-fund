from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.backend.database import get_db
from app.backend.models.database_models import Project, Contact
from app.backend.models.schemas import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectUpdate,
    APIResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/projects")

@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    # For now, we'll use a default owner_id of 1
    # In a real app, this would come from authenticated user
    db_project = Project(**project.model_dump(), owner_id=1)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectSchema])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all projects for the current user"""
    # For now, we'll get all projects
    # In a real app, this would filter by authenticated user
    result = await db.execute(
        select(Project)
        .offset(skip)
        .limit(limit)
        .order_by(Project.updated_at.desc())
    )
    projects = result.scalars().all()
    return projects

@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project by ID"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    db_project = result.scalar_one_or_none()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update only provided fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.delete("/{project_id}", response_model=APIResponse)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    db_project = result.scalar_one_or_none()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project has contacts
    contact_count_result = await db.execute(
        select(func.count(Contact.id)).where(Contact.project_id == project_id)
    )
    contact_count = contact_count_result.scalar()
    
    if contact_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete project with {contact_count} contacts. Delete contacts first."
        )
    
    await db.delete(db_project)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Project deleted successfully"
    )

@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get project statistics"""
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get contact statistics
    stats_result = await db.execute(
        select(
            func.count(Contact.id).label('total_contacts'),
            func.count(Contact.contact_grade).label('graded_contacts'),
            func.count(Contact.prospect_score).label('scored_contacts'),
            func.avg(Contact.prospect_score).label('avg_prospect_score'),
            func.avg(Contact.data_quality_score).label('avg_data_quality'),
        ).where(Contact.project_id == project_id)
    )
    stats = stats_result.first()
    
    # Get grade distribution
    grade_result = await db.execute(
        select(Contact.contact_grade, func.count(Contact.id))
        .where(Contact.project_id == project_id)
        .where(Contact.contact_grade.is_not(None))
        .group_by(Contact.contact_grade)
    )
    grade_distribution = {grade: count for grade, count in grade_result.all()}
    
    return {
        "project_id": project_id,
        "total_contacts": stats.total_contacts or 0,
        "graded_contacts": stats.graded_contacts or 0,
        "scored_contacts": stats.scored_contacts or 0,
        "average_prospect_score": float(stats.avg_prospect_score) if stats.avg_prospect_score else None,
        "average_data_quality": float(stats.avg_data_quality) if stats.avg_data_quality else None,
        "grade_distribution": grade_distribution
    }