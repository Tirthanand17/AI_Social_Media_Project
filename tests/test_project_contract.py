import os
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class ProjectContractTests(unittest.TestCase):
    def test_all_documented_datasets_exist(self):
        raw = ROOT / "data" / "raw"
        expected = [
            "01_social_media_engagement.csv",
            "02_ml_training_dataset.csv",
            "03_nlp_captions_dataset.csv",
            "04_analytics_data.csv",
            "05_scheduler_data.csv",
            "06_best_time_dataset.csv",
            "07_trends_data.csv",
            "08_ab_testing_data.csv",
            "09_competitor_tracking_data.csv",
            "10_users_data.csv",
        ]
        missing = [name for name in expected if not (raw / name).is_file()]
        self.assertEqual(missing, [], f"Missing documented datasets: {missing}")

    def test_mysql_schema_contains_core_tables(self):
        schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8").lower()
        for table in ("posts", "schedules", "analytics", "trends"):
            self.assertIn(f"create table if not exists {table}", schema)

    def test_image_prompt_compatibility_module(self):
        from nlp.image_prompt_generator import generate_prompt_package

        result = generate_prompt_package("AI tools for creators", "Instagram")
        self.assertTrue(result["image_prompt"])
        self.assertEqual(result["platform"], "Instagram")

    def test_facebook_is_safe_by_default(self):
        from publisher.facebook_publisher import publish

        with patch.dict(os.environ, {"POSTING_MODE": "dry_run"}, clear=False):
            result = publish("Offline CI test")
        self.assertEqual(result["status"], "dry_run_success")
        self.assertEqual(result["mode"], "dry_run")

    def test_instagram_is_safe_by_default(self):
        from publisher.instagram_publisher import publish

        with patch.dict(os.environ, {"POSTING_MODE": "dry_run"}, clear=False):
            result = publish("Offline CI test")
        self.assertEqual(result["status"], "dry_run_success")
        self.assertEqual(result["mode"], "dry_run")


if __name__ == "__main__":
    unittest.main()
