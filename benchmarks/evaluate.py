#!/usr/bin/env python3
"""
Benchmark Runner - Entry point for testing all real-world agents
"""

import asyncio
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Import all agents
from benchmarks.agents.advanced_calculator_agent import FinancialAnalysisAgent
from benchmarks.agents.market_intelligence_agent import MarketIntelligenceAgent
from benchmarks.agents.music_therapy_agent import MusicTherapyAgent
from benchmarks.agents.nutritional_wellness_agent import NutritionalWellnessAgent
from benchmarks.agents.career_development_agent import CareerDevelopmentAgent

from dotenv import load_dotenv

load_dotenv()


class BenchmarkRunner:
    """Runner for executing and tracking benchmark tests on real-world agents."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.agents = {
            "financial": FinancialAnalysisAgent(),
            "market_intelligence": MarketIntelligenceAgent(),
            "music_therapy": MusicTherapyAgent(),
            "nutrition": NutritionalWellnessAgent(),
            "career": CareerDevelopmentAgent(),
        }
    
    async def run_single_test(self, agent_name: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario on an agent."""
        print(f"\n🔧 Testing {agent_name}: {scenario['scenario']}")
        
        start_time = time.time()
        
        try:
            agent = self.agents[agent_name]
            
            # Create workflow
            workflow = await agent.create_workflow()
            compiled_graph = workflow.compile()
            
            # Execute the scenario
            result = await compiled_graph.execute(
                initial_input=scenario['prompt'],
                max_iterations=20,
                max_execution_time=120  # 2 minutes per test
            )
            
            execution_time = time.time() - start_time
            
            test_result = {
                "agent_name": agent_name,
                "scenario": scenario['scenario'],
                "category": scenario.get('category', 'general'),
                "initial_input": scenario['prompt'],
                "final_output": result,
                "execution_time_seconds": round(execution_time, 2),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
            print(f"✅ Success in {execution_time:.2f}s")
            print(f"📊 Output: {str(result)[:200]}...")
            
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            test_result = {
                "agent_name": agent_name,
                "scenario": scenario['scenario'],
                "category": scenario.get('category', 'general'),
                "initial_input": scenario['prompt'],
                "final_output": None,
                "execution_time_seconds": round(execution_time, 2),
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "traceback": traceback.format_exc()
            }
            
            print(f"❌ Failed in {execution_time:.2f}s: {error_msg}")
            
            return test_result
    
    async def run_agent_tests(self, agent_name: str, limit_scenarios: int = 2) -> List[Dict[str, Any]]:
        """Run tests for a specific agent."""
        print(f"\n🚀 Starting tests for {agent_name.upper()} Agent")
        print("=" * 60)
        
        agent = self.agents[agent_name]
        scenarios = agent.get_real_world_scenarios()[:limit_scenarios]
        
        results = []
        for scenario in scenarios:
            result = await self.run_single_test(agent_name, scenario)
            results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        return results
    
    async def run_all_tests(self, limit_scenarios: int = 2) -> None:
        """Run tests for all agents."""
        print("🎯 REAL-WORLD AGENT BENCHMARK SUITE")
        print("=" * 60)
        print(f"⏱️  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Testing {len(self.agents)} agents")
        print(f"📊 Max {limit_scenarios} scenarios per agent")
        
        self.start_time = time.time()
        
        for agent_name in self.agents.keys():
            try:
                agent_results = await self.run_agent_tests(agent_name, limit_scenarios)
                self.results.extend(agent_results)
            except Exception as e:
                print(f"❌ Failed to test {agent_name}: {str(e)}")
        
        total_time = time.time() - self.start_time
        
        # Print summary
        self.print_summary(total_time)
        
        # Save results
        await self.save_results()
    
    def print_summary(self, total_time: float) -> None:
        """Print test execution summary."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        
        successful_tests = [r for r in self.results if r['status'] == 'success']
        failed_tests = [r for r in self.results if r['status'] == 'error']
        
        print(f"✅ Successful tests: {len(successful_tests)}")
        print(f"❌ Failed tests: {len(failed_tests)}")
        print(f"📈 Success rate: {len(successful_tests)/len(self.results)*100:.1f}%")
        print(f"⏱️  Total execution time: {total_time:.2f}s")
        print(f"📊 Average time per test: {total_time/len(self.results):.2f}s")
        
        # Print by agent
        print("\n📋 Results by Agent:")
        for agent_name in self.agents.keys():
            agent_results = [r for r in self.results if r['agent_name'] == agent_name]
            agent_success = [r for r in agent_results if r['status'] == 'success']
            print(f"  {agent_name:20}: {len(agent_success)}/{len(agent_results)} successful")
        
        # Print failed tests
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['agent_name']}: {test['scenario']}")
                print(f"    Error: {test['error']}")
    
    async def save_results(self) -> None:
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{timestamp}.json"
        
        summary = {
            "benchmark_info": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "successful_tests": len([r for r in self.results if r['status'] == 'success']),
                "failed_tests": len([r for r in self.results if r['status'] == 'error']),
                "total_execution_time": time.time() - self.start_time if self.start_time else 0
            },
            "results": self.results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")


async def run_specific_agent(agent_name: str, scenario_index: int = 0) -> None:
    """Run a specific test for debugging."""
    runner = BenchmarkRunner()
    
    if agent_name not in runner.agents:
        print(f"❌ Agent '{agent_name}' not found. Available: {list(runner.agents.keys())}")
        return
    
    agent = runner.agents[agent_name]
    scenarios = agent.get_real_world_scenarios()
    
    if scenario_index >= len(scenarios):
        print(f"❌ Scenario index {scenario_index} out of range. Available: 0-{len(scenarios)-1}")
        return
    
    scenario = scenarios[scenario_index]
    result = await runner.run_single_test(agent_name, scenario)
    
    print("\n📊 DETAILED RESULT:")
    print(json.dumps(result, indent=2))


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Run specific agent
        print(sys.argv)
        agent_name = sys.argv[1]
        scenario_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        await run_specific_agent(agent_name, scenario_index)
    else:
        # Run full benchmark
        runner = BenchmarkRunner()
        await runner.run_all_tests(limit_scenarios=2)


if __name__ == "__main__":
    asyncio.run(main())