"""
Scoring and grading services for contacts and prospects
Implements algorithms for contact grading (A-F) and prospect scoring (0-100)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.backend.models.database_models import Contact, Company, Signal, ContactGrade

logger = logging.getLogger(__name__)

class ScoringService:
    """Service for scoring and grading contacts"""
    
    # Scoring weights for different factors
    DATA_QUALITY_WEIGHTS = {
        "email": 25,
        "phone": 20,
        "linkedin": 15,
        "title": 15,
        "company_info": 15,
        "location": 10
    }
    
    DECISION_MAKER_WEIGHTS = {
        "c_level": 100,
        "vp_level": 85,
        "director_level": 70,
        "manager_level": 55,
        "senior_level": 40,
        "mid_level": 25,
        "junior_level": 10
    }
    
    PROSPECT_SCORE_WEIGHTS = {
        "data_quality": 0.3,
        "decision_maker": 0.25,
        "company_signals": 0.25,
        "engagement_potential": 0.2
    }
    
    def __init__(self):
        pass
    
    async def calculate_data_quality_score(self, contact: Contact) -> float:
        """Calculate data quality score based on available contact information"""
        score = 0.0
        
        # Email verification
        if contact.email:
            if contact.email_verified:
                score += self.DATA_QUALITY_WEIGHTS["email"]
            else:
                score += self.DATA_QUALITY_WEIGHTS["email"] * 0.7  # Unverified email gets 70%
        
        # Phone number
        if contact.phone:
            score += self.DATA_QUALITY_WEIGHTS["phone"]
        
        # LinkedIn profile
        if contact.linkedin_url:
            score += self.DATA_QUALITY_WEIGHTS["linkedin"]
        
        # Title/role information
        if contact.title:
            score += self.DATA_QUALITY_WEIGHTS["title"]
        
        # Company information
        company_score = 0
        if contact.company_name:
            company_score += 5
        if contact.company_domain:
            company_score += 5
        if contact.company_id:  # Linked to enriched company record
            company_score += 5
        score += min(company_score, self.DATA_QUALITY_WEIGHTS["company_info"])
        
        # Location information
        if contact.location:
            score += self.DATA_QUALITY_WEIGHTS["location"]
        
        return min(score, 100.0)
    
    def calculate_decision_maker_score(self, contact: Contact) -> float:
        """Calculate decision maker score based on title and seniority"""
        if not contact.title:
            return 0.0
        
        title_lower = contact.title.lower()
        
        # C-Level executives
        c_level_keywords = ["ceo", "cto", "cfo", "coo", "cmo", "chief", "founder", "co-founder", "president"]
        if any(keyword in title_lower for keyword in c_level_keywords):
            return self.DECISION_MAKER_WEIGHTS["c_level"]
        
        # VP Level
        vp_keywords = ["vice president", "vp", "v.p.", "senior vice president", "svp"]
        if any(keyword in title_lower for keyword in vp_keywords):
            return self.DECISION_MAKER_WEIGHTS["vp_level"]
        
        # Director Level
        director_keywords = ["director", "head of", "lead"]
        if any(keyword in title_lower for keyword in director_keywords):
            return self.DECISION_MAKER_WEIGHTS["director_level"]
        
        # Manager Level
        manager_keywords = ["manager", "supervisor", "team lead"]
        if any(keyword in title_lower for keyword in manager_keywords):
            return self.DECISION_MAKER_WEIGHTS["manager_level"]
        
        # Senior Level
        senior_keywords = ["senior", "sr.", "principal", "staff"]
        if any(keyword in title_lower for keyword in senior_keywords):
            return self.DECISION_MAKER_WEIGHTS["senior_level"]
        
        # Check seniority level if available
        if contact.seniority_level:
            seniority_lower = contact.seniority_level.lower()
            if "c-level" in seniority_lower or "executive" in seniority_lower:
                return self.DECISION_MAKER_WEIGHTS["c_level"]
            elif "senior" in seniority_lower:
                return self.DECISION_MAKER_WEIGHTS["senior_level"]
            elif "mid" in seniority_lower:
                return self.DECISION_MAKER_WEIGHTS["mid_level"]
            elif "junior" in seniority_lower or "entry" in seniority_lower:
                return self.DECISION_MAKER_WEIGHTS["junior_level"]
        
        # Default to mid-level if no clear indicators
        return self.DECISION_MAKER_WEIGHTS["mid_level"]
    
    async def calculate_company_signals_score(self, contact: Contact, db: AsyncSession) -> float:
        """Calculate score based on company growth signals"""
        if not contact.company_id:
            return 0.0
        
        # Get recent signals for the company (last 90 days)
        cutoff_date = datetime.now() - timedelta(days=90)
        
        result = await db.execute(
            select(Signal)
            .where(Signal.company_id == contact.company_id)
            .where(Signal.signal_date >= cutoff_date)
            .order_by(Signal.relevance_score.desc())
        )
        signals = result.scalars().all()
        
        if not signals:
            return 0.0
        
        # Calculate weighted signal score
        total_score = 0.0
        signal_weights = {
            "funding": 25,
            "leadership_change": 15,
            "product_launch": 20,
            "expansion": 18,
            "hiring_surge": 12,
            "partnership": 10
        }
        
        for signal in signals:
            weight = signal_weights.get(signal.signal_type.value, 5)
            impact_multiplier = signal.impact_score / 100
            timing_multiplier = signal.timing_score / 100
            
            signal_contribution = weight * impact_multiplier * timing_multiplier
            total_score += signal_contribution
        
        # Normalize to 0-100 scale
        return min(total_score, 100.0)
    
    def calculate_engagement_potential_score(self, contact: Contact) -> float:
        """Calculate engagement potential based on various factors"""
        score = 50.0  # Base score
        
        # Boost for complete contact information
        if contact.email and contact.linkedin_url:
            score += 20
        elif contact.email or contact.linkedin_url:
            score += 10
        
        # Boost for specific industries (customize based on your target market)
        if contact.company_name:
            company_lower = contact.company_name.lower()
            high_value_industries = ["technology", "software", "saas", "fintech", "healthcare"]
            if any(industry in company_lower for industry in high_value_industries):
                score += 15
        
        # Boost for recent activity (if contact was recently added/updated)
        if contact.created_at:
            days_since_creation = (datetime.now() - contact.created_at).days
            if days_since_creation <= 7:
                score += 10
            elif days_since_creation <= 30:
                score += 5
        
        # Penalty for missing critical information
        if not contact.email:
            score -= 15
        if not contact.title:
            score -= 10
        if not contact.company_name:
            score -= 10
        
        return max(0.0, min(score, 100.0))
    
    async def calculate_prospect_score(self, contact: Contact, db: AsyncSession) -> float:
        """Calculate overall prospect score (0-100)"""
        # Calculate component scores
        data_quality = await self.calculate_data_quality_score(contact)
        decision_maker = self.calculate_decision_maker_score(contact)
        company_signals = await self.calculate_company_signals_score(contact, db)
        engagement_potential = self.calculate_engagement_potential_score(contact)
        
        # Calculate weighted average
        prospect_score = (
            data_quality * self.PROSPECT_SCORE_WEIGHTS["data_quality"] +
            decision_maker * self.PROSPECT_SCORE_WEIGHTS["decision_maker"] +
            company_signals * self.PROSPECT_SCORE_WEIGHTS["company_signals"] +
            engagement_potential * self.PROSPECT_SCORE_WEIGHTS["engagement_potential"]
        )
        
        return min(prospect_score, 100.0)
    
    def calculate_contact_grade(self, prospect_score: float, data_quality_score: float) -> ContactGrade:
        """Calculate contact grade (A-F) based on prospect score and data quality"""
        # Require minimum data quality for higher grades
        if data_quality_score < 30:
            return ContactGrade.F
        
        if prospect_score >= 85:
            return ContactGrade.A
        elif prospect_score >= 70:
            return ContactGrade.B
        elif prospect_score >= 55:
            return ContactGrade.C
        elif prospect_score >= 40:
            return ContactGrade.D
        else:
            return ContactGrade.F
    
    async def score_contact(self, contact_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Score a single contact and update the database"""
        # Get contact
        result = await db.execute(
            select(Contact).where(Contact.id == contact_id)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")
        
        # Calculate scores
        data_quality_score = await self.calculate_data_quality_score(contact)
        decision_maker_score = self.calculate_decision_maker_score(contact)
        prospect_score = await self.calculate_prospect_score(contact, db)
        contact_grade = self.calculate_contact_grade(prospect_score, data_quality_score)
        
        # Update contact with scores
        contact.data_quality_score = data_quality_score
        contact.decision_maker_score = decision_maker_score
        contact.prospect_score = prospect_score
        contact.contact_grade = contact_grade
        
        await db.commit()
        
        return {
            "contact_id": contact_id,
            "data_quality_score": data_quality_score,
            "decision_maker_score": decision_maker_score,
            "prospect_score": prospect_score,
            "contact_grade": contact_grade.value,
            "scoring_details": {
                "data_quality_factors": self._get_data_quality_breakdown(contact),
                "decision_maker_factors": self._get_decision_maker_breakdown(contact),
                "engagement_factors": self._get_engagement_breakdown(contact)
            }
        }
    
    async def bulk_score_contacts(self, contact_ids: List[int], db: AsyncSession) -> Dict[str, Any]:
        """Score multiple contacts in batch"""
        results = {
            "total": len(contact_ids),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for contact_id in contact_ids:
            try:
                result = await self.score_contact(contact_id, db)
                results["results"].append(result)
                results["successful"] += 1
                
            except Exception as e:
                logger.error(f"Error scoring contact {contact_id}: {str(e)}")
                results["failed"] += 1
                results["results"].append({
                    "contact_id": contact_id,
                    "error": str(e)
                })
        
        return results
    
    async def rescore_project_contacts(self, project_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Rescore all contacts in a project"""
        # Get all contacts in the project
        result = await db.execute(
            select(Contact.id).where(Contact.project_id == project_id)
        )
        contact_ids = [row[0] for row in result.all()]
        
        if not contact_ids:
            return {"message": "No contacts found in project", "total": 0}
        
        return await self.bulk_score_contacts(contact_ids, db)
    
    def _get_data_quality_breakdown(self, contact: Contact) -> Dict[str, Any]:
        """Get detailed breakdown of data quality factors"""
        return {
            "has_email": bool(contact.email),
            "email_verified": contact.email_verified,
            "has_phone": bool(contact.phone),
            "has_linkedin": bool(contact.linkedin_url),
            "has_title": bool(contact.title),
            "has_company_info": bool(contact.company_name),
            "has_location": bool(contact.location),
            "company_enriched": bool(contact.company_id)
        }
    
    def _get_decision_maker_breakdown(self, contact: Contact) -> Dict[str, Any]:
        """Get detailed breakdown of decision maker factors"""
        title_analysis = self._analyze_title(contact.title) if contact.title else {}
        
        return {
            "title": contact.title,
            "seniority_level": contact.seniority_level,
            "title_analysis": title_analysis
        }
    
    def _get_engagement_breakdown(self, contact: Contact) -> Dict[str, Any]:
        """Get detailed breakdown of engagement factors"""
        return {
            "contact_channels": {
                "email": bool(contact.email),
                "linkedin": bool(contact.linkedin_url),
                "phone": bool(contact.phone)
            },
            "company_info_complete": bool(contact.company_name and contact.company_domain),
            "profile_completeness": self._calculate_profile_completeness(contact)
        }
    
    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """Analyze title to determine seniority and department"""
        if not title:
            return {}
        
        title_lower = title.lower()
        
        # Determine seniority
        seniority = "mid_level"  # default
        if any(keyword in title_lower for keyword in ["ceo", "cto", "cfo", "chief", "founder", "president"]):
            seniority = "c_level"
        elif any(keyword in title_lower for keyword in ["vp", "vice president"]):
            seniority = "vp_level"
        elif any(keyword in title_lower for keyword in ["director", "head of"]):
            seniority = "director_level"
        elif any(keyword in title_lower for keyword in ["manager", "supervisor"]):
            seniority = "manager_level"
        elif any(keyword in title_lower for keyword in ["senior", "sr.", "principal"]):
            seniority = "senior_level"
        elif any(keyword in title_lower for keyword in ["junior", "jr.", "associate", "coordinator"]):
            seniority = "junior_level"
        
        # Determine department
        department = "unknown"
        if any(keyword in title_lower for keyword in ["sales", "business development", "revenue"]):
            department = "sales"
        elif any(keyword in title_lower for keyword in ["marketing", "growth", "demand generation"]):
            department = "marketing"
        elif any(keyword in title_lower for keyword in ["engineering", "development", "technical", "software"]):
            department = "engineering"
        elif any(keyword in title_lower for keyword in ["product", "pm"]):
            department = "product"
        elif any(keyword in title_lower for keyword in ["finance", "accounting", "financial"]):
            department = "finance"
        elif any(keyword in title_lower for keyword in ["operations", "ops", "operational"]):
            department = "operations"
        elif any(keyword in title_lower for keyword in ["hr", "human resources", "people", "talent"]):
            department = "hr"
        
        return {
            "seniority": seniority,
            "department": department,
            "is_decision_maker": seniority in ["c_level", "vp_level", "director_level"]
        }
    
    def _calculate_profile_completeness(self, contact: Contact) -> float:
        """Calculate what percentage of the profile is complete"""
        total_fields = 10
        completed_fields = 0
        
        if contact.full_name:
            completed_fields += 1
        if contact.email:
            completed_fields += 1
        if contact.phone:
            completed_fields += 1
        if contact.title:
            completed_fields += 1
        if contact.company_name:
            completed_fields += 1
        if contact.company_domain:
            completed_fields += 1
        if contact.location:
            completed_fields += 1
        if contact.linkedin_url:
            completed_fields += 1
        if contact.department:
            completed_fields += 1
        if contact.seniority_level:
            completed_fields += 1
        
        return (completed_fields / total_fields) * 100


# Global scoring service instance
scoring_service = ScoringService()