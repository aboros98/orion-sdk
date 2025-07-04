"""
Market Intelligence Agent - Real-world business research and competitive analysis
Helps businesses make informed decisions through comprehensive market research and analysis.
"""

import os
import asyncio
import json
import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from orion.agent_core import create_orchestrator, build_async_agent
from orion.agent_core.utils import function_to_schema
from orion.graph_core import WorkflowGraph
from orion.tool_registry import tool


# Market Intelligence Tools
@tool
def conduct_competitive_analysis(company_name: str, industry: str, competitors: List[str]) -> Dict[str, Any]:
    """
    Conduct comprehensive competitive analysis with market positioning and strategic insights.
    
    This tool performs detailed competitive analysis including market share assessment,
    competitor profiling, SWOT analysis, and strategic recommendations for business planning.
    
    Args:
        company_name (str): Name of the company conducting the analysis (your company).
                          Used for context and positioning in the competitive landscape.
                          Examples: "TechCorp", "StartupXYZ", "Enterprise Solutions Inc."
        industry (str): Industry or market segment being analyzed. Should be specific
                       to focus the competitive analysis effectively.
                       Examples: "SaaS", "E-commerce", "Healthcare Technology", "Fintech"
        competitors (List[str]): List of competitor company names to analyze.
                               Should include direct competitors and market leaders.
                               Minimum recommended: 3-5 competitors for comprehensive analysis.
                               Examples: ["Competitor A", "Market Leader B", "Startup C"]
    
    Returns:
        Dict[str, Any]: Comprehensive competitive analysis including:
            - target_company: Company conducting the analysis
            - industry: Target industry for analysis
            - analysis_date: When the analysis was performed
            - competitor_profiles: Detailed profiles of each competitor with strengths/weaknesses
            - competitive_landscape: Market leaders, emerging players, and market gaps
            - strategic_recommendations: Actionable recommendations for competitive positioning
            - threat_level: Assessment of competitive threat level
    
    Example:
        >>> competitors = ["Microsoft", "Google", "Amazon"]
        >>> result = conduct_competitive_analysis("TechCorp", "Cloud Computing", competitors)
        >>> print(result['threat_level'])
        'Medium-High'
    """
    try:
        # Simulate competitive research data (in real implementation, would use APIs and web scraping)
        analysis_results: Dict[str, Any] = {
            "target_company": company_name,
            "industry": industry,
            "analysis_date": datetime.now().isoformat(),
            "competitor_profiles": []
        }
        
        # Sample competitive metrics
        metrics = ["market_share", "revenue_growth", "employee_count", "funding", "product_range"]
        
        for competitor in competitors:
            # Simulate competitor data collection
            competitor_profile = {
                "name": competitor,
                "market_position": "Strong" if len(competitor) > 8 else "Moderate",
                "strengths": [
                    "Strong brand recognition",
                    "Diverse product portfolio",
                    "Global presence"
                ][:2],
                "weaknesses": [
                    "Higher pricing",
                    "Slower innovation",
                    "Limited market penetration"
                ][:2],
                "estimated_market_share": f"{15 + (len(competitor) % 20)}%",
                "key_products": [f"{competitor} Product A", f"{competitor} Service B"],
                "recent_developments": [
                    f"{competitor} launched new product line",
                    f"{competitor} expanded to new market"
                ]
            }
            analysis_results["competitor_profiles"].append(competitor_profile)
        
        # Market position analysis
        competitive_landscape = {
            "market_leaders": competitors[:2] if len(competitors) >= 2 else competitors,
            "emerging_players": competitors[2:] if len(competitors) > 2 else [],
            "market_gaps": [
                "Affordable premium segment",
                "SMB market underserved",
                "Emerging market opportunities"
            ],
            "competitive_intensity": "High" if len(competitors) > 4 else "Moderate"
        }
        
        # Strategic recommendations
        recommendations = [
            f"Differentiate from {competitors[0]} through pricing strategy" if competitors else "Focus on unique value proposition",
            "Leverage technology for competitive advantage",
            "Consider strategic partnerships to expand market reach",
            "Invest in customer experience improvements"
        ]
        
        analysis_results["competitive_landscape"] = competitive_landscape
        analysis_results["strategic_recommendations"] = recommendations
        analysis_results["threat_level"] = "Medium-High" if len(competitors) > 3 else "Medium"
        
        return analysis_results
        
    except Exception as e:
        return {"error": f"Competitive analysis error: {str(e)}"}


