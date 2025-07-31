"""
CRUD Operations

Basic Create, Read, Update, Delete operations for database models.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime

from .models import Influencer, Brand, Campaign, Post, InfluencerMetrics, BrandInfluencerMatch

class InfluencerCRUD:
    """CRUD operations for Influencer model"""
    
    @staticmethod
    def create(db: Session, influencer_data: Dict[str, Any]) -> Influencer:
        """Create a new influencer"""
        influencer = Influencer(**influencer_data)
        db.add(influencer)
        db.commit()
        db.refresh(influencer)
        return influencer
    
    @staticmethod
    def get_by_id(db: Session, influencer_id: int) -> Optional[Influencer]:
        """Get influencer by ID"""
        return db.query(Influencer).filter(Influencer.id == influencer_id).first()
    
    @staticmethod
    def get_by_username_platform(db: Session, username: str, platform: str) -> Optional[Influencer]:
        """Get influencer by username and platform"""
        return db.query(Influencer).filter(
            and_(Influencer.username == username, Influencer.platform == platform)
        ).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Influencer]:
        """Get all influencers with pagination"""
        return db.query(Influencer).filter(Influencer.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def search(db: Session, 
               platform: Optional[str] = None,
               category: Optional[str] = None,
               min_followers: int = 0,
               max_followers: Optional[int] = None,
               verified_only: bool = False,
               skip: int = 0,
               limit: int = 100) -> List[Influencer]:
        """Search influencers with filters"""
        query = db.query(Influencer).filter(Influencer.is_active == True)
        
        if platform:
            query = query.filter(Influencer.platform == platform)
        
        if category:
            query = query.filter(Influencer.category == category)
        
        query = query.filter(Influencer.follower_count >= min_followers)
        
        if max_followers:
            query = query.filter(Influencer.follower_count <= max_followers)
        
        if verified_only:
            query = query.filter(Influencer.verified == True)
        
        return query.order_by(desc(Influencer.follower_count)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, influencer_id: int, update_data: Dict[str, Any]) -> Optional[Influencer]:
        """Update influencer"""
        influencer = db.query(Influencer).filter(Influencer.id == influencer_id).first()
        if influencer:
            for key, value in update_data.items():
                setattr(influencer, key, value)
            influencer.updated_at = datetime.now()
            db.commit()
            db.refresh(influencer)
        return influencer
    
    @staticmethod
    def delete(db: Session, influencer_id: int) -> bool:
        """Soft delete influencer"""
        influencer = db.query(Influencer).filter(Influencer.id == influencer_id).first()
        if influencer:
            influencer.is_active = False
            db.commit()
            return True
        return False

class BrandCRUD:
    """CRUD operations for Brand model"""
    
    @staticmethod
    def create(db: Session, brand_data: Dict[str, Any]) -> Brand:
        """Create a new brand"""
        brand = Brand(**brand_data)
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand
    
    @staticmethod
    def get_by_id(db: Session, brand_id: int) -> Optional[Brand]:
        """Get brand by ID"""
        return db.query(Brand).filter(Brand.id == brand_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Brand]:
        """Get brand by name"""
        return db.query(Brand).filter(Brand.name == name).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Get all brands with pagination"""
        return db.query(Brand).filter(Brand.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, brand_id: int, update_data: Dict[str, Any]) -> Optional[Brand]:
        """Update brand"""
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if brand:
            for key, value in update_data.items():
                setattr(brand, key, value)
            brand.updated_at = datetime.now()
            db.commit()
            db.refresh(brand)
        return brand
    
    @staticmethod
    def delete(db: Session, brand_id: int) -> bool:
        """Soft delete brand"""
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if brand:
            brand.is_active = False
            db.commit()
            return True
        return False

class CampaignCRUD:
    """CRUD operations for Campaign model"""
    
    @staticmethod
    def create(db: Session, campaign_data: Dict[str, Any]) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(**campaign_data)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign
    
    @staticmethod
    def get_by_id(db: Session, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID"""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    @staticmethod
    def get_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get campaigns by brand"""
        return db.query(Campaign).filter(Campaign.brand_id == brand_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Get all campaigns with pagination"""
        return db.query(Campaign).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, campaign_id: int, update_data: Dict[str, Any]) -> Optional[Campaign]:
        """Update campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            for key, value in update_data.items():
                setattr(campaign, key, value)
            campaign.updated_at = datetime.now()
            db.commit()
            db.refresh(campaign)
        return campaign
    
    @staticmethod
    def delete(db: Session, campaign_id: int) -> bool:
        """Delete campaign"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            db.delete(campaign)
            db.commit()
            return True
        return False