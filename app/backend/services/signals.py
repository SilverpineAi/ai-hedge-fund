"""
Signal detection service for identifying growth signals and market activity
Integrates with news APIs, funding databases, and social media monitoring
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.models.database_models import Company, Signal, SignalType
from app.backend.database import get_db_session

logger = logging.getLogger(__name__)

class SignalDetectionService:
    """Service for detecting and creating growth signals"""
    
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.crunchbase_api_key = os.getenv("CRUNCHBASE_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def detect_signals_for_company(self, company_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Detect all types of signals for a specific company"""
        # Get company
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        detection_results = {
            "company_id": company_id,
            "company_name": company.name,
            "signals_detected": 0,
            "signals": [],
            "errors": []
        }
        
        try:
            # Detect different types of signals
            signal_detectors = [
                self.detect_funding_signals,
                self.detect_leadership_signals,
                self.detect_product_signals,
                self.detect_hiring_signals,
                self.detect_partnership_signals,
                self.detect_expansion_signals
            ]
            
            for detector in signal_detectors:
                try:
                    signals = await detector(company, db)
                    detection_results["signals"].extend(signals)
                    detection_results["signals_detected"] += len(signals)
                except Exception as e:
                    logger.error(f"Error in signal detector {detector.__name__}: {str(e)}")
                    detection_results["errors"].append(f"{detector.__name__}: {str(e)}")
            
            return detection_results
            
        except Exception as e:
            logger.error(f"Error detecting signals for company {company_id}: {str(e)}")
            detection_results["errors"].append(str(e))
            return detection_results
    
    async def detect_funding_signals(self, company: Company, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect funding-related signals"""
        signals = []
        
        if not company.domain:
            return signals
        
        try:
            # Search for funding news
            funding_keywords = ["funding", "investment", "raised", "series", "round", "venture capital", "vc"]
            news_results = await self.search_company_news(company.name, funding_keywords, days_back=90)
            
            for article in news_results:
                # Analyze article for funding information
                funding_amount = self._extract_funding_amount(article.get("description", ""))
                funding_stage = self._extract_funding_stage(article.get("description", ""))
                
                signal_data = {
                    "funding_amount": funding_amount,
                    "funding_stage": funding_stage,
                    "article_url": article.get("url"),
                    "source_name": article.get("source", {}).get("name")
                }
                
                # Calculate scores
                relevance_score = self._calculate_funding_relevance(article, funding_amount)
                impact_score = self._calculate_funding_impact(funding_amount, funding_stage)
                timing_score = self._calculate_timing_score(article.get("publishedAt"))
                
                # Create signal record
                signal = Signal(
                    company_id=company.id,
                    signal_type=SignalType.FUNDING,
                    title=f"Funding: {article.get('title', 'Unknown')}",
                    description=article.get("description", ""),
                    source="news_api",
                    source_url=article.get("url"),
                    relevance_score=relevance_score,
                    impact_score=impact_score,
                    timing_score=timing_score,
                    signal_data=signal_data,
                    keywords=funding_keywords,
                    signal_date=self._parse_date(article.get("publishedAt")),
                    detected_at=datetime.now()
                )
                
                db.add(signal)
                signals.append({
                    "type": "funding",
                    "title": signal.title,
                    "relevance_score": relevance_score,
                    "impact_score": impact_score
                })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error detecting funding signals for {company.name}: {str(e)}")
        
        return signals
    
    async def detect_leadership_signals(self, company: Company, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect leadership change signals"""
        signals = []
        
        try:
            leadership_keywords = ["ceo", "cto", "cfo", "cmo", "hired", "appointed", "joins", "executive", "leadership"]
            news_results = await self.search_company_news(company.name, leadership_keywords, days_back=60)
            
            for article in news_results:
                # Analyze for leadership changes
                leadership_info = self._extract_leadership_info(article.get("description", ""))
                
                signal_data = {
                    "executive_role": leadership_info.get("role"),
                    "executive_name": leadership_info.get("name"),
                    "change_type": leadership_info.get("change_type"),  # hired, promoted, left
                    "article_url": article.get("url")
                }
                
                relevance_score = self._calculate_leadership_relevance(article, leadership_info)
                impact_score = self._calculate_leadership_impact(leadership_info)
                timing_score = self._calculate_timing_score(article.get("publishedAt"))
                
                signal = Signal(
                    company_id=company.id,
                    signal_type=SignalType.LEADERSHIP_CHANGE,
                    title=f"Leadership: {article.get('title', 'Unknown')}",
                    description=article.get("description", ""),
                    source="news_api",
                    source_url=article.get("url"),
                    relevance_score=relevance_score,
                    impact_score=impact_score,
                    timing_score=timing_score,
                    signal_data=signal_data,
                    keywords=leadership_keywords,
                    signal_date=self._parse_date(article.get("publishedAt")),
                    detected_at=datetime.now()
                )
                
                db.add(signal)
                signals.append({
                    "type": "leadership_change",
                    "title": signal.title,
                    "relevance_score": relevance_score,
                    "impact_score": impact_score
                })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error detecting leadership signals for {company.name}: {str(e)}")
        
        return signals
    
    async def detect_product_signals(self, company: Company, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect product launch and development signals"""
        signals = []
        
        try:
            product_keywords = ["launch", "product", "release", "beta", "feature", "platform", "solution"]
            news_results = await self.search_company_news(company.name, product_keywords, days_back=45)
            
            for article in news_results:
                product_info = self._extract_product_info(article.get("description", ""))
                
                signal_data = {
                    "product_name": product_info.get("name"),
                    "product_type": product_info.get("type"),
                    "launch_stage": product_info.get("stage"),  # beta, launch, update
                    "article_url": article.get("url")
                }
                
                relevance_score = self._calculate_product_relevance(article, product_info)
                impact_score = self._calculate_product_impact(product_info)
                timing_score = self._calculate_timing_score(article.get("publishedAt"))
                
                signal = Signal(
                    company_id=company.id,
                    signal_type=SignalType.PRODUCT_LAUNCH,
                    title=f"Product: {article.get('title', 'Unknown')}",
                    description=article.get("description", ""),
                    source="news_api",
                    source_url=article.get("url"),
                    relevance_score=relevance_score,
                    impact_score=impact_score,
                    timing_score=timing_score,
                    signal_data=signal_data,
                    keywords=product_keywords,
                    signal_date=self._parse_date(article.get("publishedAt")),
                    detected_at=datetime.now()
                )
                
                db.add(signal)
                signals.append({
                    "type": "product_launch",
                    "title": signal.title,
                    "relevance_score": relevance_score,
                    "impact_score": impact_score
                })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error detecting product signals for {company.name}: {str(e)}")
        
        return signals
    
    async def detect_hiring_signals(self, company: Company, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect hiring surge signals"""
        signals = []
        
        try:
            # This would typically integrate with LinkedIn API or job board APIs
            # For now, we'll simulate hiring signal detection
            hiring_data = await self._simulate_hiring_detection(company)
            
            if hiring_data.get("hiring_surge"):
                signal = Signal(
                    company_id=company.id,
                    signal_type=SignalType.HIRING_SURGE,
                    title=f"Hiring Surge: {hiring_data['new_positions']} new positions",
                    description=f"Company is actively hiring for {hiring_data['new_positions']} positions, indicating growth",
                    source="simulated",
                    relevance_score=75.0,
                    impact_score=hiring_data.get("impact_score", 60.0),
                    timing_score=90.0,  # Recent hiring is very timely
                    signal_data=hiring_data,
                    keywords=["hiring", "jobs", "positions", "growth"],
                    signal_date=datetime.now(),
                    detected_at=datetime.now()
                )
                
                db.add(signal)
                await db.commit()
                
                signals.append({
                    "type": "hiring_surge",
                    "title": signal.title,
                    "relevance_score": 75.0,
                    "impact_score": hiring_data.get("impact_score", 60.0)
                })
            
        except Exception as e:
            logger.error(f"Error detecting hiring signals for {company.name}: {str(e)}")
        
        return signals
    
    async def detect_partnership_signals(self, company: Company, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect partnership and collaboration signals"""
        signals = []
        
        try:
            partnership_keywords = ["partnership", "collaboration", "alliance", "integration", "announces"]
            news_results = await self.search_company_news(company.name, partnership_keywords, days_back=60)
            
            for article in news_results:
                partnership_info = self._extract_partnership_info(article.get("description", ""))
                
                signal_data = {
                    "partner_company": partnership_info.get("partner"),
                    "partnership_type": partnership_info.get("type"),
                    "article_url": article.get("url")
                }
                
                relevance_score = self._calculate_partnership_relevance(article, partnership_info)
                impact_score = self._calculate_partnership_impact(partnership_info)
                timing_score = self._calculate_timing_score(article.get("publishedAt"))
                
                signal = Signal(
                    company_id=company.id,
                    signal_type=SignalType.PARTNERSHIP,
                    title=f"Partnership: {article.get('title', 'Unknown')}",
                    description=article.get("description", ""),
                    source="news_api",
                    source_url=article.get("url"),
                    relevance_score=relevance_score,
                    impact_score=impact_score,
                    timing_score=timing_score,
                    signal_data=signal_data,
                    keywords=partnership_keywords,
                    signal_date=self._parse_date(article.get("publishedAt")),
                    detected_at=datetime.now()
                )
                
                db.add(signal)
                signals.append({
                    "type": "partnership",
                    "title": signal.title,
                    "relevance_score": relevance_score,
                    "impact_score": impact_score
                })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error detecting partnership signals for {company.name}: {str(e)}")
        
        return signals
    
    async def detect_expansion_signals(self, company: Company, db: AsyncSession) -> List[Dict[str, Any]]:
        """Detect expansion and growth signals"""
        signals = []
        
        try:
            expansion_keywords = ["expansion", "opens", "new office", "international", "market", "grows"]
            news_results = await self.search_company_news(company.name, expansion_keywords, days_back=90)
            
            for article in news_results:
                expansion_info = self._extract_expansion_info(article.get("description", ""))
                
                signal_data = {
                    "expansion_type": expansion_info.get("type"),  # geographic, market, office
                    "location": expansion_info.get("location"),
                    "article_url": article.get("url")
                }
                
                relevance_score = self._calculate_expansion_relevance(article, expansion_info)
                impact_score = self._calculate_expansion_impact(expansion_info)
                timing_score = self._calculate_timing_score(article.get("publishedAt"))
                
                signal = Signal(
                    company_id=company.id,
                    signal_type=SignalType.EXPANSION,
                    title=f"Expansion: {article.get('title', 'Unknown')}",
                    description=article.get("description", ""),
                    source="news_api",
                    source_url=article.get("url"),
                    relevance_score=relevance_score,
                    impact_score=impact_score,
                    timing_score=timing_score,
                    signal_data=signal_data,
                    keywords=expansion_keywords,
                    signal_date=self._parse_date(article.get("publishedAt")),
                    detected_at=datetime.now()
                )
                
                db.add(signal)
                signals.append({
                    "type": "expansion",
                    "title": signal.title,
                    "relevance_score": relevance_score,
                    "impact_score": impact_score
                })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error detecting expansion signals for {company.name}: {str(e)}")
        
        return signals
    
    async def search_company_news(self, company_name: str, keywords: List[str], days_back: int = 30) -> List[Dict[str, Any]]:
        """Search for company news using News API"""
        if not self.news_api_key:
            return await self._simulate_news_search(company_name, keywords)
        
        try:
            # Calculate date range
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # Build search query
            keyword_query = " OR ".join(keywords)
            query = f'"{company_name}" AND ({keyword_query})'
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": 20,
                "apiKey": self.news_api_key
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("articles", [])
            
        except Exception as e:
            logger.error(f"Error searching news for {company_name}: {str(e)}")
            return await self._simulate_news_search(company_name, keywords)
    
    async def _simulate_news_search(self, company_name: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Simulate news search when API is not available"""
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Return simulated news articles
        return [
            {
                "title": f"{company_name} {keywords[0]} announcement",
                "description": f"{company_name} recently made an announcement regarding {keywords[0]}",
                "url": f"https://example.com/news/{company_name.lower().replace(' ', '-')}",
                "publishedAt": datetime.now().isoformat(),
                "source": {"name": "TechCrunch"}
            }
        ]
    
    async def _simulate_hiring_detection(self, company: Company) -> Dict[str, Any]:
        """Simulate hiring detection"""
        await asyncio.sleep(0.3)
        
        # Simulate hiring surge for some companies
        if hash(company.name) % 3 == 0:  # Arbitrary condition for demo
            return {
                "hiring_surge": True,
                "new_positions": 15,
                "departments": ["engineering", "sales", "marketing"],
                "impact_score": 70.0
            }
        
        return {"hiring_surge": False}
    
    # Helper methods for extracting information from text
    def _extract_funding_amount(self, text: str) -> Optional[str]:
        """Extract funding amount from text"""
        import re
        
        # Look for patterns like "$10M", "$5.2 million", etc.
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(?:million|M)',
            r'\$(\d+(?:\.\d+)?)\s*(?:billion|B)',
            r'\$(\d+(?:,\d{3})*(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_funding_stage(self, text: str) -> Optional[str]:
        """Extract funding stage from text"""
        text_lower = text.lower()
        
        stages = ["seed", "series a", "series b", "series c", "series d", "ipo", "acquisition"]
        for stage in stages:
            if stage in text_lower:
                return stage
        
        return None
    
    def _extract_leadership_info(self, text: str) -> Dict[str, Any]:
        """Extract leadership information from text"""
        # This would use NLP to extract names, roles, and change types
        # For now, return basic info
        return {
            "role": "executive",
            "name": "Unknown",
            "change_type": "hired"
        }
    
    def _extract_product_info(self, text: str) -> Dict[str, Any]:
        """Extract product information from text"""
        return {
            "name": "New Product",
            "type": "software",
            "stage": "launch"
        }
    
    def _extract_partnership_info(self, text: str) -> Dict[str, Any]:
        """Extract partnership information from text"""
        return {
            "partner": "Partner Company",
            "type": "strategic"
        }
    
    def _extract_expansion_info(self, text: str) -> Dict[str, Any]:
        """Extract expansion information from text"""
        return {
            "type": "geographic",
            "location": "New Market"
        }
    
    # Scoring methods
    def _calculate_funding_relevance(self, article: Dict, funding_amount: Optional[str]) -> float:
        """Calculate relevance score for funding signals"""
        base_score = 70.0
        
        if funding_amount:
            base_score += 20.0
        
        # Check title relevance
        title = article.get("title", "").lower()
        if any(word in title for word in ["funding", "investment", "raised", "series"]):
            base_score += 10.0
        
        return min(base_score, 100.0)
    
    def _calculate_funding_impact(self, funding_amount: Optional[str], funding_stage: Optional[str]) -> float:
        """Calculate impact score for funding signals"""
        base_score = 60.0
        
        if funding_amount:
            # Extract numeric value for impact calculation
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', funding_amount)
            if numbers:
                amount = float(numbers[0])
                if "million" in funding_amount.lower() or "M" in funding_amount:
                    if amount >= 50:
                        base_score += 30.0
                    elif amount >= 10:
                        base_score += 20.0
                    else:
                        base_score += 10.0
                elif "billion" in funding_amount.lower() or "B" in funding_amount:
                    base_score += 40.0
        
        return min(base_score, 100.0)
    
    def _calculate_leadership_relevance(self, article: Dict, leadership_info: Dict) -> float:
        """Calculate relevance score for leadership signals"""
        return 65.0  # Base score for leadership changes
    
    def _calculate_leadership_impact(self, leadership_info: Dict) -> float:
        """Calculate impact score for leadership signals"""
        role = leadership_info.get("role", "").lower()
        
        if any(title in role for title in ["ceo", "cto", "cfo", "founder"]):
            return 85.0
        elif "vp" in role or "vice president" in role:
            return 70.0
        elif "director" in role:
            return 55.0
        else:
            return 40.0
    
    def _calculate_product_relevance(self, article: Dict, product_info: Dict) -> float:
        """Calculate relevance score for product signals"""
        return 60.0
    
    def _calculate_product_impact(self, product_info: Dict) -> float:
        """Calculate impact score for product signals"""
        return 65.0
    
    def _calculate_partnership_relevance(self, article: Dict, partnership_info: Dict) -> float:
        """Calculate relevance score for partnership signals"""
        return 55.0
    
    def _calculate_partnership_impact(self, partnership_info: Dict) -> float:
        """Calculate impact score for partnership signals"""
        return 60.0
    
    def _calculate_expansion_relevance(self, article: Dict, expansion_info: Dict) -> float:
        """Calculate relevance score for expansion signals"""
        return 70.0
    
    def _calculate_expansion_impact(self, expansion_info: Dict) -> float:
        """Calculate impact score for expansion signals"""
        return 75.0
    
    def _calculate_timing_score(self, published_at: Optional[str]) -> float:
        """Calculate timing score based on how recent the signal is"""
        if not published_at:
            return 50.0
        
        try:
            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            days_ago = (datetime.now(published_date.tzinfo) - published_date).days
            
            if days_ago <= 1:
                return 100.0
            elif days_ago <= 7:
                return 90.0
            elif days_ago <= 30:
                return 75.0
            elif days_ago <= 90:
                return 50.0
            else:
                return 25.0
                
        except Exception:
            return 50.0
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return datetime.now()
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now()


# Global signal detection service instance
signal_detection_service = SignalDetectionService()