@tool
def analyze_market_trends(industry: str, time_period: str = "12_months", focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze market trends, growth opportunities, and industry dynamics for strategic planning.
    
    This tool provides comprehensive market trend analysis including growth metrics, trend insights,
    SWOT analysis, and investment climate assessment to inform business strategy decisions.
    
    Args:
        industry (str): Industry or market segment to analyze. Should be specific for accurate trend analysis.
                       Examples: "Technology", "Healthcare", "E-commerce", "Fintech", "Manufacturing"
        time_period (str, optional): Time period for trend analysis. 
                                   Options: "6_months", "12_months", "24_months", "5_years".
                                   Default is "12_months".
        focus_areas (Optional[List[str]], optional): Specific areas to focus the analysis on.
                                                    If None, analyzes all major areas.
                                                    Options: ["technology", "consumer_behavior", 
                                                            "regulations", "economic_factors"].
                                                    Default is None (analyzes all areas).
    
    Returns:
        Dict[str, Any]: Comprehensive market trend analysis including:
            - industry: Target industry analyzed
            - analysis_period: Time period covered
            - report_date: When the analysis was performed
            - overall_market_health: Overall market condition assessment
            - market_metrics: Market size, growth rate, and maturity indicators
            - trend_insights: Detailed trends by focus area with impact levels and timelines
            - swot_analysis: Opportunities and threats identification
            - investment_climate: Funding availability, investor sentiment, and valuation trends
    
    Example:
        >>> focus = ["technology", "consumer_behavior"]
        >>> result = analyze_market_trends("E-commerce", "24_months", focus)
        >>> print(result['overall_market_health'])
        'Growing'
    """
    try:
        if focus_areas is None:
            focus_areas = ["technology", "consumer_behavior", "regulations", "economic_factors"]
        
        # Simulate market trend analysis
        trend_analysis: Dict[str, Any] = {
            "industry": industry,
            "analysis_period": time_period,
            "report_date": datetime.now().isoformat(),
            "overall_market_health": "Growing" if "tech" in industry.lower() else "Stable"
        }
        
        # Market size and growth
        market_metrics = {
            "estimated_market_size": f"${50 + (len(industry) * 5)}B",
            "growth_rate": f"{3 + (len(industry) % 8)}% CAGR",
            "market_maturity": "Growth" if len(industry) < 10 else "Mature",
            "key_growth_drivers": [
                "Digital transformation acceleration",
                "Changing consumer preferences",
                "Regulatory changes"
            ]
        }
        
        # Trend analysis by focus area
        trend_insights = {}
        for area in focus_areas:
            if area == "technology":
                trend_insights[area] = {
                    "key_trends": [
                        "AI and automation adoption",
                        "Cloud migration acceleration",
                        "Data privacy emphasis"
                    ],
                    "impact_level": "High",
                    "timeline": "1-2 years"
                }
            elif area == "consumer_behavior":
                trend_insights[area] = {
                    "key_trends": [
                        "Sustainability focus increasing",
                        "Remote work normalization",
                        "Digital-first expectations"
                    ],
                    "impact_level": "High",
                    "timeline": "Immediate"
                }
            elif area == "regulations":
                trend_insights[area] = {
                    "key_trends": [
                        "Data protection requirements",
                        "ESG compliance mandates",
                        "Industry-specific regulations"
                    ],
                    "impact_level": "Medium",
                    "timeline": "6-18 months"
                }
            else:
                trend_insights[area] = {
                    "key_trends": [
                        "Economic uncertainty impact",
                        "Supply chain resilience focus",
                        "Investment pattern shifts"
                    ],
                    "impact_level": "Medium",
                    "timeline": "3-12 months"
                }
        
        # Opportunities and threats
        swot_analysis = {
            "opportunities": [
                "Emerging market expansion",
                "Technology adoption gap",
                "Sustainability solutions demand",
                "Partnership possibilities"
            ],
            "threats": [
                "Increased competition",
                "Economic volatility",
                "Regulatory changes",
                "Technology disruption"
            ]
        }
        
        # Investment insights
        investment_climate = {
            "funding_availability": "Moderate" if "startup" in industry.lower() else "Good",
            "investor_sentiment": "Cautiously optimistic",
            "hot_sectors": ["AI/ML", "Sustainability", "Healthcare", "Fintech"],
            "valuation_trends": "Normalizing after high growth period"
        }
        
        trend_analysis["market_metrics"] = market_metrics
        trend_analysis["trend_insights"] = trend_insights
        trend_analysis["swot_analysis"] = swot_analysis
        trend_analysis["investment_climate"] = investment_climate
        
        return trend_analysis
        
    except Exception as e:
        return {"error": f"Market trend analysis error: {str(e)}"}


@tool
def assess_customer_segments(industry: str, target_market: str, business_model: str) -> Dict[str, Any]:
    """
    Analyze customer segments, market opportunities, and penetration strategies for business development.
    
    This tool provides detailed customer segmentation analysis including segment characteristics,
    pain points, market size, growth potential, and strategic recommendations for targeting.
    
    Args:
        industry (str): Industry or market sector being analyzed. Affects customer segment characteristics
                       and market dynamics.
                       Examples: "Technology", "Healthcare", "Retail", "Financial Services"
        target_market (str): Specific market or geographic region to focus on. Can be broad or specific.
                            Examples: "North America", "SMB market", "Enterprise customers", "Urban consumers"
        business_model (str): Business model type that determines customer segment structure.
                             Options: "B2B" (Business-to-Business), "B2C" (Business-to-Consumer).
                             Affects segmentation approach and customer characteristics.
    
    Returns:
        Dict[str, Any]: Comprehensive customer segment analysis including:
            - industry: Target industry for analysis
            - target_market: Specific market focus
            - business_model: B2B or B2C model used
            - analysis_date: When the analysis was performed
            - customer_segments: Detailed segment profiles with characteristics and pain points
            - penetration_analysis: Current market penetration and untapped opportunities
            - segment_recommendations: Strategic recommendations for segment targeting
    
    Example:
        >>> result = assess_customer_segments("SaaS", "Enterprise market", "B2B")
        >>> print(len(result['customer_segments']))
        3
    """
    try:
        # Customer segmentation analysis
        segment_analysis: Dict[str, Any] = {
            "industry": industry,
            "target_market": target_market,
            "business_model": business_model,
            "analysis_date": datetime.now().isoformat()
        }
        
        # Define customer segments based on business model
        if business_model.lower() == "b2b":
            customer_segments = {
                "enterprise": {
                    "size": "Large (1000+ employees)",
                    "characteristics": ["Complex needs", "Long sales cycles", "High value contracts"],
                    "pain_points": ["Integration challenges", "Scalability requirements", "Compliance needs"],
                    "market_size": "25% of total market",
                    "growth_potential": "Steady",
                    "acquisition_cost": "High"
                },
                "mid_market": {
                    "size": "Medium (100-1000 employees)",
                    "characteristics": ["Balanced needs", "Moderate complexity", "Growth-focused"],
                    "pain_points": ["Resource constraints", "Technology gaps", "Efficiency needs"],
                    "market_size": "45% of total market",
                    "growth_potential": "High",
                    "acquisition_cost": "Medium"
                },
                "small_business": {
                    "size": "Small (10-100 employees)",
                    "characteristics": ["Simple needs", "Price sensitive", "Quick decisions"],
                    "pain_points": ["Budget limitations", "Limited IT resources", "Time constraints"],
                    "market_size": "30% of total market",
                    "growth_potential": "Very High",
                    "acquisition_cost": "Low"
                }
            }
        else:  # B2C
            customer_segments = {
                "premium": {
                    "demographics": "High income, urban, 25-45 years",
                    "characteristics": ["Quality-focused", "Brand conscious", "Early adopters"],
                    "pain_points": ["Time constraints", "Quality concerns", "Status needs"],
                    "market_size": "20% of total market",
                    "growth_potential": "Moderate",
                    "acquisition_cost": "High"
                },
                "mainstream": {
                    "demographics": "Middle income, suburban, 30-55 years",
                    "characteristics": ["Value-conscious", "Practical", "Research-driven"],
                    "pain_points": ["Price vs quality balance", "Reliability needs", "Family considerations"],
                    "market_size": "60% of total market",
                    "growth_potential": "Steady",
                    "acquisition_cost": "Medium"
                },
                "budget_conscious": {
                    "demographics": "Lower-middle income, diverse locations, 18-65 years",
                    "characteristics": ["Price sensitive", "Necessity-focused", "Word-of-mouth driven"],
                    "pain_points": ["Affordability", "Value demonstration", "Trust building"],
                    "market_size": "20% of total market",
                    "growth_potential": "High",
                    "acquisition_cost": "Low"
                }
            }
        
        # Market penetration analysis
        penetration_analysis = {
            "current_penetration": "15-25% depending on segment",
            "saturation_level": "Low to Medium",
            "untapped_opportunities": [
                "Geographic expansion",
                "New customer segments",
                "Product line extension",
                "Channel diversification"
            ]
        }
        
        # Segment recommendations
        recommendations = []
        for segment_name, segment_data in customer_segments.items():
            if segment_data.get("growth_potential") == "High" or segment_data.get("growth_potential") == "Very High":
                recommendations.append(f"Prioritize {segment_name} segment for growth initiatives")
        
        recommendations.extend([
            "Develop segment-specific value propositions",
            "Tailor marketing messages by segment",
            "Consider different pricing strategies per segment"
        ])
        
        segment_analysis["customer_segments"] = customer_segments
        segment_analysis["penetration_analysis"] = penetration_analysis
        segment_analysis["segment_recommendations"] = recommendations
        
        return segment_analysis
        
    except Exception as e:
        return {"error": f"Customer segment analysis error: {str(e)}"}


@tool
def evaluate_market_entry_strategy(target_market: str, business_type: str, budget_range: str, timeline: str) -> Dict[str, Any]:
    """Evaluate market entry strategies for new business opportunities."""
    try:
        entry_analysis: Dict[str, Any] = {
            "target_market": target_market,
            "business_type": business_type,
            "budget_range": budget_range,
            "timeline": timeline,
            "analysis_date": datetime.now().isoformat()
        }
        
        # Market entry barriers analysis
        barriers = {
            "capital_requirements": "Medium" if "startup" in budget_range.lower() else "High",
            "regulatory_complexity": "High" if any(x in target_market.lower() for x in ["healthcare", "financial", "education"]) else "Medium",
            "competitive_intensity": "High" if "tech" in business_type.lower() else "Medium",
            "customer_acquisition_difficulty": "Medium",
            "technology_requirements": "High" if "tech" in business_type.lower() else "Low"
        }
        
        # Entry strategy options
        strategy_options = []
        
        # Direct entry
        strategy_options.append({
            "strategy": "Direct Market Entry",
            "description": "Establish operations directly in target market",
            "advantages": ["Full control", "Higher margins", "Brand building"],
            "disadvantages": ["High investment", "High risk", "Longer timeline"],
            "suitability": "High budget, long timeline",
            "risk_level": "High",
            "investment_required": "High"
        })
        
        # Partnership entry
        strategy_options.append({
            "strategy": "Strategic Partnership",
            "description": "Partner with established local players",
            "advantages": ["Reduced risk", "Local expertise", "Faster entry"],
            "disadvantages": ["Shared control", "Lower margins", "Dependency"],
            "suitability": "Medium budget, medium timeline",
            "risk_level": "Medium",
            "investment_required": "Medium"
        })
        
        # Licensing
        strategy_options.append({
            "strategy": "Licensing/Franchising",
            "description": "License business model to local operators",
            "advantages": ["Low investment", "Rapid scaling", "Local adaptation"],
            "disadvantages": ["Limited control", "Lower revenue", "Quality concerns"],
            "suitability": "Low budget, short timeline",
            "risk_level": "Low",
            "investment_required": "Low"
        })
        
        # Digital-first entry
        if "tech" in business_type.lower() or "digital" in business_type.lower():
            strategy_options.append({
                "strategy": "Digital-First Entry",
                "description": "Enter market through digital channels",
                "advantages": ["Low overhead", "Scalable", "Data-driven"],
                "disadvantages": ["Limited local presence", "Digital competition", "Customer trust"],
                "suitability": "Any budget, short timeline",
                "risk_level": "Medium",
                "investment_required": "Low-Medium"
            })
        
        # Success factors
        success_factors = [
            "Strong value proposition for local market",
            "Understanding of local regulations and culture",
            "Adequate funding and resource allocation",
            "Strong local partnerships or talent",
            "Adaptive business model",
            "Clear go-to-market strategy"
        ]
        
        # Risk mitigation strategies
        risk_mitigation = [
            "Conduct pilot program before full launch",
            "Secure local legal and regulatory expertise",
            "Build strong local partnerships",
            "Maintain financial reserves for unexpected costs",
            "Develop exit strategy if needed"
        ]
        
        # Recommended approach
        if budget_range.lower() == "high" and timeline == "long":
            recommended_strategy = "Direct Market Entry"
        elif budget_range.lower() == "medium":
            recommended_strategy = "Strategic Partnership"
        else:
            recommended_strategy = "Licensing/Franchising or Digital-First Entry"
        
        entry_analysis["market_barriers"] = barriers
        entry_analysis["strategy_options"] = strategy_options
        entry_analysis["recommended_strategy"] = recommended_strategy
        entry_analysis["success_factors"] = success_factors
        entry_analysis["risk_mitigation"] = risk_mitigation
        
        return entry_analysis
        
    except Exception as e:
        return {"error": f"Market entry analysis error: {str(e)}"}


@tool
def monitor_industry_intelligence(industry: str, monitoring_areas: List[str], alert_frequency: str = "weekly") -> Dict[str, Any]:
    """Set up ongoing industry intelligence monitoring for strategic insights."""
    try:
        intelligence_setup: Dict[str, Any] = {
            "industry": industry,
            "monitoring_areas": monitoring_areas,
            "alert_frequency": alert_frequency,
            "setup_date": datetime.now().isoformat()
        }
        
        # Define monitoring sources and methods
        monitoring_sources = {
            "news_sources": [
                f"{industry.title()} Weekly",
                "Business Intelligence Today",
                "Market Research Reports",
                "Industry Trade Publications"
            ],
            "data_sources": [
                "Financial databases",
                "Government statistics",
                "Patent databases",
                "Social media sentiment"
            ],
            "expert_networks": [
                "Industry associations",
                "Professional networks",
                "Analyst firms",
                "Academic institutions"
            ]
        }
        
        # Monitoring framework
        monitoring_framework = {}
        for area in monitoring_areas:
            if area.lower() == "competitors":
                monitoring_framework[area] = {
                    "metrics": ["Product launches", "Funding rounds", "Executive changes", "Market share shifts"],
                    "sources": ["Company websites", "Press releases", "SEC filings", "News alerts"],
                    "frequency": "Daily",
                    "alert_threshold": "Significant developments"
                }
            elif area.lower() == "market_trends":
                monitoring_framework[area] = {
                    "metrics": ["Market size", "Growth rates", "Technology adoption", "Consumer behavior"],
                    "sources": ["Market research", "Survey data", "Government reports", "Analyst reports"],
                    "frequency": "Weekly",
                    "alert_threshold": "Trend changes > 10%"
                }
            elif area.lower() == "regulations":
                monitoring_framework[area] = {
                    "metrics": ["New regulations", "Policy changes", "Compliance requirements", "Legal precedents"],
                    "sources": ["Government websites", "Legal databases", "Industry alerts", "Law firms"],
                    "frequency": "Weekly",
                    "alert_threshold": "New regulatory announcements"
                }
            elif area.lower() == "technology":
                monitoring_framework[area] = {
                    "metrics": ["Patent filings", "R&D investments", "Technology breakthroughs", "Startup funding"],
                    "sources": ["Patent databases", "Research publications", "Tech news", "Investment reports"],
                    "frequency": "Bi-weekly",
                    "alert_threshold": "Disruptive technology emergence"
                }
        
        # Intelligence deliverables
        deliverables = {
            "reports": {
                "executive_summary": f"Monthly {industry} Intelligence Brief",
                "detailed_analysis": f"Quarterly {industry} Market Analysis",
                "trend_forecast": f"Annual {industry} Trend Predictions",
                "competitive_update": f"Weekly Competitive Intelligence Report"
            },
            "alerts": {
                "urgent": "Same-day notification for critical developments",
                "important": f"{alert_frequency.title()} summary of key changes",
                "informational": "Monthly compilation of general industry news"
            }
        }
        
        # Success metrics
        success_metrics = [
            "Early identification of market opportunities",
            "Proactive response to competitive threats",
            "Informed strategic decision making",
            "Reduced market entry risks",
            "Improved market positioning"
        ]
        
        intelligence_setup["monitoring_sources"] = monitoring_sources
        intelligence_setup["monitoring_framework"] = monitoring_framework
        intelligence_setup["deliverables"] = deliverables
        intelligence_setup["success_metrics"] = success_metrics
        
        return intelligence_setup
        
    except Exception as e:
        return {"error": f"Industry intelligence setup error: {str(e)}"}


async def market_intelligence_agent(business_query: str) -> str:
    """Market intelligence agent that provides comprehensive business research and analysis."""
    try:
        # This would integrate with the orchestrator to analyze the query and route to appropriate tools
        return f"Processing market intelligence analysis for: {business_query}"
    except Exception as e:
        return f"Error in market intelligence analysis: {str(e)}"


class MarketIntelligenceAgent:
    """Real-world market intelligence agent for business research and competitive analysis."""
    
    def __init__(self):
        self.name = "MarketIntelligenceAgent"
        self.complexity_level = 6
        self.description = "Real-world market intelligence agent for competitive analysis, market trends, and business strategy"
    
    async def create_workflow(self) -> WorkflowGraph:
        """Create the market intelligence workflow."""
        try:
            api_key = os.environ.get("API_KEY", "")
            base_url = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                raise ValueError("API_KEY environment variable is required")
            
            # Create tools for different market intelligence domains
            competitive_tools = [
                await function_to_schema(conduct_competitive_analysis, func_name="conduct_competitive_analysis", enhance_description=True),
                await function_to_schema(monitor_industry_intelligence, func_name="monitor_industry_intelligence", enhance_description=True),
            ]
            
            market_analysis_tools = [
                await function_to_schema(analyze_market_trends, func_name="analyze_market_trends", enhance_description=True),
                await function_to_schema(assess_customer_segments, func_name="assess_customer_segments", enhance_description=True),
            ]
            
            strategy_tools = [
                await function_to_schema(evaluate_market_entry_strategy, func_name="evaluate_market_entry_strategy", enhance_description=True),
            ]
            
            # Create response agent
            response_agent = await function_to_schema(market_intelligence_agent, func_name="market_intelligence_agent", enhance_description=True)
            
            # Create main orchestrator with routing capability
            all_tools = competitive_tools + market_analysis_tools + strategy_tools + [response_agent]
            main_orchestrator = create_orchestrator(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=all_tools
            )
            
            # Create specialized LLM execution nodes
            competitive_analyst = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=competitive_tools
            )
            
            market_analyst = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=market_analysis_tools
            )
            
            strategy_consultant = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=strategy_tools
            )
            
            # Create workflow graph
            execution_graph = WorkflowGraph()
            
            # Add main orchestrator
            execution_graph.add_orchestrator_node("main_orchestrator", main_orchestrator)
            
            # Add LLM execution nodes
            execution_graph.add_node("competitive_analyst", competitive_analyst)
            execution_graph.add_node("market_analyst", market_analyst)
            execution_graph.add_node("strategy_consultant", strategy_consultant)
            
            # Add tool nodes
            execution_graph.add_node("competitive_analyzer", conduct_competitive_analysis)
            execution_graph.add_node("trend_analyzer", analyze_market_trends)
            execution_graph.add_node("segment_analyzer", assess_customer_segments)
            execution_graph.add_node("entry_strategy_evaluator", evaluate_market_entry_strategy)
            execution_graph.add_node("intelligence_monitor", monitor_industry_intelligence)
            
            # Connect orchestrator to specialized agents
            execution_graph.add_edge("__start__", "main_orchestrator")
            execution_graph.add_edge("main_orchestrator", "competitive_analyst")
            execution_graph.add_edge("main_orchestrator", "market_analyst")
            execution_graph.add_edge("main_orchestrator", "strategy_consultant")
            
            # Connect specialized agents to their tools
            execution_graph.add_edge("competitive_analyst", "competitive_analyzer")
            execution_graph.add_edge("competitive_analyst", "intelligence_monitor")
            execution_graph.add_edge("market_analyst", "trend_analyzer")
            execution_graph.add_edge("market_analyst", "segment_analyzer")
            execution_graph.add_edge("strategy_consultant", "entry_strategy_evaluator")
            
            # Add human interaction
            execution_graph.add_human_in_the_loop("main_orchestrator")
            
            return execution_graph
            
        except Exception as e:
            print(f"Error creating workflow: {e}")
            raise
    
    def get_real_world_scenarios(self) -> List[Dict[str, Any]]:
        """Get real-world market intelligence scenarios for business application."""
        return [
            {
                "scenario": "Tech startup competitive analysis",
                "prompt": "Analyze the competitive landscape for our AI-powered customer service platform. Main competitors are Zendesk, Intercom, and Freshworks. What's our market positioning?",
                "category": "competitive_analysis"
            },
            {
                "scenario": "E-commerce market expansion",
                "prompt": "We're an e-commerce platform considering expansion into Southeast Asian markets. Analyze market trends, customer segments, and entry strategies.",
                "category": "market_expansion"
            },
            {
                "scenario": "Fintech industry intelligence",
                "prompt": "Set up ongoing market intelligence monitoring for the digital payments industry, focusing on competitors, regulations, and technology trends.",
                "category": "industry_monitoring"
            },
            {
                "scenario": "SaaS customer segmentation",
                "prompt": "Analyze customer segments for our B2B project management SaaS targeting the construction industry. What segments should we prioritize?",
                "category": "customer_analysis"
            },
            {
                "scenario": "Healthcare market entry",
                "prompt": "Evaluate market entry strategies for our telemedicine platform in the European market. Budget is $2M, timeline is 18 months.",
                "category": "strategy_planning"
            }
        ]
    
    async def solve_real_world_problem(self, scenario: str) -> Dict[str, Any]:
        """Solve a real-world business intelligence problem."""
        try:
            workflow = await self.create_workflow()
            compiled_graph = workflow.compile()
            
            result = await compiled_graph.execute(initial_input=scenario)
            
            return {
                "agent": self.name,
                "scenario": scenario,
                "intelligence": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "scenario": scenario,
                "error": str(e),
                "status": "error"
            }


# Export the agent
__all__ = ["MarketIntelligenceAgent", "market_intelligence_agent"] 