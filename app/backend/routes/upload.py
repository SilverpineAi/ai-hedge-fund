import csv
import io
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
from datetime import datetime

from app.backend.database import get_db
from app.backend.models.database_models import Project, UploadBatch, Contact, EnrichmentStatus
from app.backend.models.schemas import (
    CSVUploadResponse,
    UploadBatch as UploadBatchSchema,
    APIResponse,
    EnrichmentStatusEnum
)

router = APIRouter(prefix="/upload")

# Define required and optional CSV columns
REQUIRED_COLUMNS = ['full_name']
OPTIONAL_COLUMNS = [
    'first_name', 'last_name', 'email', 'phone', 'title', 'department',
    'seniority_level', 'location', 'company_name', 'company_domain',
    'linkedin_url', 'twitter_handle'
]
ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

def validate_csv_headers(headers: List[str]) -> tuple[List[str], List[str]]:
    """Validate CSV headers and return errors and warnings"""
    errors = []
    warnings = []
    
    # Check for required columns
    for required_col in REQUIRED_COLUMNS:
        if required_col not in headers:
            errors.append(f"Required column '{required_col}' is missing")
    
    # Check for unknown columns
    unknown_columns = [col for col in headers if col not in ALL_COLUMNS]
    if unknown_columns:
        warnings.append(f"Unknown columns will be ignored: {', '.join(unknown_columns)}")
    
    # Check for empty column names
    if '' in headers or None in headers:
        errors.append("Empty column names found")
    
    # Check for duplicate column names
    if len(headers) != len(set(headers)):
        duplicates = [col for col in set(headers) if headers.count(col) > 1]
        errors.append(f"Duplicate column names found: {', '.join(duplicates)}")
    
    return errors, warnings

def clean_contact_data(row: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate contact data from CSV row"""
    cleaned = {}
    
    # Handle name fields
    if 'full_name' in row and row['full_name']:
        cleaned['full_name'] = str(row['full_name']).strip()
        
        # Try to split full_name if first_name/last_name not provided
        if 'first_name' not in row or not row['first_name']:
            name_parts = cleaned['full_name'].split()
            if len(name_parts) >= 2:
                cleaned['first_name'] = name_parts[0]
                cleaned['last_name'] = ' '.join(name_parts[1:])
            elif len(name_parts) == 1:
                cleaned['first_name'] = name_parts[0]
    
    # Handle other string fields
    string_fields = ['first_name', 'last_name', 'email', 'phone', 'title', 
                    'department', 'seniority_level', 'location', 'company_name', 
                    'company_domain', 'linkedin_url', 'twitter_handle']
    
    for field in string_fields:
        if field in row and row[field] and str(row[field]).strip():
            cleaned[field] = str(row[field]).strip()
    
    # Basic email validation
    if 'email' in cleaned:
        email = cleaned['email'].lower()
        if '@' not in email or '.' not in email:
            # Invalid email, remove it
            del cleaned['email']
        else:
            cleaned['email'] = email
    
    # Clean phone number
    if 'phone' in cleaned:
        phone = ''.join(filter(str.isdigit, cleaned['phone']))
        if len(phone) < 10:
            del cleaned['phone']
        else:
            cleaned['phone'] = phone
    
    # Clean LinkedIn URL
    if 'linkedin_url' in cleaned:
        url = cleaned['linkedin_url']
        if not url.startswith('http'):
            url = 'https://' + url
        if 'linkedin.com' not in url:
            del cleaned['linkedin_url']
        else:
            cleaned['linkedin_url'] = url
    
    return cleaned

@router.post("/csv", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a CSV file of contacts"""
    
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Check file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Try to detect encoding
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to decode file. Please ensure it's a valid CSV file."
                )
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(text_content))
        headers = csv_reader.fieldnames
        
        if not headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file has no headers"
            )
        
        # Validate headers
        validation_errors, warnings = validate_csv_headers(headers)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV validation failed: {'; '.join(validation_errors)}"
            )
        
        # Read all rows
        rows = list(csv_reader)
        
        if len(rows) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file contains no data rows"
            )
        
        if len(rows) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file contains too many rows. Maximum 10,000 contacts allowed."
            )
        
        # Create upload batch
        upload_batch = UploadBatch(
            project_id=project_id,
            filename=file.filename,
            total_records=len(rows),
            status=EnrichmentStatus.PENDING
        )
        db.add(upload_batch)
        await db.commit()
        await db.refresh(upload_batch)
        
        # Process rows and create contacts
        contacts_created = 0
        contacts_failed = 0
        preview_records = []
        processing_errors = []
        
        for i, row in enumerate(rows[:100]):  # Process first 100 for preview
            try:
                cleaned_data = clean_contact_data(row)
                
                if not cleaned_data.get('full_name'):
                    processing_errors.append(f"Row {i+2}: Missing required field 'full_name'")
                    contacts_failed += 1
                    continue
                
                # Create contact
                contact = Contact(
                    project_id=project_id,
                    upload_batch_id=upload_batch.id,
                    original_data=row,
                    **cleaned_data
                )
                db.add(contact)
                contacts_created += 1
                
                # Add to preview (first 10 records)
                if len(preview_records) < 10:
                    preview_records.append(cleaned_data)
                
            except Exception as e:
                processing_errors.append(f"Row {i+2}: {str(e)}")
                contacts_failed += 1
        
        # Update upload batch with results
        upload_batch.processed_records = contacts_created + contacts_failed
        upload_batch.successful_records = contacts_created
        upload_batch.failed_records = contacts_failed
        upload_batch.status = EnrichmentStatus.COMPLETED
        
        if processing_errors:
            upload_batch.error_log = {"errors": processing_errors}
        
        await db.commit()
        
        # If we have more than 100 rows, queue the rest for background processing
        if len(rows) > 100:
            # TODO: Queue background job to process remaining rows
            upload_batch.status = EnrichmentStatus.IN_PROGRESS
            await db.commit()
        
        return CSVUploadResponse(
            upload_batch_id=upload_batch.id,
            filename=file.filename,
            total_records=len(rows),
            preview_records=preview_records,
            validation_errors=processing_errors,
            warnings=warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV file: {str(e)}"
        )

@router.get("/batches/{batch_id}", response_model=UploadBatchSchema)
async def get_upload_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get upload batch details"""
    result = await db.execute(
        select(UploadBatch).where(UploadBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload batch not found"
        )
    
    return batch

@router.get("/batches/project/{project_id}")
async def get_project_batches(
    project_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all upload batches for a project"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get batches
    result = await db.execute(
        select(UploadBatch)
        .where(UploadBatch.project_id == project_id)
        .offset(skip)
        .limit(limit)
        .order_by(UploadBatch.created_at.desc())
    )
    batches = result.scalars().all()
    return batches

@router.delete("/batches/{batch_id}", response_model=APIResponse)
async def delete_upload_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an upload batch and all its contacts"""
    result = await db.execute(
        select(UploadBatch).where(UploadBatch.id == batch_id)
    )
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload batch not found"
        )
    
    # Delete all contacts from this batch
    contacts_result = await db.execute(
        select(Contact).where(Contact.upload_batch_id == batch_id)
    )
    contacts = contacts_result.scalars().all()
    
    for contact in contacts:
        await db.delete(contact)
    
    # Delete the batch
    await db.delete(batch)
    await db.commit()
    
    return APIResponse(
        success=True,
        message=f"Upload batch and {len(contacts)} contacts deleted successfully"
    )