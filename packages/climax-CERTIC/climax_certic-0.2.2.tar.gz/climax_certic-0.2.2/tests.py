import unittest
from src.climax.__main__ import MaXProjectConfig, dir_is_max
from pathlib import Path

TEST_CONFIG_FILE = "tests_assets/max_config.xml"
TEST_CONFIG_EMPTY_FILE = "tests_assets/empty_max_config.xml"
TEST_CONFIG_FILE_BAD_ROOT = "tests_assets/bad_root_max_config.xml"
TEST_MAX_PROJECT_DIR = "tests_assets/max_project_dir"


class TestConfigFiles(unittest.TestCase):
    def setUp(self):
        pass

    def test_config(self):
        config = MaXProjectConfig(TEST_CONFIG_FILE)
        self.assertEqual(Path(TEST_CONFIG_FILE).resolve(), config.config_file_path)
        self.assertEqual(["fr", "en"], config.languages)
        self.assertEqual("mon Corpus Numérique", config.title)
        self.assertEqual("dev", config.env)
        self.assertEqual("max-tei-bundle", config.vocabulary_bundle)
        config.title = "new test title"
        self.assertEqual("new test title", config.title)

    def test_empty_config(self):
        config = MaXProjectConfig(TEST_CONFIG_EMPTY_FILE)
        config.title = "empty test title"
        self.assertEqual("empty test title", config.title)

    def test_bad_config(self):
        with self.assertRaises(ValueError) as context:  # noqa: F841
            MaXProjectConfig(TEST_CONFIG_FILE_BAD_ROOT)

    def test_set_languages(self):
        config = MaXProjectConfig("nothere")
        config.languages = ["fr", "en", "es", "jp"]
        self.assertEqual(["fr", "en", "es", "jp"], config.languages)

    def test_dir_is_max_project(self):
        self.assertTrue(dir_is_max(Path(TEST_MAX_PROJECT_DIR)))
        self.assertFalse(dir_is_max(Path(".")))

    def test_max_version(self):
        config = MaXProjectConfig("nothere")
        config.version = {"name": "name", "url": "url"}
        self.assertEqual({"name": "name", "url": "url"}, config.version)


if __name__ == "__main__":
    unittest.main()
