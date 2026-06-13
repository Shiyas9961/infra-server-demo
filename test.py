import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TESTS_DIR = BASE_DIR / "tests"


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(TESTS_DIR),
        top_level_dir=str(BASE_DIR),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
