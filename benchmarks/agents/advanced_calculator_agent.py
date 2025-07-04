"""
Financial Analysis Agent - Real-world financial planning and investment analysis
Helps users make informed financial decisions through comprehensive analysis and modeling.
"""

import os
import asyncio
import math
import statistics
import numpy as np
import requests
import json
from typing import Dict, Any, List, Union
from datetime import datetime, timedelta
from orion.agent_core import create_orchestrator, build_async_agent
from orion.agent_core.utils import function_to_schema
from orion.graph_core import WorkflowGraph
from orion.tool_registry import tool


# Financial Analysis Tools
@tool
def calculate_investment_returns(principal: float, annual_rate: float, years: int, compound_frequency: int = 12, investment_type: str = "savings") -> Dict[str, Any]:
    """
    Calculate comprehensive investment returns with compound interest, inflation adjustment, and year-by-year growth analysis.
    
    This tool provides detailed financial planning insights including compound interest calculations,
    inflation-adjusted returns, and yearly progression tracking to help users make informed investment decisions.
    
    Args:
        principal (float): Initial investment amount in dollars. Must be positive.
        annual_rate (float): Annual interest rate as a decimal (e.g., 0.05 for 5%). Must be between 0 and 1.
        years (int): Investment time period in years. Must be positive.
        compound_frequency (int, optional): Number of times interest is compounded per year. 
                                          Default is 12 (monthly). Common values: 1 (annually), 
                                          4 (quarterly), 12 (monthly), 365 (daily).
        investment_type (str, optional): Type of investment for categorization. 
                                       Examples: "savings", "stocks", "bonds", "real_estate".
                                       Default is "savings".
    
    Returns:
        Dict[str, Any]: Comprehensive investment analysis including:
            - investment_summary: Basic investment details and final amounts
            - inflation_adjusted: Real purchasing power calculations
            - yearly_progression: Year-by-year growth tracking
            - financial_advice: Personalized recommendations based on inflation comparison
    
    Example:
        >>> result = calculate_investment_returns(10000, 0.07, 10)
        >>> print(result['investment_summary']['final_amount'])
        19671.51
    """
    try:
        # Compound interest formula: A = P(1 + r/n)^(nt)
        amount = principal * (1 + annual_rate / compound_frequency) ** (compound_frequency * years)
        total_return = amount - principal
        roi_percentage = (total_return / principal) * 100
        
        # Calculate year-by-year growth
        yearly_values = []
        for year in range(1, years + 1):
            yearly_amount = principal * (1 + annual_rate / compound_frequency) ** (compound_frequency * year)
            yearly_values.append({
                "year": year,
                "value": round(yearly_amount, 2),
                "gain": round(yearly_amount - principal, 2)
            })
        
        # Assume 3.5% inflation rate
        inflation_rate = 3.5
        real_annual_rate = ((1 + annual_rate) / (1 + inflation_rate/100)) - 1
        real_amount = principal * (1 + real_annual_rate / compound_frequency) ** (compound_frequency * years)
        real_return = real_amount - principal
        
        return {
            "investment_summary": {
                "initial_investment": principal,
                "annual_rate": annual_rate * 100,
                "time_period_years": years,
                "compound_frequency": compound_frequency,
                "final_amount": round(amount, 2),
                "total_return": round(total_return, 2),
                "roi_percentage": round(roi_percentage, 2),
                "investment_type": investment_type
            },
            "inflation_adjusted": {
                "current_inflation_rate": round(inflation_rate, 2),
                "real_annual_return": round(real_annual_rate * 100, 2),
                "inflation_adjusted_amount": round(real_amount, 2),
                "real_purchasing_power_gain": round(real_return, 2)
            },
            "yearly_progression": yearly_values,
            "financial_advice": f"Your {annual_rate*100:.1f}% return beats inflation ({inflation_rate:.1f}%) by {(annual_rate*100-inflation_rate):.1f}%" if annual_rate*100 > inflation_rate else f"Consider investments with higher returns to beat {inflation_rate:.1f}% inflation"
        }
    except Exception as e:
        return {"error": f"Investment calculation error: {str(e)}"}


@tool
def analyze_portfolio_risk(investments: List[Dict[str, Union[str, float]]], total_portfolio_value: float) -> Dict[str, Any]:
    """
    Analyze portfolio diversification, risk distribution, and provide investment recommendations.
    
    This tool evaluates investment portfolios by calculating asset allocation weights, risk distribution,
    diversification scores, and provides personalized recommendations for portfolio optimization.
    
    Args:
        investments (List[Dict[str, Union[str, float]]]): List of investment dictionaries, each containing:
            - name (str): Name or identifier of the investment
            - amount (float): Dollar amount invested in this asset
            - type (str): Asset type (e.g., "stocks", "bonds", "real_estate", "crypto", "commodities")
            - risk_level (str): Risk classification ("low", "medium", "high", "very_high")
        total_portfolio_value (float): Total value of the entire portfolio in dollars. 
                                     Must be greater than sum of individual investments.
    
    Returns:
        Dict[str, Any]: Comprehensive portfolio analysis including:
            - portfolio_overview: Total value, allocation percentage, and investment count
            - investments: Detailed breakdown of each investment with weights and risk levels
            - risk_analysis: Overall risk score, risk distribution, and diversification metrics
            - recommendations: Personalized suggestions for portfolio improvement
    
    Example:
        >>> investments = [
        ...     {"name": "Tech Stocks", "amount": 50000, "type": "stocks", "risk_level": "high"},
        ...     {"name": "Government Bonds", "amount": 30000, "type": "bonds", "risk_level": "low"}
        ... ]
        >>> result = analyze_portfolio_risk(investments, 100000)
        >>> print(result['risk_analysis']['overall_risk_score'])
        6.5
    """
    try:
        if not investments:
            return {"error": "No investments provided for analysis"}
        
        # Calculate portfolio weights
        portfolio_analysis = []
        total_allocated = 0
        
        for investment in investments:
            amount = float(investment.get('amount', 0))
            asset_type = investment.get('type', 'unknown')
            risk_level = investment.get('risk_level', 'medium')
            
            weight = (amount / total_portfolio_value) * 100
            total_allocated += amount
            
            portfolio_analysis.append({
                "asset": investment.get('name', 'Unknown'),
                "type": asset_type,
                "amount": amount,
                "weight_percentage": round(weight, 2),
                "risk_level": risk_level
            })
        
        # Risk assessment
        risk_distribution = {}
        asset_distribution = {}
        
        for investment in portfolio_analysis:
            risk = investment['risk_level']
            asset_type = investment['type']
            
            risk_distribution[risk] = risk_distribution.get(risk, 0) + investment['weight_percentage']
            asset_distribution[asset_type] = asset_distribution.get(asset_type, 0) + investment['weight_percentage']
        
        # Generate risk score (1-10, 10 being highest risk)
        risk_weights = {'low': 2, 'medium': 5, 'high': 8, 'very_high': 10}
        weighted_risk = sum(risk_distribution.get(risk, 0) * weight / 100 for risk, weight in risk_weights.items())
        
        # Diversification score (higher is better)
        num_asset_types = len(asset_distribution)
        max_concentration = max(asset_distribution.values()) if asset_distribution else 100
        diversification_score = min(10, (num_asset_types * 2) - (max_concentration / 20))
        
        recommendations = []
        if max_concentration > 40:
            recommendations.append("Consider reducing concentration in single asset type")
        if weighted_risk > 7:
            recommendations.append("Portfolio has high risk - consider balancing with safer assets")
        if num_asset_types < 3:
            recommendations.append("Increase diversification across different asset types")
        if total_allocated < total_portfolio_value * 0.9:
            recommendations.append("Consider fully allocating available capital")
        
        return {
            "portfolio_overview": {
                "total_value": total_portfolio_value,
                "allocated_amount": total_allocated,
                "allocation_percentage": round((total_allocated / total_portfolio_value) * 100, 2),
                "number_of_investments": len(investments)
            },
            "investments": portfolio_analysis,
            "risk_analysis": {
                "overall_risk_score": round(weighted_risk, 2),
                "risk_distribution": risk_distribution,
                "asset_distribution": asset_distribution,
                "diversification_score": round(diversification_score, 2)
            },
            "recommendations": recommendations
        }
    except Exception as e:
        return {"error": f"Portfolio analysis error: {str(e)}"}


