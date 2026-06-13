import unittest

from app_data import get_health_payload, get_person_payload


class TestMain(unittest.TestCase):
    def test_health_check(self):
        self.assertEqual(get_health_payload(), {"status": "ok"})

    def test_get_person(self):
        self.assertEqual(get_person_payload(), {"name": "John Doe", "age": 30})


if __name__ == "__main__":
    unittest.main()
