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
    """Calculate investment returns with real market data and compound interest for real financial planning."""
    try:
        # Get real market data for context
        market_data = {}
        try:
            # Use real market data from Yahoo Finance API
            if investment_type.lower() in ["stocks", "stock", "equity"]:
                # Get S&P 500 data for comparison
                response = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=1y", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    chart_data = data.get('chart', {}).get('result', [{}])[0]
                    meta = chart_data.get('meta', {})
                    current_price = meta.get('regularMarketPrice', 0)
                    prev_close = meta.get('previousClose', 0)
                    if current_price and prev_close:
                        daily_change = ((current_price - prev_close) / prev_close) * 100
                        market_data = {
                            "sp500_current": current_price,
                            "daily_change_percent": round(daily_change, 2),
                            "market_context": "Based on current S&P 500 performance"
                        }
            
            # Get current Treasury rates for context
            treasury_response = requests.get("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/avg_interest_rates?filter=record_date:eq:2024-01-01", timeout=10)
            if treasury_response.status_code == 200:
                treasury_data = treasury_response.json()
                if treasury_data.get('data'):
                    treasury_rate = float(treasury_data['data'][0].get('avg_interest_rate_amt', 4.5))
                    market_data["risk_free_rate"] = treasury_rate
        except:
            market_data = {"note": "Real-time market data unavailable"}
        
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
        
        # Get real inflation data for context
        try:
            inflation_response = requests.get("https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0", timeout=10)
            if inflation_response.status_code == 200:
                inflation_data = inflation_response.json()
                if inflation_data.get('Results', {}).get('series'):
                    recent_data = inflation_data['Results']['series'][0]['data'][:12]  # Last 12 months
                    inflation_rate = sum(float(d.get('value', 0)) for d in recent_data) / len(recent_data) if recent_data else 3.5
                else:
                    inflation_rate = 3.5  # Default estimate
            else:
                inflation_rate = 3.5
        except:
            inflation_rate = 3.5
        
        # Calculate real return (adjusted for inflation)
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
            "market_context": market_data,
            "yearly_progression": yearly_values,
            "financial_advice": f"Your {annual_rate*100:.1f}% return beats inflation ({inflation_rate:.1f}%) by {(annual_rate*100-inflation_rate):.1f}%" if annual_rate*100 > inflation_rate else f"Consider investments with higher returns to beat {inflation_rate:.1f}% inflation"
        }
    except Exception as e:
        return {"error": f"Investment calculation error: {str(e)}"}


@tool
def analyze_portfolio_risk(investments: List[Dict[str, Union[str, float]]], total_portfolio_value: float) -> Dict[str, Any]:
    """Analyze portfolio diversification and risk profile for real investment decisions."""
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
    """Calculate loan affordability and monthly payments for real financial planning."""
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
    """Comprehensive retirement planning analysis for real financial decision making."""
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