@tool
def calculate_loan_affordability(annual_income: float, monthly_expenses: float, loan_amount: float, 
                               interest_rate: float, loan_term_years: int) -> Dict[str, Any]:
    """
    Calculate loan affordability, monthly payments, and debt-to-income analysis for financial planning.
    
    This tool helps users determine if they can afford a loan by calculating monthly payments,
    debt-to-income ratios, and providing affordability assessments based on financial industry standards.
    
    Args:
        annual_income (float): Gross annual income in dollars. Must be positive.
        monthly_expenses (float): Total monthly expenses excluding the potential loan payment. 
                                Includes housing, utilities, food, transportation, etc.
        loan_amount (float): Principal amount of the loan in dollars. Must be positive.
        interest_rate (float): Annual interest rate as a decimal (e.g., 0.045 for 4.5%). 
                             Must be between 0 and 1.
        loan_term_years (int): Length of the loan in years. Common values: 15, 20, 30 for mortgages;
                             3-7 for auto loans; 1-5 for personal loans.
    
    Returns:
        Dict[str, Any]: Comprehensive loan affordability analysis including:
            - loan_details: Basic loan information and monthly payment calculation
            - affordability_analysis: Income analysis, debt ratios, and affordability rating
            - cost_analysis: Total cost breakdown including interest paid over the loan term
    
    Example:
        >>> result = calculate_loan_affordability(75000, 2000, 300000, 0.045, 30)
        >>> print(result['affordability_analysis']['affordability_rating'])
        'Good - Within acceptable range'
    """
    try:
        monthly_income = annual_income / 12
        available_monthly = monthly_income - monthly_expenses
        
        # Calculate monthly payment using loan formula
        monthly_rate = interest_rate / 12
        num_payments = loan_term_years * 12
        
        if monthly_rate == 0:
            monthly_payment = loan_amount / num_payments
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                            ((1 + monthly_rate)**num_payments - 1)
        
        # Affordability analysis
        debt_to_income_ratio = (monthly_payment / monthly_income) * 100
        remaining_after_loan = available_monthly - monthly_payment
        
        # Total cost analysis
        total_paid = monthly_payment * num_payments
        total_interest = total_paid - loan_amount
        
        # Affordability assessment
        if debt_to_income_ratio <= 28:
            affordability = "Excellent - Well within recommended limits"
        elif debt_to_income_ratio <= 36:
            affordability = "Good - Within acceptable range"
        elif debt_to_income_ratio <= 43:
            affordability = "Marginal - Consider reducing loan amount"
        else:
            affordability = "Not recommended - Exceeds safe debt limits"
        
        return {
            "loan_details": {
                "loan_amount": loan_amount,
                "interest_rate": interest_rate * 100,
                "term_years": loan_term_years,
                "monthly_payment": round(monthly_payment, 2)
            },
            "affordability_analysis": {
                "monthly_income": round(monthly_income, 2),
                "monthly_expenses": monthly_expenses,
                "available_monthly": round(available_monthly, 2),
                "remaining_after_loan": round(remaining_after_loan, 2),
                "debt_to_income_ratio": round(debt_to_income_ratio, 2),
                "affordability_rating": affordability
            },
            "cost_analysis": {
                "total_amount_paid": round(total_paid, 2),
                "total_interest_paid": round(total_interest, 2),
                "interest_percentage_of_loan": round((total_interest / loan_amount) * 100, 2)
            },
            "recommendation": f"Based on {debt_to_income_ratio:.1f}% debt-to-income ratio: {affordability}"
        }
    except Exception as e:
        return {"error": f"Loan affordability calculation error: {str(e)}"}


