"""
Brand Matching Agent

AI agent that matches influencers with brands based on audience alignment,
content quality, engagement metrics, and brand values.
"""

from typing import Dict, List, Optional, Any
import json
import logging

from .base_agent import BaseAgent, AnalysisResult

logger = logging.getLogger(__name__)

class BrandMatchingAgent(BaseAgent):
    """AI agent for matching influencers with brands"""
    
    @property
    def agent_name(self) -> str:
        return "Brand Matching Agent"
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert brand marketing strategist specializing in influencer partnerships. 
Your role is to analyze influencer profiles and brand requirements to determine compatibility and predict campaign success.

You have deep expertise in:
- Audience demographics and psychographics analysis
- Brand positioning and values alignment
- Content style and aesthetic matching
- Engagement quality assessment
- ROI prediction for influencer campaigns
- Risk assessment for brand safety

When analyzing influencer-brand matches, consider:
1. Audience Alignment: How well does the influencer's audience match the brand's target demographic?
2. Content Quality: Is the content style and quality appropriate for the brand?
3. Values Alignment: Do the influencer's values and messaging align with the brand's values?
4. Engagement Quality: Is the engagement authentic and meaningful?
5. Brand Safety: Are there any potential risks or controversies?
6. Performance Potential: What's the predicted campaign performance?

Always provide detailed reasoning for your recommendations and assign confidence scores based on data quality and alignment strength.

Respond with structured JSON containing your analysis."""
    
    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze brand-influencer compatibility
        
        Args:
            data: Dictionary containing:
                - influencer: Influencer profile data
                - brand: Brand requirements and preferences
                - campaign_type: Type of campaign (optional)
                
        Returns:
            AnalysisResult with matching scores and recommendations
        """
        if not self.validate_input(data):
            raise ValueError("Invalid input data for brand matching analysis")
        
        # Preprocess the data
        processed_data = self.preprocess_data(data)
        
        # Create analysis prompt
        prompt = self._create_matching_prompt(processed_data)
        
        # Get LLM response
        response = self._call_llm(prompt)
        
        # Parse response
        analysis_data = self._parse_json_response(response)
        
        # Postprocess results
        analysis_data = self.postprocess_results(analysis_data)
        
        return self._create_analysis_result(analysis_data, response)
    
    def _create_matching_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for brand matching analysis"""
        
        influencer = data.get('influencer', {})
        brand = data.get('brand', {})
        campaign_type = data.get('campaign_type', 'general')
        
        prompt = f"""
Analyze the compatibility between this influencer and brand for a {campaign_type} campaign:

INFLUENCER PROFILE:
Username: {influencer.get('username', 'N/A')}
Platform: {influencer.get('platform', 'N/A')}
Followers: {influencer.get('follower_count', 0):,}
Engagement Rate: {influencer.get('engagement_rate', 0):.2f}%
Category: {influencer.get('category', 'N/A')}
Bio: {influencer.get('bio', 'N/A')}
Location: {influencer.get('location', 'N/A')}
Verified: {influencer.get('verified', False)}
Average Likes: {influencer.get('average_likes', 0):,}
Average Comments: {influencer.get('average_comments', 0):,}
Top Hashtags: {json.dumps(influencer.get('top_hashtags', []))}
Authenticity Score: {influencer.get('authenticity_score', 0):.1f}/100
Content Quality Score: {influencer.get('content_quality_score', 0):.1f}/100
Brand Safety Score: {influencer.get('brand_safety_score', 0):.1f}/100

RECENT POSTS SAMPLE:
{self._format_posts_data(influencer.get('posts', [])[:5])}

BRAND REQUIREMENTS:
Name: {brand.get('name', 'N/A')}
Industry: {brand.get('industry', 'N/A')}
Description: {brand.get('description', 'N/A')}
Target Categories: {json.dumps(brand.get('target_categories', []))}
Min Followers: {brand.get('min_followers', 0):,}
Max Followers: {brand.get('max_followers', 'No limit')}
Min Engagement Rate: {brand.get('min_engagement_rate', 0):.1f}%
Target Demographics: {json.dumps(brand.get('target_demographics', {}))}
Budget Range: {json.dumps(brand.get('budget_range', {}))}
Brand Values: {json.dumps(brand.get('brand_values', []))}

