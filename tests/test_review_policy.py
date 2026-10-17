import unittest

from app.review_policy import assess_review_route


class ReviewRoutingTests(unittest.TestCase):
    def test_confident_consistent_case_is_provisional(self):
        result = assess_review_route(
            {
                "probabilities": {"real": 0.91, "fake": 0.09},
                "face_results": [{"prediction": "REAL"}],
            }
        )

        self.assertEqual(result["status"], "provisional")
        self.assertFalse(result["required_review"])
        self.assertFalse(result["score_is_calibrated"])

    def test_low_model_score_routes_for_human_review(self):
        result = assess_review_route(
            {"probabilities": {"real": 0.52, "fake": 0.48}}
        )

        self.assertEqual(result["status"], "needs_review")
        self.assertTrue(result["required_review"])
        self.assertIn("not a calibrated probability", result["routing_reasons"][0])

    def test_conflicting_face_predictions_route_for_review(self):
        result = assess_review_route(
            {
                "probabilities": {"real": 0.91, "fake": 0.09},
                "face_results": [
                    {"prediction": "REAL"},
                    {"prediction": "FAKE"},
                ],
            }
        )

        self.assertTrue(result["required_review"])
        self.assertTrue(
            any("conflicting model predictions" in reason for reason in result["routing_reasons"])
        )

    def test_high_impact_case_routes_even_with_high_score(self):
        result = assess_review_route(
            {"probabilities": {"real": 0.99, "fake": 0.01}},
            high_impact=True,
        )

        self.assertTrue(result["required_review"])
        self.assertTrue(result["high_impact"])
        self.assertEqual(result["status"], "needs_review")


if __name__ == "__main__":
    unittest.main()
