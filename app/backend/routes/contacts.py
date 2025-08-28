from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.backend.database import get_db
from app.backend.models.database_models import Contact, Company, Project
from app.backend.models.schemas import (
    Contact as ContactSchema,
    ContactCreate,
    ContactUpdate,
    APIResponse,
    PaginatedResponse,
    ContactGradeEnum,
    EnrichmentStatusEnum
)

router = APIRouter(prefix="/contacts")

@router.post("/", response_model=ContactSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == contact.project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

@router.get("/", response_model=List[ContactSchema])
async def get_contacts(
    project_id: Optional[int] = Query(None),
    grade: Optional[ContactGradeEnum] = Query(None),
    enrichment_status: Optional[EnrichmentStatusEnum] = Query(None),
    min_prospect_score: Optional[float] = Query(None, ge=0, le=100),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get contacts with filtering and search"""
    query = select(Contact).options(selectinload(Contact.company))
    
    # Apply filters
    conditions = []
    if project_id:
        conditions.append(Contact.project_id == project_id)
    if grade:
        conditions.append(Contact.contact_grade == grade)
    if enrichment_status:
        conditions.append(Contact.enrichment_status == enrichment_status)
    if min_prospect_score is not None:
        conditions.append(Contact.prospect_score >= min_prospect_score)
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Contact.full_name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.company_name.ilike(search_term),
                Contact.title.ilike(search_term)
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(
        Contact.prospect_score.desc().nulls_last(),
        Contact.updated_at.desc()
    )
    
    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts

@router.get("/{contact_id}", response_model=ContactSchema)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific contact by ID"""
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
    
    return contact

@router.put("/{contact_id}", response_model=ContactSchema)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a contact"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    db_contact = result.scalar_one_or_none()
    
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update only provided fields
    update_data = contact_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact, field, value)
    
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

@router.delete("/{contact_id}", response_model=APIResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a contact"""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id)
    )
    db_contact = result.scalar_one_or_none()
    
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    await db.delete(db_contact)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Contact deleted successfully"
    )

@router.post("/{contact_id}/enrich", response_model=APIResponse)
async def enrich_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger enrichment for a specific contact"""
    from app.backend.services.enrichment import enrichment_service
    
    try:
        async with enrichment_service:
            result = await enrichment_service.enrich_contact(contact_id, db)
        
        return APIResponse(
            success=True,
            message="Contact enriched successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enriching contact: {str(e)}"
        )

@router.post("/bulk-enrich", response_model=APIResponse)
async def bulk_enrich_contacts(
    contact_ids: List[int],
    db: AsyncSession = Depends(get_db)
):
    """Trigger enrichment for multiple contacts"""
    if len(contact_ids) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot enrich more than 1000 contacts at once"
        )
    
    # Verify all contacts exist
    result = await db.execute(
        select(Contact).where(Contact.id.in_(contact_ids))
    )
    contacts = result.scalars().all()
    
    if len(contacts) != len(contact_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some contacts not found"
        )
    
    # Update enrichment status for all contacts
    for contact in contacts:
        contact.enrichment_status = EnrichmentStatusEnum.PENDING
    
    await db.commit()
    
    # TODO: Trigger background enrichment jobs
    
    return APIResponse(
        success=True,
        message=f"Enrichment queued for {len(contacts)} contacts"
    )

@router.get("/project/{project_id}/top-prospects")
async def get_top_prospects(
    project_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get top prospects for a project based on scores"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get top prospects
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.company))
        .where(
            and_(
                Contact.project_id == project_id,
                Contact.prospect_score.is_not(None)
            )
        )
        .order_by(Contact.prospect_score.desc())
        .limit(limit)
    )
    
    contacts = result.scalars().all()
    return contacts

@router.post("/{contact_id}/score", response_model=APIResponse)
async def score_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger scoring for a specific contact"""
    from app.backend.services.scoring import scoring_service
    
    try:
        result = await scoring_service.score_contact(contact_id, db)
        return APIResponse(
            success=True,
            message="Contact scored successfully",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring contact: {str(e)}"
        )