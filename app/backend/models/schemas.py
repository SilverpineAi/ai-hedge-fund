from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from enum import Enum

# Enums for API schemas
class ContactGradeEnum(str, Enum):
    A = "A"
    B = "B" 
    C = "C"
    D = "D"
    F = "F"

class EnrichmentStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class SignalTypeEnum(str, Enum):
    FUNDING = "funding"
    LEADERSHIP_CHANGE = "leadership_change"
    PRODUCT_LAUNCH = "product_launch"
    MARKET_ACTIVITY = "market_activity"
    HIRING_SURGE = "hiring_surge"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    EXPANSION = "expansion"
    PARTNERSHIP = "partnership"

class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskChannelEnum(str, Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    DIRECT_MAIL = "direct_mail"

class ProjectStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

# Project schemas
class ProjectBase(BaseSchema):
    name: str
    description: Optional[str] = None
    status: ProjectStatusEnum = ProjectStatusEnum.ACTIVE

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

# Company schemas
class CompanyBase(BaseSchema):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size_range: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    funding_stage: Optional[str] = None
    total_funding: Optional[float] = None
    headquarters_location: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    technologies: Optional[Dict[str, Any]] = None
    social_profiles: Optional[Dict[str, Any]] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseSchema):
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    size_range: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    funding_stage: Optional[str] = None
    total_funding: Optional[float] = None
    headquarters_location: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    technologies: Optional[Dict[str, Any]] = None
    social_profiles: Optional[Dict[str, Any]] = None

class Company(CompanyBase):
    id: int
    enrichment_data: Optional[Dict[str, Any]] = None
    last_enriched: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# Contact schemas
class ContactBase(BaseSchema):
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    location: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    social_profiles: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class ContactCreate(ContactBase):
    project_id: int

class ContactUpdate(BaseSchema):
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    location: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    social_profiles: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    contact_grade: Optional[ContactGradeEnum] = None
    prospect_score: Optional[float] = Field(None, ge=0, le=100)
    data_quality_score: Optional[float] = Field(None, ge=0, le=100)
    decision_maker_score: Optional[float] = Field(None, ge=0, le=100)

class Contact(ContactBase):
    id: int
    project_id: int
    upload_batch_id: Optional[int] = None
    company_id: Optional[int] = None
    contact_grade: Optional[ContactGradeEnum] = None
    prospect_score: Optional[float] = None
    data_quality_score: Optional[float] = None
    decision_maker_score: Optional[float] = None
    enrichment_status: EnrichmentStatusEnum
    email_found: bool
    email_verified: Optional[bool] = None
    phone_found: bool
    linkedin_found: bool
    enrichment_data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None
    last_enriched: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    company: Optional[Company] = None

# Signal schemas
class SignalBase(BaseSchema):
    signal_type: SignalTypeEnum
    title: str
    description: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    relevance_score: float = Field(ge=0, le=100)
    impact_score: float = Field(ge=0, le=100)
    timing_score: float = Field(ge=0, le=100)
    signal_data: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None
    signal_date: datetime

class SignalCreate(SignalBase):
    company_id: int

class Signal(SignalBase):
    id: int
    company_id: int
    detected_at: datetime
    created_at: datetime
    
    # Related data
    company: Optional[Company] = None

# Task schemas
class TaskBase(BaseSchema):
    title: str
    description: Optional[str] = None
    channel: TaskChannelEnum
    priority: int = Field(ge=1, le=5)
    recommended_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    task_data: Optional[Dict[str, Any]] = None
    ai_generated_content: Optional[Dict[str, Any]] = None
    signals_used: Optional[List[int]] = None
    engagement_score: Optional[float] = Field(None, ge=0, le=100)

class TaskCreate(TaskBase):
    contact_id: int

class TaskUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    channel: Optional[TaskChannelEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[TaskStatusEnum] = None
    recommended_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    task_data: Optional[Dict[str, Any]] = None
    ai_generated_content: Optional[Dict[str, Any]] = None
    signals_used: Optional[List[int]] = None
    engagement_score: Optional[float] = Field(None, ge=0, le=100)

class Task(TaskBase):
    id: int
    contact_id: int
    status: TaskStatusEnum
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    contact: Optional[Contact] = None

# Upload schemas
class UploadBatchBase(BaseSchema):
    filename: str
    total_records: int = 0
    processed_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    status: EnrichmentStatusEnum = EnrichmentStatusEnum.PENDING
    error_log: Optional[Dict[str, Any]] = None

class UploadBatch(UploadBatchBase):
    id: int
    project_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime

# CSV Upload schemas
class CSVUploadResponse(BaseSchema):
    upload_batch_id: int
    filename: str
    total_records: int
    preview_records: List[Dict[str, Any]]
    validation_errors: List[str] = []
    warnings: List[str] = []

class CSVValidationError(BaseSchema):
    row: int
    column: str
    error: str
    value: Optional[str] = None

# Processing Job schemas
class ProcessingJobBase(BaseSchema):
    job_type: str
    status: EnrichmentStatusEnum = EnrichmentStatusEnum.PENDING
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    job_config: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    error_log: Optional[Dict[str, Any]] = None

class ProcessingJob(ProcessingJobBase):
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# Dashboard and Analytics schemas
class ContactStats(BaseSchema):
    total_contacts: int
    graded_contacts: int
    scored_contacts: int
    enriched_contacts: int
    grade_distribution: Dict[str, int]
    average_prospect_score: Optional[float] = None
    average_data_quality: Optional[float] = None

class ProjectDashboard(BaseSchema):
    project: Project
    contact_stats: ContactStats
    recent_signals: List[Signal] = []
    pending_tasks: List[Task] = []
    top_prospects: List[Contact] = []

# Event schemas for WebSocket communication
class WSEvent(BaseSchema):
    type: str
    data: Dict[str, Any]

class EnrichmentProgress(BaseSchema):
    batch_id: int
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    progress_percentage: float
    current_status: EnrichmentStatusEnum
    estimated_completion: Optional[datetime] = None

# API Response schemas
class APIResponse(BaseSchema):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool