"""
Orion Framework Benchmarks

This package contains benchmark agents and tests for evaluating the Orion framework
performance across different complexity levels and use cases.
"""

# Real-world problem-solving agents for practical use cases
from .agents import (
    FinancialAnalysisAgent,
    MarketIntelligenceAgent,
    MusicTherapyAgent,
    NutritionalWellnessAgent,
    CareerDevelopmentAgent,
    WebResearchAgent
)

__all__ = [
    "FinancialAnalysisAgent",
    "MarketIntelligenceAgent", 
    "MusicTherapyAgent",
    "NutritionalWellnessAgent",
    "CareerDevelopmentAgent",
    "WebResearchAgent"
]

__version__ = "1.0.0" 