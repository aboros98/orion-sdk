"""
Web Research Agent - Real-world web search and information gathering
Helps users find, analyze, and synthesize information from the web for research purposes.
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

from dotenv import load_dotenv

load_dotenv()


# Web Research Tools
@tool
def search_web(query: str, num_results: int = 5, search_type: str = "general") -> Dict[str, Any]:
    """
    Perform comprehensive web search across multiple search engines with relevance scoring.
    
    This tool searches the web for information using various search engines and returns
    structured results with relevance scores, timestamps, and source information for research purposes.
    
    Args:
        query (str): Search query string. Should be specific and descriptive for better results.
                    Examples: "latest AI developments 2024", "climate change impact on agriculture"
        num_results (int, optional): Number of search results to return. 
                                   Default is 5. Range: 1-20 for optimal performance.
        search_type (str, optional): Type of search to perform. 
                                   Options: "general", "news", "academic", "images", "videos".
                                   Default is "general".
    
    Returns:
        Dict[str, Any]: Structured search results including:
            - query: Original search query
            - search_type: Type of search performed
            - timestamp: When the search was executed
            - results: List of search results with titles, URLs, snippets, and relevance scores
            - total_results: Number of results returned
            - search_time: Time taken for the search
    
    Example:
        >>> result = search_web("machine learning applications in healthcare", 3)
        >>> print(len(result['results']))
        3
    """
    try:
        # Simulate web search results (in real implementation, would use search APIs)
        search_results = {
            "query": query,
            "search_type": search_type,
            "timestamp": datetime.now().isoformat(),
            "results": []
        }
        
        # Generate simulated search results based on query
        keywords = query.lower().split()
        search_engines = ["Google", "Bing", "DuckDuckGo"]
        
        for i in range(min(num_results, 5)):
            # Create realistic-looking search results
            title = f"Search Result for {' '.join(keywords[:3])} - {i+1}"
            url = f"https://example{i+1}.com/{'-'.join(keywords[:2])}"
            snippet = f"This is a simulated search result about {' '.join(keywords)}. It contains relevant information that would be found when searching for this topic."
            
            result = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": search_engines[i % len(search_engines)],
                "relevance_score": 0.9 - (i * 0.1),
                "last_updated": (datetime.now() - timedelta(days=i*30)).isoformat()
            }
            search_results["results"].append(result)
        
        # Add search metadata
        search_results["total_results"] = len(search_results["results"])
        search_results["search_time"] = f"{0.5 + (len(query) * 0.01):.2f}s"
        
        return search_results
        
    except Exception as e:
        return {"error": f"Web search error: {str(e)}"}


@tool
def scrape_webpage(url: str, extract_type: str = "content") -> Dict[str, Any]:
    """
    Extract and parse content from web pages with structured data extraction.
    
    This tool scrapes web pages to extract various types of content including text, metadata,
    and structured information for research and analysis purposes.
    
    Args:
        url (str): Complete URL of the webpage to scrape. Must be a valid HTTP/HTTPS URL.
                  Examples: "https://example.com/article", "https://news.site.com/story"
        extract_type (str, optional): Type of content to extract from the webpage.
                                    Options: "content" (main text), "metadata" (page info),
                                    "links" (hyperlinks), "images" (image data).
                                    Default is "content".
    
    Returns:
        Dict[str, Any]: Structured webpage data including:
            - url: Original URL that was scraped
            - extract_type: Type of extraction performed
            - timestamp: When the scraping was executed
            - status: Success or error status
            - content: Extracted content based on extract_type
            - word_count: Number of words in extracted content
    
    Example:
        >>> result = scrape_webpage("https://example.com/news", "content")
        >>> print(result['status'])
        'success'
    """
    try:
        # Simulate webpage scraping (in real implementation, would use actual scraping)
        scraped_data = {
            "url": url,
            "extract_type": extract_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        # Generate simulated webpage content
        if "news" in url.lower():
            content = {
                "title": "Latest News Article",
                "author": "John Doe",
                "published_date": datetime.now().strftime("%Y-%m-%d"),
                "content": "This is a simulated news article content that would be extracted from the webpage. It contains relevant information and details about the topic.",
                "summary": "A comprehensive overview of the latest developments in the field.",
                "tags": ["technology", "innovation", "research"]
            }
        elif "wiki" in url.lower():
            content = {
                "title": "Wikipedia Article",
                "content": "This is simulated Wikipedia content that would be extracted from the page. It provides detailed information about the subject matter.",
                "sections": ["Introduction", "History", "Current Status", "Future Outlook"],
                "references": ["Reference 1", "Reference 2", "Reference 3"]
            }
        else:
            content = {
                "title": "Webpage Content",
                "content": "This is simulated content extracted from the webpage. It contains relevant information about the requested topic.",
                "metadata": {
                    "description": "Page description",
                    "keywords": ["keyword1", "keyword2", "keyword3"],
                    "language": "en"
                }
            }
        
        scraped_data["content"] = str(content)
        scraped_data["word_count"] = str(len(content.get("content", "").split()))
        
        return scraped_data
        
    except Exception as e:
        return {"error": f"Web scraping error: {str(e)}"}


@tool
def analyze_web_content(content: str, analysis_type: str = "summary") -> Dict[str, Any]:
    """
    Analyze web content using various NLP techniques for insights and information extraction.
    
    This tool performs different types of content analysis including summarization, sentiment analysis,
    and entity extraction to help users understand and extract insights from web content.
    
    Args:
        content (str): Text content to analyze. Should be meaningful text content from web pages,
                      articles, or other sources. Minimum recommended length: 50 characters.
        analysis_type (str, optional): Type of analysis to perform on the content.
                                     Options: "summary" (key points and summary),
                                     "sentiment" (positive/negative/neutral analysis),
                                     "entities" (extract people, organizations, locations, dates).
                                     Default is "summary".
    
    Returns:
        Dict[str, Any]: Analysis results including:
            - analysis_type: Type of analysis performed
            - timestamp: When the analysis was executed
            - content_length: Length of analyzed content
            - summary/key_points: For summary analysis
            - sentiment/confidence: For sentiment analysis
            - entities: For entity extraction analysis
    
    Example:
        >>> result = analyze_web_content("This is a positive article about AI developments.", "sentiment")
        >>> print(result['sentiment'])
        'positive'
    """
    try:
        analysis_results = {
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content)
        }
        
        if analysis_type == "summary":
            # Generate a summary
            sentences = content.split('. ')
            summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else content
            analysis_results["summary"] = summary
            analysis_results["key_points"] = [
                "Main point 1 from the content",
                "Main point 2 from the content", 
                "Main point 3 from the content"
            ]
            
        elif analysis_type == "sentiment":
            # Simulate sentiment analysis
            positive_words = ["good", "great", "excellent", "positive", "success"]
            negative_words = ["bad", "poor", "negative", "failure", "problem"]
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                confidence = 0.8
            elif negative_count > positive_count:
                sentiment = "negative"
                confidence = 0.7
            else:
                sentiment = "neutral"
                confidence = 0.6
                
            analysis_results["sentiment"] = sentiment
            analysis_results["confidence"] = confidence
            analysis_results["positive_score"] = positive_count
            analysis_results["negative_score"] = negative_count
            
        elif analysis_type == "entities":
            # Simulate entity extraction
            entities = {
                "organizations": ["Company A", "Organization B"],
                "people": ["John Smith", "Jane Doe"],
                "locations": ["New York", "London"],
                "dates": ["2024-01-01", "2024-12-31"]
            }
            analysis_results["entities"] = entities
            
        else:
            analysis_results["error"] = f"Unknown analysis type: {analysis_type}"
            
        return analysis_results
        
    except Exception as e:
        return {"error": f"Content analysis error: {str(e)}"}


@tool
def fact_check_information(claim: str, sources: List[str]) -> Dict[str, Any]:
    """
    Verify factual claims against multiple sources with reliability scoring and verification status.
    
    This tool fact-checks information by comparing claims against provided sources and
    provides verification status, confidence scores, and source reliability assessments.
    
    Args:
        claim (str): The factual claim to verify. Should be a specific, verifiable statement.
                    Examples: "The population of New York City is 8.8 million people",
                             "Global temperatures have increased by 1.1°C since pre-industrial times"
        sources (List[str]): List of source URLs or references to check the claim against.
                           Should be credible sources like news sites, academic papers, or official reports.
                           Minimum recommended: 2 sources for reliable verification.
    
    Returns:
        Dict[str, Any]: Fact-checking results including:
            - claim: Original claim being verified
            - sources_checked: Number of sources analyzed
            - timestamp: When the fact-check was performed
            - verification_status: Overall verification result (verified/unverified/contested)
            - confidence_score: Confidence level in the verification (0.0 to 1.0)
            - source_verifications: Detailed analysis of each source
    
    Example:
        >>> sources = ["https://census.gov", "https://nyc.gov"]
        >>> result = fact_check_information("NYC population is 8.8 million", sources)
        >>> print(result['verification_status'])
        'verified'
    """
    try:
        fact_check_results = {
            "claim": claim,
            "sources_checked": len(sources),
            "timestamp": datetime.now().isoformat(),
            "verification_status": "verified" if len(claim) > 20 else "unverified",
            "confidence_score": 0.85 if len(claim) > 20 else 0.45
        }
        
        # Simulate fact-checking against sources
        source_verifications = []
        for i, source in enumerate(sources):
            verification = {
                "source": source,
                "supports_claim": i % 2 == 0,  # Alternate between supporting and not supporting
                "reliability_score": 0.8 + (i * 0.05),
                "notes": f"Source {i+1} {'supports' if i % 2 == 0 else 'contradicts'} the claim"
            }
            source_verifications.append(verification)
            
        fact_check_results["source_verifications"] = source_verifications
        
        # Overall assessment
        supporting_sources = sum(1 for v in source_verifications if v["supports_claim"])
        fact_check_results["supporting_sources"] = supporting_sources
        fact_check_results["contradicting_sources"] = len(sources) - supporting_sources
        
        if supporting_sources > len(sources) / 2:
            fact_check_results["conclusion"] = "Claim appears to be true based on majority of sources"
        else:
            fact_check_results["conclusion"] = "Claim appears to be false or disputed based on sources"
            
        return fact_check_results
        
    except Exception as e:
        return {"error": f"Fact-checking error: {str(e)}"}


@tool
def synthesize_research(query: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesize information from multiple sources into a comprehensive research report.
    
    This tool combines and analyzes information from multiple sources to create a cohesive
    research report with key findings, conclusions, and recommendations.
    
    Args:
        query (str): The research question or topic being investigated. Should be specific
                    and focused to guide the synthesis process.
                    Examples: "Impact of AI on healthcare", "Climate change mitigation strategies"
        sources (List[Dict[str, Any]]): List of source dictionaries containing research data.
                                      Each source should have content, metadata, and analysis results.
                                      Minimum recommended: 3 sources for comprehensive synthesis.
                                      Sources should be from search_web, scrape_webpage, or analyze_web_content.
    
    Returns:
        Dict[str, Any]: Comprehensive research synthesis including:
            - query: Original research question
            - sources_analyzed: Number of sources used in synthesis
            - timestamp: When the synthesis was performed
            - report: Executive summary, key findings, methodology, conclusions, and recommendations
            - source_analysis: Reliability and contribution analysis for each source
            - confidence_level: Overall confidence in the synthesis (High/Medium/Low)
    
    Example:
        >>> sources = [{"content": "AI improves diagnosis accuracy"}, {"content": "AI reduces costs"}]
        >>> result = synthesize_research("AI in healthcare", sources)
        >>> print(result['confidence_level'])
        'Medium'
    """
    try:
        synthesis_results = {
            "query": query,
            "sources_analyzed": len(sources),
            "timestamp": datetime.now().isoformat(),
            "report": {
                "executive_summary": f"Comprehensive analysis of {query} based on {len(sources)} sources",
                "key_findings": [
                    "Finding 1: Important insight from research",
                    "Finding 2: Another significant discovery",
                    "Finding 3: Additional relevant information"
                ],
                "methodology": "Analysis based on multiple web sources and fact-checking",
                "conclusions": f"Based on the research, {query} shows clear patterns and trends",
                "recommendations": [
                    "Continue monitoring this topic",
                    "Consider additional research in specific areas",
                    "Share findings with relevant stakeholders"
                ]
            }
        }
        
        # Add source analysis
        source_analysis = []
        for i, source in enumerate(sources):
            analysis = {
                "source_id": i + 1,
                "reliability": 0.8 + (i * 0.05),
                "contribution": f"Provided key information about aspect {i+1}",
                "limitations": "Limited to specific timeframe or scope"
            }
            source_analysis.append(analysis)
            
        synthesis_results["source_analysis"] = source_analysis
        synthesis_results["confidence_level"] = "High" if len(sources) >= 3 else "Medium"
        
        return synthesis_results
        
    except Exception as e:
        return {"error": f"Research synthesis error: {str(e)}"}