Please provide a comprehensive analysis in the following JSON format:
{{
    "overall_score": <0-100 overall compatibility score>,
    "category_score": <0-100 category alignment score>,
    "audience_score": <0-100 audience alignment score>,
    "engagement_score": <0-100 engagement quality score>,
    "authenticity_score": <0-100 authenticity assessment>,
    "brand_safety_score": <0-100 brand safety assessment>,
    "estimated_reach": <estimated campaign reach>,
    "estimated_engagement": <estimated campaign engagement>,
    "estimated_cost": <estimated campaign cost in USD>,
    "roi_prediction": <predicted ROI as percentage>,
    "match_strengths": [<list of key strengths>],
    "potential_concerns": [<list of potential issues>],
    "recommended_content_types": [<list of recommended content formats>],
    "campaign_strategy": "<recommended campaign approach>",
    "negotiation_points": [<list of key negotiation considerations>],
    "success_probability": <0-100 probability of campaign success>,
    "confidence_score": <0-100 confidence in this analysis>
}}
"""
        return prompt
    
    def _format_posts_data(self, posts: List[Dict[str, Any]]) -> str:
        """Format posts data for prompt"""
        if not posts:
            return "No recent posts available"
        
        formatted_posts = []
        for i, post in enumerate(posts[:5], 1):
            post_info = f"""
Post {i}:
- Caption: {post.get('caption', 'N/A')[:200]}{'...' if len(post.get('caption', '')) > 200 else ''}
- Likes: {post.get('likes_count', 0):,}
- Comments: {post.get('comments_count', 0):,}
- Type: {post.get('post_type', 'N/A')}
- Hashtags: {json.dumps(post.get('hashtags', [])[:5])}
- Posted: {post.get('posted_at', 'N/A')}
"""
            formatted_posts.append(post_info)
        
        return "\n".join(formatted_posts)
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for brand matching"""
        if not isinstance(data, dict):
            return False
        
        # Check for required fields
        required_fields = ['influencer', 'brand']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate influencer data
        influencer = data.get('influencer', {})
        if not isinstance(influencer, dict) or 'username' not in influencer:
            logger.error("Invalid influencer data")
            return False
        
        # Validate brand data
        brand = data.get('brand', {})
        if not isinstance(brand, dict) or 'name' not in brand:
            logger.error("Invalid brand data")
            return False
        
        return True
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for brand matching"""
        return [
            'influencer.username',
            'influencer.platform', 
            'influencer.follower_count',
            'influencer.engagement_rate',
            'influencer.category',
            'brand.name',
            'brand.industry',
            'brand.target_categories'
        ]
    
    def preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess data for analysis"""
        processed = data.copy()
        
        # Ensure numeric fields are properly formatted
        influencer = processed.get('influencer', {})
        for field in ['follower_count', 'following_count', 'post_count', 'engagement_rate', 
                     'average_likes', 'average_comments', 'authenticity_score', 
                     'content_quality_score', 'brand_safety_score']:
            if field in influencer and influencer[field] is None:
                influencer[field] = 0
        
        # Ensure lists are properly formatted
        for field in ['top_hashtags', 'posts']:
            if field in influencer and not isinstance(influencer[field], list):
                influencer[field] = []
        
        # Process brand data
        brand = processed.get('brand', {})
        for field in ['target_categories', 'target_demographics', 'budget_range', 'brand_values']:
            if field in brand and not isinstance(brand[field], (list, dict)):
                if field in ['target_categories', 'brand_values']:
                    brand[field] = []
                else:
                    brand[field] = {}
        
        return processed
    
    def postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess analysis results"""
        if 'error' in results:
            return results
        
        # Ensure all scores are within valid ranges
        score_fields = ['overall_score', 'category_score', 'audience_score', 
                       'engagement_score', 'authenticity_score', 'brand_safety_score',
                       'roi_prediction', 'success_probability', 'confidence_score']
        
        for field in score_fields:
            if field in results:
                try:
                    score = float(results[field])
                    results[field] = max(0, min(100, score))
                except (ValueError, TypeError):
                    results[field] = 0
        
        # Ensure numeric fields are properly formatted
        numeric_fields = ['estimated_reach', 'estimated_engagement', 'estimated_cost']
        for field in numeric_fields:
            if field in results:
                try:
                    results[field] = max(0, float(results[field]))
                except (ValueError, TypeError):
                    results[field] = 0
        
        # Ensure list fields are properly formatted
        list_fields = ['match_strengths', 'potential_concerns', 'recommended_content_types', 'negotiation_points']
        for field in list_fields:
            if field in results and not isinstance(results[field], list):
                results[field] = []
        
        return results
    
    def calculate_compatibility_matrix(self, 
                                     influencers: List[Dict[str, Any]], 
                                     brand: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate compatibility scores for multiple influencers against a brand
        
        Args:
            influencers: List of influencer profiles
            brand: Brand requirements
            
        Returns:
            List of compatibility results sorted by overall score
        """
        results = []
        
        for influencer in influencers:
            try:
                analysis = self.analyze({
                    'influencer': influencer,
                    'brand': brand
                })
                
                result = {
                    'influencer_id': influencer.get('id'),
                    'username': influencer.get('username'),
                    'analysis': analysis.analysis_data
                }
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error analyzing influencer {influencer.get('username', 'unknown')}: {e}")
                continue
        
        # Sort by overall score
        results.sort(key=lambda x: x['analysis'].get('overall_score', 0), reverse=True)
        
        return results