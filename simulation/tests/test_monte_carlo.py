import pytest
from simulation.monte_carlo import MonteCarloEngine
from simulation.tests.test_simulation import mock_system

def test_monte_carlo_execution(mock_system):
    mc = MonteCarloEngine(mock_system)
    summary = mc.run_monte_carlo(iterations=3, hours=0.5)
    
    assert "mission_success_rate" in summary
    assert summary["total_iterations"] == 3
    assert "mean" in summary["mission_success_rate"]

def test_monte_carlo_statistical_validity(mock_system):
    mc = MonteCarloEngine(mock_system)
    summary = mc.run_monte_carlo(iterations=5, hours=1.0)
    
    for metric in ["mission_success_rate", "avg_delivery_time_min"]:
        stats = summary[metric]
        assert stats["max"] >= stats["min"]
        assert len(stats["ci_95"]) == 2