@tool
def tax_optimization_analysis(annual_income: float, filing_status: str, deductions: List[Dict[str, float]], 
                            retirement_contributions: float, hsa_contribution: float = 0) -> Dict[str, Any]:
    """Analyze tax optimization strategies for real financial planning."""
    try:
        # 2024 tax brackets (current IRS data)
        tax_brackets = {
            "single": [
                (11000, 0.10), (44725, 0.12), (95375, 0.22), 
                (182050, 0.24), (231250, 0.32), (578125, 0.35), (float('inf'), 0.37)
            ],
            "married_filing_jointly": [
                (22000, 0.10), (89450, 0.12), (190750, 0.22), 
                (364200, 0.24), (462500, 0.32), (693750, 0.35), (float('inf'), 0.37)
            ],
            "married_filing_separately": [
                (11000, 0.10), (44725, 0.12), (95375, 0.22), 
                (182050, 0.24), (231250, 0.32), (346875, 0.35), (float('inf'), 0.37)
            ],
            "head_of_household": [
                (15700, 0.10), (59850, 0.12), (95350, 0.22), 
                (182050, 0.24), (231250, 0.32), (578100, 0.35), (float('inf'), 0.37)
            ]
        }
        
        # 2024 standard deductions (current IRS data)
        standard_deductions = {
            "single": 13850, 
            "married_filing_jointly": 27700,
            "married_filing_separately": 13850,
            "head_of_household": 20800
        }
        
        brackets = tax_brackets.get(filing_status, tax_brackets["single"])
        standard_deduction = standard_deductions.get(filing_status, 13850)
        
        # Calculate total deductions
        itemized_deductions = sum(deduction.get('amount', 0) for deduction in deductions)
        total_deductions = max(standard_deduction, itemized_deductions)
        
        # Calculate taxable income
        adjusted_gross_income = annual_income - retirement_contributions - hsa_contribution
        taxable_income = max(0, adjusted_gross_income - total_deductions)
        
        # Calculate tax owed
        tax_owed = 0
        remaining_income = taxable_income
        
        for i, (bracket_limit, rate) in enumerate(brackets):
            if remaining_income <= 0:
                break
            
            if i == 0:
                taxable_in_bracket = min(remaining_income, bracket_limit)
            else:
                prev_limit = brackets[i-1][0]
                taxable_in_bracket = min(remaining_income, bracket_limit - prev_limit)
            
            tax_owed += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
        
        # Calculate effective tax rate
        effective_rate = (tax_owed / annual_income) * 100 if annual_income > 0 else 0
        marginal_rate = next(rate for limit, rate in brackets if taxable_income <= limit) * 100
        
        # Tax optimization recommendations
        recommendations = []
        
        # Check if itemizing is beneficial
        if itemized_deductions < standard_deduction:
            recommendations.append(f"Use standard deduction (${standard_deduction:,.2f}) instead of itemizing")
        
        # Retirement contribution recommendations
        max_401k = 23000  # 2024 limit
        if retirement_contributions < max_401k:
            additional_contribution = min(max_401k - retirement_contributions, annual_income * 0.15)
            tax_savings = additional_contribution * (marginal_rate / 100)
            recommendations.append(f"Consider increasing 401(k) contribution by ${additional_contribution:,.2f} for ${tax_savings:,.2f} tax savings")
        
        # HSA recommendation
        max_hsa = 4150  # 2024 individual limit
        if hsa_contribution < max_hsa:
            additional_hsa = max_hsa - hsa_contribution
            recommendations.append(f"Maximize HSA contribution (additional ${additional_hsa:,.2f}) for triple tax advantage")
        
        return {
            "income_analysis": {
                "gross_income": annual_income,
                "retirement_contributions": retirement_contributions,
                "hsa_contributions": hsa_contribution,
                "adjusted_gross_income": adjusted_gross_income
            },
            "deduction_analysis": {
                "standard_deduction": standard_deduction,
                "itemized_deductions": itemized_deductions,
                "deduction_used": total_deductions,
                "deduction_type": "Standard" if total_deductions == standard_deduction else "Itemized"
            },
            "tax_calculation": {
                "taxable_income": round(taxable_income, 2),
                "federal_tax_owed": round(tax_owed, 2),
                "effective_tax_rate": round(effective_rate, 2),
                "marginal_tax_rate": round(marginal_rate, 2)
            },
            "optimization_opportunities": recommendations,
            "after_tax_income": round(annual_income - tax_owed, 2)
        }
    except Exception as e:
        return {"error": f"Tax analysis error: {str(e)}"}


async def financial_analysis_agent(financial_query: str) -> str:
    """Financial analysis agent that provides comprehensive financial planning advice."""
    try:
        # This would integrate with the orchestrator to analyze the query and route to appropriate tools
        return f"Processing financial analysis for: {financial_query}"
    except Exception as e:
        return f"Error in financial analysis: {str(e)}"


