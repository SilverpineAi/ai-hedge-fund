"""
Data enrichment services for contacts and companies
Integrates with external APIs like Hunter.io, Clearbit, etc.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.models.database_models import Contact, Company, EnrichmentStatus
from app.backend.database import get_db_session

logger = logging.getLogger(__name__)

class EnrichmentService:
    """Service for enriching contact and company data"""
    
    def __init__(self):
        self.hunter_api_key = os.getenv("HUNTER_API_KEY")
        self.clearbit_api_key = os.getenv("CLEARBIT_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def enrich_contact(self, contact_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Enrich a single contact with missing data"""
        # Get contact
        result = await db.execute(select(Contact).where(Contact.id == contact_id))
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")
        
        # Update status to in progress
        contact.enrichment_status = EnrichmentStatus.IN_PROGRESS
        await db.commit()
        
        enrichment_results = {
            "contact_id": contact_id,
            "original_data": {
                "email": contact.email,
                "phone": contact.phone,
                "linkedin_url": contact.linkedin_url
            },
            "enriched_data": {},
            "errors": []
        }
        
        try:
            # Find email if missing
            if not contact.email and contact.full_name and contact.company_domain:
                email_result = await self.find_email(contact.full_name, contact.company_domain)
                if email_result.get("email"):
                    contact.email = email_result["email"]
                    contact.email_found = True
                    contact.email_verified = email_result.get("verified", False)
                    enrichment_results["enriched_data"]["email"] = email_result
            
            # Find LinkedIn profile if missing
            if not contact.linkedin_url and contact.full_name and contact.company_name:
                linkedin_result = await self.find_linkedin_profile(contact.full_name, contact.company_name)
                if linkedin_result.get("linkedin_url"):
                    contact.linkedin_url = linkedin_result["linkedin_url"]
                    contact.linkedin_found = True
                    enrichment_results["enriched_data"]["linkedin"] = linkedin_result
            
            # Enrich company data if missing
            if contact.company_domain and not contact.company_id:
                company_result = await self.enrich_company_data(contact.company_domain)
                if company_result.get("company_id"):
                    contact.company_id = company_result["company_id"]
                    enrichment_results["enriched_data"]["company"] = company_result
            
            # Update enrichment status and timestamp
            contact.enrichment_status = EnrichmentStatus.COMPLETED
            contact.last_enriched = datetime.now()
            contact.enrichment_data = enrichment_results["enriched_data"]
            
            await db.commit()
            
            return enrichment_results
            
        except Exception as e:
            logger.error(f"Error enriching contact {contact_id}: {str(e)}")
            contact.enrichment_status = EnrichmentStatus.FAILED
            enrichment_results["errors"].append(str(e))
            await db.commit()
            return enrichment_results
    
    async def find_email(self, full_name: str, domain: str) -> Dict[str, Any]:
        """Find email using Hunter.io API"""
        if not self.hunter_api_key:
            return {"error": "Hunter.io API key not configured"}
        
        try:
            # Split name for better matching
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Clean domain
            domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
            
            url = "https://api.hunter.io/v2/email-finder"
            params = {
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name,
                "api_key": self.hunter_api_key
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data") and data["data"].get("email"):
                return {
                    "email": data["data"]["email"],
                    "verified": data["data"].get("verification", {}).get("result") == "deliverable",
                    "confidence": data["data"].get("confidence", 0),
                    "source": "hunter.io"
                }
            
            return {"error": "Email not found"}
            
        except Exception as e:
            logger.error(f"Error finding email for {full_name}@{domain}: {str(e)}")
            return {"error": str(e)}
    
    async def find_linkedin_profile(self, full_name: str, company_name: str) -> Dict[str, Any]:
        """Find LinkedIn profile (placeholder - would integrate with LinkedIn API or web scraping)"""
        # This is a placeholder implementation
        # In a real system, you'd integrate with:
        # - LinkedIn Sales Navigator API
        # - Web scraping services
        # - People search APIs like PeopleDataLabs
        
        try:
            # Simulate finding LinkedIn profile
            await asyncio.sleep(0.5)  # Simulate API call
            
            # Generate a potential LinkedIn URL (this is just for demo)
            name_slug = full_name.lower().replace(" ", "-").replace(".", "")
            potential_url = f"https://linkedin.com/in/{name_slug}"
            
            return {
                "linkedin_url": potential_url,
                "confidence": 0.6,  # Low confidence since this is simulated
                "source": "simulated"
            }
            
        except Exception as e:
            logger.error(f"Error finding LinkedIn for {full_name}: {str(e)}")
            return {"error": str(e)}
    
    async def enrich_company_data(self, domain: str) -> Dict[str, Any]:
        """Enrich company data using Clearbit or similar APIs"""
        if not self.clearbit_api_key:
            return await self._simulate_company_enrichment(domain)
        
        try:
            # Clean domain
            domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
            
            url = f"https://company.clearbit.com/v2/companies/find"
            headers = {"Authorization": f"Bearer {self.clearbit_api_key}"}
            params = {"domain": domain}
            
            response = await self.client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return await self._process_clearbit_company_data(data)
            elif response.status_code == 404:
                return {"error": "Company not found"}
            else:
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error enriching company data for {domain}: {str(e)}")
            return await self._simulate_company_enrichment(domain)
    
    async def _process_clearbit_company_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Clearbit company data and create/update company record"""
        async with get_db_session() as db:
            # Check if company already exists
            result = await db.execute(
                select(Company).where(Company.domain == data.get("domain"))
            )
            company = result.scalar_one_or_none()
            
            if not company:
                # Create new company
                company = Company(
                    name=data.get("name", ""),
                    domain=data.get("domain", ""),
                    industry=data.get("category", {}).get("industry"),
                    employee_count=data.get("metrics", {}).get("employees"),
                    annual_revenue=data.get("metrics", {}).get("annualRevenue"),
                    founded_year=data.get("foundedYear"),
                    description=data.get("description"),
                    headquarters_location=self._format_location(data.get("geo", {})),
                    technologies=data.get("tech"),
                    social_profiles=self._extract_social_profiles(data),
                    enrichment_data=data,
                    last_enriched=datetime.now()
                )
                db.add(company)
            else:
                # Update existing company
                company.industry = data.get("category", {}).get("industry") or company.industry
                company.employee_count = data.get("metrics", {}).get("employees") or company.employee_count
                company.annual_revenue = data.get("metrics", {}).get("annualRevenue") or company.annual_revenue
                company.founded_year = data.get("foundedYear") or company.founded_year
                company.description = data.get("description") or company.description
                company.headquarters_location = self._format_location(data.get("geo", {})) or company.headquarters_location
                company.technologies = data.get("tech") or company.technologies
                company.social_profiles = self._extract_social_profiles(data) or company.social_profiles
                company.enrichment_data = data
                company.last_enriched = datetime.now()
            
            await db.commit()
            await db.refresh(company)
            
            return {
                "company_id": company.id,
                "enriched_fields": ["industry", "employee_count", "annual_revenue", "description"],
                "source": "clearbit"
            }
    
    async def _simulate_company_enrichment(self, domain: str) -> Dict[str, Any]:
        """Simulate company enrichment when APIs are not available"""
        await asyncio.sleep(0.5)  # Simulate API call
        
        # This would be replaced with actual API calls or web scraping
        simulated_data = {
            "name": domain.replace(".com", "").replace(".io", "").title(),
            "domain": domain,
            "industry": "Technology",
            "employee_count": 50,
            "description": f"Technology company based on {domain}",
            "source": "simulated"
        }
        
        return simulated_data
    
    def _format_location(self, geo_data: Dict[str, Any]) -> Optional[str]:
        """Format location from geo data"""
        if not geo_data:
            return None
        
        parts = []
        if geo_data.get("city"):
            parts.append(geo_data["city"])
        if geo_data.get("state"):
            parts.append(geo_data["state"])
        if geo_data.get("country"):
            parts.append(geo_data["country"])
        
        return ", ".join(parts) if parts else None
    
    def _extract_social_profiles(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract social media profiles from company data"""
        profiles = {}
        
        if data.get("linkedin", {}).get("handle"):
            profiles["linkedin"] = f"https://linkedin.com/company/{data['linkedin']['handle']}"
        
        if data.get("twitter", {}).get("handle"):
            profiles["twitter"] = f"https://twitter.com/{data['twitter']['handle']}"
        
        if data.get("facebook", {}).get("handle"):
            profiles["facebook"] = f"https://facebook.com/{data['facebook']['handle']}"
        
        return profiles
    
    async def bulk_enrich_contacts(self, contact_ids: List[int]) -> Dict[str, Any]:
        """Enrich multiple contacts in batch"""
        results = {
            "total": len(contact_ids),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        async with get_db_session() as db:
            for contact_id in contact_ids:
                try:
                    result = await self.enrich_contact(contact_id, db)
                    results["results"].append(result)
                    
                    if not result.get("errors"):
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        
                except Exception as e:
                    logger.error(f"Error in bulk enrichment for contact {contact_id}: {str(e)}")
                    results["failed"] += 1
                    results["results"].append({
                        "contact_id": contact_id,
                        "errors": [str(e)]
                    })
                
                # Rate limiting - avoid hitting API limits
                await asyncio.sleep(0.5)
        
        return results


# Global enrichment service instance
enrichment_service = EnrichmentService()