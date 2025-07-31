"""
Influencer Discovery App - Main Entry Point

Main script for running the influencer discovery and analysis system.
Supports various platforms and analysis modes.
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

# Import scrapers
from src.scrapers import InstagramScraper, TwitterScraper
from src.agents import BrandMatchingAgent
from src.database.models import Influencer, Brand, PlatformEnum, CategoryEnum

# Import existing LLM infrastructure
from src.llm.llm_config import get_llm_config
from src.utils.logger import setup_logger

console = Console()
logger = logging.getLogger(__name__)

class InfluencerDiscoveryApp:
    """Main application class for influencer discovery"""
    
    def __init__(self):
        """Initialize the application"""
        self.scrapers = {}
        self.agents = {}
        self.setup_scrapers()
        self.setup_agents()
    
    def setup_scrapers(self):
        """Initialize social media scrapers"""
        try:
            # Instagram scraper
            instagram_username = None  # Add Instagram credentials if available
            instagram_password = None
            self.scrapers['instagram'] = InstagramScraper(
                username=instagram_username,
                password=instagram_password,
                rate_limit=2.0
            )
            
            # Twitter scraper
            twitter_bearer_token = None  # Add Twitter API token if available
            self.scrapers['twitter'] = TwitterScraper(
                bearer_token=twitter_bearer_token,
                rate_limit=1.0
            )
            
            logger.info("Scrapers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing scrapers: {e}")
    
    def setup_agents(self):
        """Initialize AI agents"""
        try:
            # Brand matching agent
            self.agents['brand_matching'] = BrandMatchingAgent()
            
            logger.info("AI agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI agents: {e}")
    
    async def discover_influencers(self, 
                                 platform: str,
                                 keyword: str,
                                 min_followers: int = 1000,
                                 max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Discover influencers on a platform
        
        Args:
            platform: Social media platform
            keyword: Search keyword/hashtag
            min_followers: Minimum follower count
            max_results: Maximum results to return
            
        Returns:
            List of discovered influencer profiles
        """
        if platform not in self.scrapers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        scraper = self.scrapers[platform]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Discovering influencers on {platform}...", total=None)
            
            try:
                influencers = scraper.search_influencers(
                    keyword=keyword,
                    min_followers=min_followers,
                    max_results=max_results
                )
                
                progress.update(task, description=f"Found {len(influencers)} influencers")
                
                return [inf.__dict__ for inf in influencers]
                
            except Exception as e:
                logger.error(f"Error discovering influencers: {e}")
                return []
    
    async def analyze_influencer(self, username: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a specific influencer
        
        Args:
            username: Influencer username
            platform: Social media platform
            
        Returns:
            Influencer analysis results
        """
        if platform not in self.scrapers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        scraper = self.scrapers[platform]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing @{username}...", total=None)
            
            try:
                # Get profile data
                profile = scraper.get_profile(username)
                if not profile:
                    console.print(f"[red]Profile @{username} not found on {platform}[/red]")
                    return None
                
                progress.update(task, description=f"Profile loaded, analyzing content...")
                
                # Convert to dict for analysis
                profile_dict = profile.__dict__
                
                return profile_dict
                
            except Exception as e:
                logger.error(f"Error analyzing influencer: {e}")
                return None
    
    async def match_with_brand(self, 
                             influencers: List[Dict[str, Any]], 
                             brand_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Match influencers with a brand
        
        Args:
            influencers: List of influencer profiles
            brand_data: Brand requirements and preferences
            
        Returns:
            List of matching results
        """
        if 'brand_matching' not in self.agents:
            logger.error("Brand matching agent not available")
            return []
        
        agent = self.agents['brand_matching']
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Matching influencers with brand...", total=len(influencers))
            
            matches = []
            
            for i, influencer in enumerate(influencers):
                try:
                    # Analyze brand-influencer match
                    result = agent.analyze({
                        'influencer': influencer,
                        'brand': brand_data
                    })
                    
                    match_data = {
                        'influencer': influencer,
                        'match_analysis': result.analysis_data,
                        'confidence': result.confidence_score
                    }
                    
                    matches.append(match_data)
                    
                    progress.update(task, advance=1, 
                                  description=f"Analyzed {i+1}/{len(influencers)} influencers")
                    
                except Exception as e:
                    logger.error(f"Error matching influencer {influencer.get('username', 'unknown')}: {e}")
                    continue
            
            # Sort by overall match score
            matches.sort(key=lambda x: x['match_analysis'].get('overall_score', 0), reverse=True)
            
            return matches
    
    def display_influencer_results(self, influencers: List[Dict[str, Any]]):
        """Display influencer discovery results"""
        if not influencers:
            console.print("[yellow]No influencers found[/yellow]")
            return
        
        table = Table(title="Discovered Influencers")
        table.add_column("Username", style="cyan")
        table.add_column("Platform", style="magenta")
        table.add_column("Followers", style="green", justify="right")
        table.add_column("Engagement", style="blue", justify="right")
        table.add_column("Category", style="yellow")
        table.add_column("Verified", style="red")
        
        for inf in influencers[:20]:  # Show top 20
            table.add_row(
                f"@{inf.get('username', 'N/A')}",
                inf.get('platform', 'N/A').title(),
                f"{inf.get('follower_count', 0):,}",
                f"{inf.get('engagement_rate', 0):.2f}%",
                inf.get('category', 'N/A').title(),
                "✓" if inf.get('verified', False) else "✗"
            )
        
        console.print(table)
    
    def display_matching_results(self, matches: List[Dict[str, Any]]):
        """Display brand matching results"""
        if not matches:
            console.print("[yellow]No matches found[/yellow]")
            return
        
        table = Table(title="Brand-Influencer Matches")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("Username", style="cyan")
        table.add_column("Overall Score", style="green", justify="right")
        table.add_column("Audience", style="blue", justify="right")
        table.add_column("Engagement", style="yellow", justify="right")
        table.add_column("Brand Safety", style="red", justify="right")
        table.add_column("Est. Cost", style="magenta", justify="right")
        
        for i, match in enumerate(matches[:10], 1):  # Show top 10
            analysis = match['match_analysis']
            influencer = match['influencer']
            
            table.add_row(
                str(i),
                f"@{influencer.get('username', 'N/A')}",
                f"{analysis.get('overall_score', 0):.1f}",
                f"{analysis.get('audience_score', 0):.1f}",
                f"{analysis.get('engagement_score', 0):.1f}",
                f"{analysis.get('brand_safety_score', 0):.1f}",
                f"${analysis.get('estimated_cost', 0):,.0f}"
            )
        
        console.print(table)
        
        # Show detailed analysis for top match
        if matches:
            top_match = matches[0]
            self.display_detailed_match(top_match)
    
    def display_detailed_match(self, match: Dict[str, Any]):
        """Display detailed analysis for a match"""
        analysis = match['match_analysis']
        influencer = match['influencer']
        
        # Create detailed panel
        details = f"""
[bold]Influencer:[/bold] @{influencer.get('username', 'N/A')}
[bold]Platform:[/bold] {influencer.get('platform', 'N/A').title()}
[bold]Followers:[/bold] {influencer.get('follower_count', 0):,}
[bold]Engagement Rate:[/bold] {influencer.get('engagement_rate', 0):.2f}%

[bold]Match Scores:[/bold]
• Overall: {analysis.get('overall_score', 0):.1f}/100
• Category Alignment: {analysis.get('category_score', 0):.1f}/100
• Audience Fit: {analysis.get('audience_score', 0):.1f}/100
• Engagement Quality: {analysis.get('engagement_score', 0):.1f}/100

[bold]Estimated Performance:[/bold]
• Reach: {analysis.get('estimated_reach', 0):,}
• Engagement: {analysis.get('estimated_engagement', 0):,}
• Cost: ${analysis.get('estimated_cost', 0):,.0f}
• ROI: {analysis.get('roi_prediction', 0):.1f}%

[bold]Strengths:[/bold]
{chr(10).join(f"• {strength}" for strength in analysis.get('match_strengths', []))}

[bold]Potential Concerns:[/bold]
{chr(10).join(f"• {concern}" for concern in analysis.get('potential_concerns', []))}
"""
        
        console.print(Panel(details, title="Top Match Analysis", expand=False))

async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Influencer Discovery App")
    parser.add_argument("--platform", choices=["instagram", "twitter"], 
                       default="instagram", help="Social media platform")
    parser.add_argument("--keyword", required=True, 
                       help="Search keyword or hashtag")
    parser.add_argument("--min-followers", type=int, default=1000,
                       help="Minimum follower count")
    parser.add_argument("--max-results", type=int, default=50,
                       help="Maximum number of results")
    parser.add_argument("--analyze-user", 
                       help="Analyze specific user instead of searching")
    parser.add_argument("--brand-match", 
                       help="JSON file with brand requirements for matching")
    parser.add_argument("--show-reasoning", action="store_true",
                       help="Show detailed AI reasoning")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(show_reasoning=args.show_reasoning)
    
    # Initialize app
    app = InfluencerDiscoveryApp()
    
    try:
        if args.analyze_user:
            # Analyze specific user
            console.print(f"[bold]Analyzing @{args.analyze_user} on {args.platform}[/bold]")
            
            result = await app.analyze_influencer(args.analyze_user, args.platform)
            if result:
                app.display_influencer_results([result])
        else:
            # Discover influencers
            console.print(f"[bold]Discovering influencers for '{args.keyword}' on {args.platform}[/bold]")
            
            influencers = await app.discover_influencers(
                platform=args.platform,
                keyword=args.keyword,
                min_followers=args.min_followers,
                max_results=args.max_results
            )
            
            if influencers:
                app.display_influencer_results(influencers)
                
                # Brand matching if requested
                if args.brand_match:
                    try:
                        with open(args.brand_match, 'r') as f:
                            brand_data = json.load(f)
                        
                        console.print(f"\n[bold]Matching with brand: {brand_data.get('name', 'Unknown')}[/bold]")
                        
                        matches = await app.match_with_brand(influencers, brand_data)
                        if matches:
                            app.display_matching_results(matches)
                            
                    except Exception as e:
                        logger.error(f"Error loading brand data: {e}")
            else:
                console.print("[red]No influencers found. Try different keywords or lower follower threshold.[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        logger.error(f"Application error: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
