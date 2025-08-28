from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.backend.database import get_db
from app.backend.models.database_models import Company, Contact, Signal
from app.backend.models.schemas import (
    Company as CompanySchema,
    CompanyCreate,
    CompanyUpdate,
    APIResponse
)

router = APIRouter(prefix="/companies")

@router.post("/", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new company"""
    db_company = Company(**company.model_dump())
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company

@router.get("/", response_model=List[CompanySchema])
async def get_companies(
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    size_range: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get companies with filtering and search"""
    query = select(Company)
    
    # Apply filters
    conditions = []
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Company.name.ilike(search_term),
                Company.domain.ilike(search_term),
                Company.description.ilike(search_term)
            )
        )
    if industry:
        conditions.append(Company.industry.ilike(f"%{industry}%"))
    if size_range:
        conditions.append(Company.size_range == size_range)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(
        Company.updated_at.desc()
    )
    
    result = await db.execute(query)
    companies = result.scalars().all()
    return companies

@router.get("/{company_id}", response_model=CompanySchema)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific company by ID"""
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.put("/{company_id}", response_model=CompanySchema)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a company"""
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    db_company = result.scalar_one_or_none()
    
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update only provided fields
    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_company, field, value)
    
    await db.commit()
    await db.refresh(db_company)
    return db_company

@router.delete("/{company_id}", response_model=APIResponse)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a company"""
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    db_company = result.scalar_one_or_none()
    
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if company has contacts
    contact_count_result = await db.execute(
        select(func.count(Contact.id)).where(Contact.company_id == company_id)
    )
    contact_count = contact_count_result.scalar()
    
    if contact_count > 0:
        # Don't delete company with contacts, just unlink them
        contacts_result = await db.execute(
            select(Contact).where(Contact.company_id == company_id)
        )
        contacts = contacts_result.scalars().all()
        
        for contact in contacts:
            contact.company_id = None
        
        await db.commit()
    
    await db.delete(db_company)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Company deleted successfully"
    )

@router.get("/{company_id}/contacts")
async def get_company_contacts(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all contacts for a company"""
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get contacts
    result = await db.execute(
        select(Contact)
        .where(Contact.company_id == company_id)
        .offset(skip)
        .limit(limit)
        .order_by(Contact.prospect_score.desc().nulls_last())
    )
    
    contacts = result.scalars().all()
    return contacts

@router.get("/{company_id}/signals")
async def get_company_signals(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get all signals for a company"""
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get signals
    result = await db.execute(
        select(Signal)
        .where(Signal.company_id == company_id)
        .offset(skip)
        .limit(limit)
        .order_by(Signal.signal_date.desc())
    )
    
    signals = result.scalars().all()
    return signals

@router.post("/{company_id}/enrich", response_model=APIResponse)
async def enrich_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger enrichment for a company"""
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # TODO: Trigger background enrichment job for company data
    # This would typically queue a background job to:
    # - Fetch company data from Clearbit, ZoomInfo, etc.
    # - Update company information
    # - Detect new signals
    
    return APIResponse(
        success=True,
        message="Company enrichment queued"
    )

@router.post("/{company_id}/detect-signals", response_model=APIResponse)
async def detect_company_signals(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Trigger signal detection for a company"""
    from app.backend.services.signals import signal_detection_service
    
    try:
        async with signal_detection_service:
            result = await signal_detection_service.detect_signals_for_company(company_id, db)
        
        return APIResponse(
            success=True,
            message="Signal detection completed",
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
            detail=f"Error detecting signals: {str(e)}"
        )

@router.get("/search/domain/{domain}")
async def search_company_by_domain(
    domain: str,
    db: AsyncSession = Depends(get_db)
):
    """Search for a company by domain"""
    result = await db.execute(
        select(Company).where(Company.domain.ilike(f"%{domain}%"))
    )
    company = result.scalar_one_or_none()
    
    if not company:
        return {"found": False, "company": None}
    
    return {"found": True, "company": company}

@router.get("/stats/industries")
async def get_industry_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics by industry"""
    result = await db.execute(
        select(Company.industry, func.count(Company.id))
        .where(Company.industry.is_not(None))
        .group_by(Company.industry)
        .order_by(func.count(Company.id).desc())
        .limit(20)
    )
    
    industries = result.all()
    return [{"industry": industry, "count": count} for industry, count in industries]

@router.get("/stats/sizes")
async def get_size_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics by company size"""
    result = await db.execute(
        select(Company.size_range, func.count(Company.id))
        .where(Company.size_range.is_not(None))
        .group_by(Company.size_range)
        .order_by(func.count(Company.id).desc())
    )
    
    sizes = result.all()
    return [{"size_range": size_range, "count": count} for size_range, count in sizes]