@tool
def retirement_planning_analysis(current_age: int, retirement_age: int, current_savings: float, 
                               monthly_contribution: float, expected_return: float, 
                               desired_retirement_income: float) -> Dict[str, Any]:
    """
    Comprehensive retirement planning analysis with savings projections and income gap analysis.
    
    This tool helps users plan for retirement by calculating future savings projections,
    analyzing income adequacy, and providing actionable recommendations for retirement planning.
    
    Args:
        current_age (int): Current age in years. Must be between 18 and 100.
        retirement_age (int): Target retirement age in years. Must be greater than current_age.
        current_savings (float): Current retirement savings balance in dollars. Must be non-negative.
        monthly_contribution (float): Monthly contribution to retirement savings in dollars. 
                                    Must be non-negative.
        expected_return (float): Expected annual investment return as a decimal (e.g., 0.07 for 7%). 
                               Must be between 0 and 1. Typical range: 0.04 to 0.10.
        desired_retirement_income (float): Desired monthly income during retirement in dollars. 
                                         Should account for inflation and lifestyle needs.
    
    Returns:
        Dict[str, Any]: Comprehensive retirement analysis including:
            - retirement_timeline: Age and time period calculations
            - current_financial_position: Current savings and contribution details
            - projected_retirement_wealth: Future value calculations for savings and contributions
            - retirement_income_analysis: Income adequacy assessment using 4% withdrawal rule
            - action_plan: Recommendations and additional savings requirements
    
    Example:
        >>> result = retirement_planning_analysis(35, 65, 50000, 500, 0.07, 5000)
        >>> print(result['retirement_income_analysis']['income_adequacy'])
        'Sufficient'
    """
    try:
        years_to_retirement = retirement_age - current_age
        years_in_retirement = 85 - retirement_age  # Assuming life expectancy of 85
        
        if years_to_retirement <= 0:
            return {"error": "Already at or past retirement age"}
        
        # Future value of current savings
        future_value_current = current_savings * (1 + expected_return) ** years_to_retirement
        
        # Future value of monthly contributions (annuity)
        monthly_rate = expected_return / 12
        months_to_retirement = years_to_retirement * 12
        
        if monthly_rate == 0:
            future_value_contributions = monthly_contribution * months_to_retirement
        else:
            future_value_contributions = monthly_contribution * \
                (((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate)
        
        total_retirement_savings = future_value_current + future_value_contributions
        
        # Calculate sustainable withdrawal amount (4% rule)
        safe_withdrawal_rate = 0.04
        sustainable_annual_income = total_retirement_savings * safe_withdrawal_rate
        sustainable_monthly_income = sustainable_annual_income / 12
        
        # Gap analysis
        desired_annual_income = desired_retirement_income * 12
        income_gap = desired_annual_income - sustainable_annual_income
        
        # Calculate additional savings needed
        if income_gap > 0:
            additional_capital_needed = income_gap / safe_withdrawal_rate
            additional_monthly_savings = additional_capital_needed / \
                (((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate) if monthly_rate != 0 else \
                additional_capital_needed / months_to_retirement
        else:
            additional_capital_needed = 0
            additional_monthly_savings = 0
        
        # Recommendations
        recommendations = []
        if income_gap > 0:
            recommendations.append(f"Increase monthly savings by ${additional_monthly_savings:.2f}")
            recommendations.append("Consider maximizing employer 401(k) matching")
            recommendations.append("Explore tax-advantaged retirement accounts (IRA, Roth IRA)")
        else:
            recommendations.append("On track for retirement goals!")
            recommendations.append("Consider increasing contributions for more comfortable retirement")
        
        return {
            "retirement_timeline": {
                "current_age": current_age,
                "retirement_age": retirement_age,
                "years_to_retirement": years_to_retirement,
                "years_in_retirement": years_in_retirement
            },
            "current_financial_position": {
                "current_savings": current_savings,
                "monthly_contribution": monthly_contribution,
                "expected_annual_return": expected_return * 100
            },
            "projected_retirement_wealth": {
                "future_value_of_current_savings": round(future_value_current, 2),
                "future_value_of_contributions": round(future_value_contributions, 2),
                "total_projected_savings": round(total_retirement_savings, 2)
            },
            "retirement_income_analysis": {
                "sustainable_monthly_income": round(sustainable_monthly_income, 2),
                "desired_monthly_income": desired_retirement_income,
                "monthly_income_gap": round(income_gap / 12, 2),
                "income_adequacy": "Sufficient" if income_gap <= 0 else "Insufficient"
            },
            "action_plan": {
                "additional_capital_needed": round(additional_capital_needed, 2),
                "additional_monthly_savings_required": round(additional_monthly_savings, 2),
                "recommendations": recommendations
            }
        }
    except Exception as e:
        return {"error": f"Retirement planning error: {str(e)}"}


class FinancialAnalysisAgent:
    """Real-world financial analysis agent for investment planning and financial decision making."""
    
    def __init__(self):
        self.name = "FinancialAnalysisAgent"
        self.complexity_level = 1
        self.description = "Real-world financial planning agent for investment analysis, retirement planning, and loan affordability"
    
    async def create_workflow(self) -> WorkflowGraph:
        """Create the financial analysis workflow."""
        try:
            api_key = os.environ.get("API_KEY", "")
            base_url = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                raise ValueError("API_KEY environment variable is required")
            
            # Create workflow graph
            workflow = WorkflowGraph()
            
            # Create tool schemas for orchestrator
            tools = [
                await function_to_schema(calculate_investment_returns, func_name="calculate_investment_returns", enhance_description=True),
                await function_to_schema(analyze_portfolio_risk, func_name="analyze_portfolio_risk", enhance_description=True),
                await function_to_schema(calculate_loan_affordability, func_name="calculate_loan_affordability", enhance_description=True),
                await function_to_schema(retirement_planning_analysis, func_name="retirement_planning_analysis", enhance_description=True),
            ]
            
            # Create orchestrator agent
            orchestrator_agent = create_orchestrator(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=tools
            )
            
            # Add orchestrator node
            workflow.add_orchestrator_node("financial_orchestrator", orchestrator_agent)
            
            # Add tool nodes
            workflow.add_node("calculate_investment_returns", calculate_investment_returns)
            workflow.add_node("analyze_portfolio_risk", analyze_portfolio_risk)
            workflow.add_node("calculate_loan_affordability", calculate_loan_affordability)
            workflow.add_node("retirement_planning_analysis", retirement_planning_analysis)
            
            # Connect workflow
            workflow.add_edge("__start__", "financial_orchestrator")
            workflow.add_edge("financial_orchestrator", "calculate_investment_returns")
            workflow.add_edge("financial_orchestrator", "analyze_portfolio_risk")
            workflow.add_edge("financial_orchestrator", "calculate_loan_affordability")
            workflow.add_edge("financial_orchestrator", "retirement_planning_analysis")
            
            # All tools lead to end
            workflow.add_edge("calculate_investment_returns", "__end__")
            workflow.add_edge("analyze_portfolio_risk", "__end__")
            workflow.add_edge("calculate_loan_affordability", "__end__")
            workflow.add_edge("retirement_planning_analysis", "__end__")
            
            return workflow
            
        except Exception as e:
            print(f"Error creating workflow: {e}")
            raise
    
    def get_real_world_scenarios(self) -> List[Dict[str, Any]]:
        """Get real-world financial scenarios for testing."""
        return [
            {
                "scenario": "Young professional retirement planning",
                "prompt": "I'm 25 years old, make $75,000/year, have $10,000 saved, can save $500/month. I want to retire at 65 with $5,000/month income. What's my retirement plan?",
                "category": "retirement_planning"
            },
            {
                "scenario": "Investment portfolio analysis",
                "prompt": "Analyze my $100,000 portfolio: $40,000 in tech stocks (high risk), $30,000 in bonds (low risk), $20,000 in real estate (medium risk), $10,000 in cash. What's my risk profile?",
                "category": "portfolio_analysis"
            },
            {
                "scenario": "Home loan affordability",
                "prompt": "I earn $80,000/year, have $3,000 monthly expenses, want a $300,000 mortgage at 6.5% for 30 years. Can I afford this?",
                "category": "loan_analysis"
            },
            {
                "scenario": "Investment return calculation",
                "prompt": "If I invest $50,000 at 7% annual return for 20 years with monthly compounding, what will it be worth?",
                "category": "investment_calculation"
            }
        ]


# Export the agent
__all__ = ["FinancialAnalysisAgent"]