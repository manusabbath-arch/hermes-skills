"""Prueba base que corre init.sh: si esto falla, nada de lo demás importa."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import app  # noqa: E402


class Smoke(unittest.TestCase):
    def test_health(self):
        self.assertEqual(app.health(), "ok")


if __name__ == "__main__":
    unittest.main()
