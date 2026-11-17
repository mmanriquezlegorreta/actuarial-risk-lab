import unittest
import numpy as np
from models.monte_carlo import calculate_solvency_metrics
from models.monte_carlo import (
    simulate_portfolio,
    calculate_risk_metrics
)


class TestActuarialRiskLab(unittest.TestCase):

    def setUp(self):

        self.results = simulate_portfolio(
            age=40,
            term=10,
            number_insured=1000,
            sum_insured=500000,
            interest_rate=0.05,
            simulations=10000,
            seed=42
        )

        self.losses = self.results["losses"]

        self.metrics = calculate_risk_metrics(
            self.losses,
            initial_capital=2000000
        )

    def test_premium_positive(self):

        self.assertGreater(
            self.results["premium"], 0
        )

    def test_simulation_size(self):

        self.assertEqual(
            len(self.losses), 10000
        )

    def test_losses_finite(self):

        self.assertTrue(
            np.all(np.isfinite(self.losses))
        )

    def test_reproducibility(self):

        repeated = simulate_portfolio(
            simulations=10000,
            seed=42
        )

        np.testing.assert_array_equal(
            self.losses,
            repeated["losses"]
        )

    def test_var_tvar(self):

        self.assertGreaterEqual(
            self.metrics["tvar_95"],
            self.metrics["var_95"]
        )

    def test_insolvency_probability(self):

        probability = self.metrics[
            "insolvency_probability"
        ]

        self.assertGreaterEqual(probability, 0)
        self.assertLessEqual(probability, 1)

    def test_standard_deviation(self):

        self.assertGreaterEqual(
            self.metrics["standard_deviation"], 0
        )

    def test_risk_metrics_finite(self):

        for value in self.metrics.values():

            self.assertTrue(
                np.isfinite(value)
            )

    def test_expected_loss_approximately_zero(self):

        expected_loss = np.mean(self.losses)

        standard_error = (
            self.metrics["standard_deviation"]
            / np.sqrt(len(self.losses))
        )

        self.assertLess(
            abs(expected_loss),
            5 * standard_error,
            "La pérdida esperada se aleja demasiado de cero."
        )


    def test_monte_carlo_convergence(self):

        large_simulation = simulate_portfolio(
            age=40,
            term=10,
            number_insured=1000,
            sum_insured=500000,
            interest_rate=0.05,
            simulations=50000,
            seed=123
        )

        losses_10000 = self.losses
        losses_50000 = large_simulation["losses"]

        mean_10000 = np.mean(losses_10000)
        mean_50000 = np.mean(losses_50000)

        sd_10000 = np.std(losses_10000, ddof=1)
        sd_50000 = np.std(losses_50000, ddof=1)

        combined_error = np.sqrt(
            (sd_10000 ** 2 / len(losses_10000))
            +
            (sd_50000 ** 2 / len(losses_50000))
        )

        difference = abs(mean_10000 - mean_50000)

        self.assertLess(
            difference,
            5 * combined_error,
            "Las pérdidas esperadas no son estadísticamente compatibles."
        )

    def test_risk_metrics_convergence(self):

        results = simulate_portfolio(
            age=40,
            term=10,
            number_insured=1000,
            sum_insured=500000,
            interest_rate=0.05,
            simulations=50000,
            seed=123
        )

        metrics_10000 = calculate_risk_metrics(
            self.losses,
            initial_capital=2000000
        )

        metrics_50000 = calculate_risk_metrics(
            results["losses"],
            initial_capital=2000000
        )

        # Comparar VaR 95%
        self.assertLess(
            abs(
                metrics_10000["var_95"]
                - metrics_50000["var_95"]
            ),
            1000000
        )

        # Comparar VaR 99%
        self.assertLess(
            abs(
                np.quantile(self.losses, 0.99)
                - np.quantile(results["losses"], 0.99)
            ),
            1500000
        )

        # Comparar TVaR 95%
        self.assertLess(
            abs(
                metrics_10000["tvar_95"]
                - metrics_50000["tvar_95"]
            ),
            1500000
        )

        # Comparar probabilidad de insolvencia
        self.assertLessEqual(
            abs(
                metrics_10000["insolvency_probability"]
                - metrics_50000["insolvency_probability"]
            ),
            0.05
        )
    def test_adverse_mortality_increases_expected_loss(self):

        adverse_results = simulate_portfolio(
            age=40,
            term=10,
            number_insured=1000,
            sum_insured=500000,
            interest_rate=0.05,
            simulations=10000,
            seed=42,
            mortality_multiplier=1.20
        )

        base_expected_loss = np.mean(self.losses)

        adverse_expected_loss = np.mean(
            adverse_results["losses"]
        )

        self.assertGreater(
            adverse_expected_loss,
            base_expected_loss,
            "El escenario adverso no incrementó la pérdida esperada."
        ) 
    def test_var_99_greater_than_var_95(self):

        var_95 = np.quantile(
            self.losses,
            0.95
        )

        var_99 = np.quantile(
            self.losses,
            0.99
        )

        self.assertGreaterEqual(
            var_99,
            var_95
        )
    def test_solvency_metrics(self):

        solvency = calculate_solvency_metrics(
            self.losses,
            2000000
        )

        self.assertGreaterEqual(
            solvency["required_capital_95"], 0
        )

        self.assertGreaterEqual(
            solvency["required_capital_99"],
            solvency["required_capital_95"]
        )

        self.assertTrue(
            np.isfinite(solvency["solvency_margin_95"])
        )

        self.assertIn(
            solvency["status"],
            [
                "SOLVENCIA ADECUADA",
                "CAPITAL INSUFICIENTE AL 95%"
            ]
        )

if __name__ == "__main__":

    unittest.main(verbosity=2)