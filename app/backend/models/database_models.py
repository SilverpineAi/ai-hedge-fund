from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Float, 
    ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.backend.database import Base

# Enums for various status and type fields
class ContactGrade(PyEnum):
    A = "A"
    B = "B" 
    C = "C"
    D = "D"
    F = "F"

class EnrichmentStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class SignalType(PyEnum):
    FUNDING = "funding"
    LEADERSHIP_CHANGE = "leadership_change"
    PRODUCT_LAUNCH = "product_launch"
    MARKET_ACTIVITY = "market_activity"
    HIRING_SURGE = "hiring_surge"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    EXPANSION = "expansion"
    PARTNERSHIP = "partnership"

class TaskStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskChannel(PyEnum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    DIRECT_MAIL = "direct_mail"

class ProjectStatus(PyEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# Users table - for multi-tenant architecture
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner")

# Projects table - organize work by campaigns/projects
class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="project")
    upload_batches: Mapped[List["UploadBatch"]] = relationship("UploadBatch", back_populates="project")

# Upload batches - track CSV upload sessions
class UploadBatch(Base):
    __tablename__ = "upload_batches"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    processed_records: Mapped[int] = mapped_column(Integer, default=0)
    successful_records: Mapped[int] = mapped_column(Integer, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[EnrichmentStatus] = mapped_column(Enum(EnrichmentStatus), default=EnrichmentStatus.PENDING)
    error_log: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="upload_batches")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="upload_batch")

# Companies table - store company intelligence data
class Company(Base):
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255))
    size_range: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "1-10", "11-50", "51-200"
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    annual_revenue: Mapped[Optional[float]] = mapped_column(Float)
    funding_stage: Mapped[Optional[str]] = mapped_column(String(100))
    total_funding: Mapped[Optional[float]] = mapped_column(Float)
    headquarters_location: Mapped[Optional[str]] = mapped_column(String(255))
    founded_year: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    technologies: Mapped[Optional[dict]] = mapped_column(JSON)  # Tech stack information
    social_profiles: Mapped[Optional[dict]] = mapped_column(JSON)  # LinkedIn, Twitter, etc.
    enrichment_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Raw data from APIs
    last_enriched: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="company")
    signals: Mapped[List["Signal"]] = relationship("Signal", back_populates="company")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_companies_domain_name', 'domain', 'name'),
        Index('ix_companies_industry_size', 'industry', 'size_range'),
    )

# Contacts table - main entity for leads/prospects
class Contact(Base):
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    upload_batch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("upload_batches.id"))
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id"))
    
    # Basic contact information
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    department: Mapped[Optional[str]] = mapped_column(String(255))
    seniority_level: Mapped[Optional[str]] = mapped_column(String(100))  # Entry, Mid, Senior, Executive, C-Level
    location: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Company information (denormalized for cases where company record doesn't exist)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    company_domain: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Social profiles and additional contact methods
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    twitter_handle: Mapped[Optional[str]] = mapped_column(String(100))
    social_profiles: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Scoring and grading
    contact_grade: Mapped[Optional[ContactGrade]] = mapped_column(Enum(ContactGrade))
    prospect_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    data_quality_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    decision_maker_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    
    # Enrichment tracking
    enrichment_status: Mapped[EnrichmentStatus] = mapped_column(Enum(EnrichmentStatus), default=EnrichmentStatus.PENDING)
    email_found: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    phone_found: Mapped[bool] = mapped_column(Boolean, default=False)
    linkedin_found: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    enrichment_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Raw enrichment data
    original_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Original CSV data
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)  # Custom tags
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    last_enriched: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="contacts")
    upload_batch: Mapped[Optional["UploadBatch"]] = relationship("UploadBatch", back_populates="contacts")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="contacts")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="contact")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_contacts_project_grade', 'project_id', 'contact_grade'),
        Index('ix_contacts_project_score', 'project_id', 'prospect_score'),
        Index('ix_contacts_email_company', 'email', 'company_name'),
        Index('ix_contacts_enrichment_status', 'enrichment_status'),
    )

# Signals table - track growth signals and market activity
class Signal(Base):
    __tablename__ = "signals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Signal details
    signal_type: Mapped[SignalType] = mapped_column(Enum(SignalType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(255), nullable=False)  # News API, LinkedIn, etc.
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Scoring and relevance
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    timing_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100 (how recent/timely)
    
    # Signal-specific data
    signal_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Additional structured data
    keywords: Mapped[Optional[List[str]]] = mapped_column(JSON)  # Keywords that triggered this signal
    
    # Timestamps
    signal_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # When the event occurred
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # When we detected it
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="signals")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_signals_company_type', 'company_id', 'signal_type'),
        Index('ix_signals_relevance_timing', 'relevance_score', 'timing_score'),
        Index('ix_signals_date', 'signal_date'),
    )

# Tasks table - recommended outreach actions
class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"), nullable=False)
    
    # Task details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[TaskChannel] = mapped_column(Enum(TaskChannel), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1-5, where 5 is highest
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Timing and scheduling
    recommended_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Task-specific data
    task_data: Mapped[Optional[dict]] = mapped_column(JSON)  # Channel-specific data (email template, LinkedIn message, etc.)
    ai_generated_content: Mapped[Optional[dict]] = mapped_column(JSON)  # AI-generated messages/content
    
    # Tracking and analytics
    signals_used: Mapped[Optional[List[int]]] = mapped_column(JSON)  # Signal IDs that influenced this task
    engagement_score: Mapped[Optional[float]] = mapped_column(Float)  # Predicted engagement likelihood
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    contact: Mapped["Contact"] = relationship("Contact", back_populates="tasks")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_tasks_contact_status', 'contact_id', 'status'),
        Index('ix_tasks_priority_date', 'priority', 'recommended_date'),
        Index('ix_tasks_channel_status', 'channel', 'status'),
    )

# API Keys and Configuration table - store external API credentials
class ApiConfiguration(Base):
    __tablename__ = "api_configurations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    api_key: Mapped[str] = mapped_column(String(500), nullable=False)  # Should be encrypted
    endpoint_url: Mapped[Optional[str]] = mapped_column(String(500))
    rate_limit: Mapped[Optional[int]] = mapped_column(Integer)  # Requests per hour
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    configuration: Mapped[Optional[dict]] = mapped_column(JSON)  # Additional service-specific config
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Processing Jobs table - track background processing jobs
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)  # enrichment, scoring, signal_detection
    status: Mapped[EnrichmentStatus] = mapped_column(Enum(EnrichmentStatus), default=EnrichmentStatus.PENDING)
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    failed_items: Mapped[int] = mapped_column(Integer, default=0)
    
    # Job configuration and results
    job_config: Mapped[Optional[dict]] = mapped_column(JSON)
    results: Mapped[Optional[dict]] = mapped_column(JSON)
    error_log: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_processing_jobs_type_status', 'job_type', 'status'),
    )