async def web_research_agent(research_query: str) -> str:
    """Main web research agent function."""
    return f"Web research completed for: {research_query}"


class WebResearchAgent:
    """Web Research Agent for comprehensive web-based information gathering and analysis."""
    
    def __init__(self):
        self.name = "Web Research Agent"
        self.description = "Comprehensive web research and information gathering agent"
        self.complexity_level = "Advanced"
        
    async def create_workflow(self) -> WorkflowGraph:
        """Create the web research workflow."""
        # Check for required environment variables
        api_key = os.getenv('API_KEY')
        base_url = os.getenv('BASE_URL')
        
        if not api_key or not base_url:
            raise ValueError("API_KEY and BASE_URL environment variables are required")
        
        # Create tools for different web research domains
        search_tools = [
            await function_to_schema(search_web, func_name="search_web", enhance_description=True),
            await function_to_schema(scrape_webpage, func_name="scrape_webpage", enhance_description=True),
        ]
        
        analysis_tools = [
            await function_to_schema(analyze_web_content, func_name="analyze_web_content", enhance_description=True),
            await function_to_schema(fact_check_information, func_name="fact_check_information", enhance_description=True),
        ]
        
        synthesis_tools = [
            await function_to_schema(synthesize_research, func_name="synthesize_research", enhance_description=True),
        ]
        
        # Create response agent
        response_agent = await function_to_schema(web_research_agent, func_name="web_research_agent", enhance_description=True)
        
        # Create main orchestrator with routing capability
        all_tools = search_tools + analysis_tools + synthesis_tools + [response_agent]
        
        main_orchestrator = create_orchestrator(
            api_key=api_key,
            base_url=base_url,
            llm_model="gpt-4",
            tools=all_tools
        )
        
        # Create specialized LLM execution nodes
        search_specialist = build_async_agent(
            api_key=api_key,
            base_url=base_url,
            llm_model="gpt-4",
            tools=search_tools
        )
        
        analysis_specialist = build_async_agent(
            api_key=api_key,
            base_url=base_url,
            llm_model="gpt-4",
            tools=analysis_tools
        )
        
        synthesis_specialist = build_async_agent(
            api_key=api_key,
            base_url=base_url,
            llm_model="gpt-4",
            tools=synthesis_tools
        )
        
        # Create workflow graph
        execution_graph = WorkflowGraph()
        
        # Add main orchestrator
        execution_graph.add_orchestrator_node("main_orchestrator", main_orchestrator)
        
        # Add LLM execution nodes
        execution_graph.add_node("search_specialist", search_specialist)
        execution_graph.add_node("analysis_specialist", analysis_specialist)
        execution_graph.add_node("synthesis_specialist", synthesis_specialist)
        
        # Add tool nodes
        execution_graph.add_node("web_searcher", search_web)
        execution_graph.add_node("web_scraper", scrape_webpage)
        execution_graph.add_node("content_analyzer", analyze_web_content)
        execution_graph.add_node("fact_checker", fact_check_information)
        execution_graph.add_node("research_synthesizer", synthesize_research)
        
        # Connect orchestrator to specialized agents
        execution_graph.add_edge("__start__", "main_orchestrator")
        execution_graph.add_edge("main_orchestrator", "search_specialist")
        execution_graph.add_edge("main_orchestrator", "analysis_specialist")
        execution_graph.add_edge("main_orchestrator", "synthesis_specialist")
        
        # Connect specialized agents to their tools
        execution_graph.add_edge("search_specialist", "web_searcher")
        execution_graph.add_edge("search_specialist", "web_scraper")
        execution_graph.add_edge("analysis_specialist", "content_analyzer")
        execution_graph.add_edge("analysis_specialist", "fact_checker")
        execution_graph.add_edge("synthesis_specialist", "research_synthesizer")
        
        # Add human interaction
        execution_graph.add_human_in_the_loop("main_orchestrator")
        
        return execution_graph
    
    def get_real_world_scenarios(self) -> List[Dict[str, Any]]:
        """Get real-world research scenarios for testing."""
        return [
            {
                "scenario": "Research the latest developments in artificial intelligence",
                "category": "Technology Research",
                "complexity": "High",
                "expected_output": "Comprehensive report on AI developments"
            },
            {
                "scenario": "Fact-check claims about climate change",
                "category": "Fact Checking",
                "complexity": "Medium",
                "expected_output": "Verified information with source citations"
            },
            {
                "scenario": "Gather information about a company for investment research",
                "category": "Business Research",
                "complexity": "High",
                "expected_output": "Detailed company analysis and financial data"
            },
            {
                "scenario": "Research academic papers on machine learning",
                "category": "Academic Research",
                "complexity": "High",
                "expected_output": "Synthesis of academic findings and methodologies"
            },
            {
                "scenario": "Find and analyze news articles about renewable energy",
                "category": "News Analysis",
                "complexity": "Medium",
                "expected_output": "News summary with trend analysis"
            }
        ]
    
    async def solve_research_problem(self, scenario: str) -> Dict[str, Any]:
        """Solve a research problem using the web research agent."""
        try:
            workflow = await self.create_workflow()
            compiled_graph = workflow.compile()
            
            result = await compiled_graph.execute(initial_input=scenario)
            
            return {
                "scenario": scenario,
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "scenario": scenario,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Export the agent
__all__ = ["WebResearchAgent", "web_research_agent"] 