class FinancialAnalysisAgent:
    """Real-world financial analysis agent for investment planning and financial decision making."""
    
    def __init__(self):
        self.name = "FinancialAnalysisAgent"
        self.complexity_level = 1
        self.description = "Real-world financial planning agent for investment analysis, retirement planning, and tax optimization"
    
    async def create_workflow(self) -> WorkflowGraph:
        """Create the financial analysis workflow."""
        try:
            api_key = os.environ.get("API_KEY", "")
            base_url = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                raise ValueError("API_KEY environment variable is required")
            
            # Create tools for different financial domains
            investment_tools = [
                await function_to_schema(calculate_investment_returns, func_name="calculate_investment_returns", enhance_description=True),
                await function_to_schema(analyze_portfolio_risk, func_name="analyze_portfolio_risk", enhance_description=True),
            ]
            
            lending_tools = [
                await function_to_schema(calculate_loan_affordability, func_name="calculate_loan_affordability", enhance_description=True),
            ]
            
            planning_tools = [
                await function_to_schema(retirement_planning_analysis, func_name="retirement_planning_analysis", enhance_description=True),
                await function_to_schema(tax_optimization_analysis, func_name="tax_optimization_analysis", enhance_description=True),
            ]
            
            # Create response agent
            response_agent = await function_to_schema(financial_analysis_agent, func_name="financial_analysis_agent", enhance_description=True)
            
            # Create main orchestrator with routing capability
            all_tools = investment_tools + lending_tools + planning_tools + [response_agent]
            main_orchestrator = create_orchestrator(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=all_tools
            )
            
            # Create specialized LLM execution nodes
            investment_advisor = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=investment_tools
            )
            
            lending_advisor = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=lending_tools
            )
            
            planning_advisor = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=planning_tools
            )
            
            # Create workflow graph
            execution_graph = WorkflowGraph()
            
            # Add main orchestrator
            execution_graph.add_orchestrator_node("main_orchestrator", main_orchestrator)
            
            # Add LLM execution nodes
            execution_graph.add_node("investment_advisor", investment_advisor)
            execution_graph.add_node("lending_advisor", lending_advisor)
            execution_graph.add_node("planning_advisor", planning_advisor)
            
            # Add tool nodes
            execution_graph.add_node("investment_calculator", calculate_investment_returns)
            execution_graph.add_node("portfolio_analyzer", analyze_portfolio_risk)
            execution_graph.add_node("loan_calculator", calculate_loan_affordability)
            execution_graph.add_node("retirement_planner", retirement_planning_analysis)
            execution_graph.add_node("tax_optimizer", tax_optimization_analysis)
            
            # Connect orchestrator to specialized agents
            execution_graph.add_edge("__start__", "main_orchestrator")
            execution_graph.add_edge("main_orchestrator", "investment_advisor")
            execution_graph.add_edge("main_orchestrator", "lending_advisor")
            execution_graph.add_edge("main_orchestrator", "planning_advisor")
            
            # Connect specialized agents to their tools
            execution_graph.add_edge("investment_advisor", "investment_calculator")
            execution_graph.add_edge("investment_advisor", "portfolio_analyzer")
            execution_graph.add_edge("lending_advisor", "loan_calculator")
            execution_graph.add_edge("planning_advisor", "retirement_planner")
            execution_graph.add_edge("planning_advisor", "tax_optimizer")
            
            # Add human interaction
            execution_graph.add_human_in_the_loop("main_orchestrator")
            
            return execution_graph
            
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
            },
            {
                "scenario": "Tax optimization strategy",
                "prompt": "I'm single, earn $95,000, contribute $8,000 to 401k, have $15,000 in deductions. How can I optimize my taxes?",
                "category": "tax_planning"
            }
        ]
    
    async def solve_financial_problem(self, scenario: str) -> Dict[str, Any]:
        """Solve a real-world financial problem."""
        try:
            workflow = await self.create_workflow()
            compiled_graph = workflow.compile()
            
            result = await compiled_graph.execute(initial_input=scenario)
            
            return {
                "agent": self.name,
                "scenario": scenario,
                "solution": result,
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
__all__ = ["FinancialAnalysisAgent", "financial_analysis_agent"] 