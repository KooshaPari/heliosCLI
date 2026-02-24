"""Tests for Pareto computation engine."""

import pandas as pd

from helios_router_ui.pareto.engine import compute_combos, compute_pareto


class TestParetoFrontier:
    """Test Pareto frontier computation."""

    def test_empty_dataframe(self):
        """Test with empty input."""
        result = compute_pareto(pd.DataFrame())
        assert result.empty

    def test_single_offer(self):
        """Test with single offer."""
        df = pd.DataFrame([{"offer_id": "o1", "quality": 0.8, "cost_usd": 0.5, "speed_score": 50}])
        result = compute_pareto(df)
        assert len(result) == 1
        assert result.iloc[0]["on_pareto"]  is True

    def test_dominated_offer(self):
        """Test that dominated offers are marked correctly."""
        df = pd.DataFrame(
            [
                {"offer_id": "o1", "quality": 0.8, "cost_usd": 0.5, "speed_score": 50},
                {"offer_id": "o2", "quality": 0.9, "cost_usd": 0.3, "speed_score": 60},  # dominates o1
            ]
        )
        result = compute_pareto(df)
        # o2 should be on pareto, o1 should not
        assert result[result["offer_id"] == "o2"]["on_pareto"].iloc[0]  is True

    def test_pareto_minimize_cost(self):
        """Test Pareto with cost minimization."""
        df = pd.DataFrame(
            [
                {"offer_id": "o1", "quality": 0.5, "cost_usd": 1.0, "speed_score": 50},
                {"offer_id": "o2", "quality": 0.5, "cost_usd": 0.5, "speed_score": 50},  # cheaper
            ]
        )
        result = compute_pareto(df, minimize_cost=True, minimize_speed=False, maximize_quality=False)
        # o2 should be on pareto (cheaper)
        assert result[result["offer_id"] == "o2"]["on_pareto"].iloc[0]  is True


class TestCombinations:
    """Test combination computation."""

    def test_pairs(self):
        """Test pair combinations."""
        df = pd.DataFrame(
            [
                {
                    "offer_id": "o1",
                    "quality": 0.8,
                    "cost_usd": 0.5,
                    "speed_score": 50,
                    "provider": "p1",
                    "model_id": "m1",
                },
                {
                    "offer_id": "o2",
                    "quality": 0.6,
                    "cost_usd": 0.3,
                    "speed_score": 40,
                    "provider": "p2",
                    "model_id": "m2",
                },
                {
                    "offer_id": "o3",
                    "quality": 0.7,
                    "cost_usd": 0.4,
                    "speed_score": 45,
                    "provider": "p3",
                    "model_id": "m3",
                },
            ]
        )
        result = compute_combos(df, 2)
        assert len(result) == 3  # C(3,2) = 3 pairs

    def test_trios(self):
        """Test trio combinations."""
        df = pd.DataFrame(
            [
                {
                    "offer_id": "o1",
                    "quality": 0.8,
                    "cost_usd": 0.5,
                    "speed_score": 50,
                    "provider": "p1",
                    "model_id": "m1",
                },
                {
                    "offer_id": "o2",
                    "quality": 0.6,
                    "cost_usd": 0.3,
                    "speed_score": 40,
                    "provider": "p2",
                    "model_id": "m2",
                },
                {
                    "offer_id": "o3",
                    "quality": 0.7,
                    "cost_usd": 0.4,
                    "speed_score": 45,
                    "provider": "p3",
                    "model_id": "m3",
                },
                {
                    "offer_id": "o4",
                    "quality": 0.9,
                    "cost_usd": 0.6,
                    "speed_score": 55,
                    "provider": "p4",
                    "model_id": "m4",
                },
            ]
        )
        result = compute_combos(df, 3)
        assert len(result) == 4  # C(4,3) = 4 trios
