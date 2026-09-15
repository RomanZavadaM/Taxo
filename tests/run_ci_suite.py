"""Run unittest and return its result before third-party Windows shutdown hooks.

Some binary GUI/image wheels can change the process status while CPython 3.13
is finalizing on Windows runners.  All test cleanup and unittest reporting have
already completed at this point, so CI exits from the recorded TestResult.
"""
import os
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.stdout.flush()
sys.stderr.flush()
os._exit(0 if result.wasSuccessful() else 1)
