import unittest
from unittest.mock import MagicMock, patch

from vocab import validate_answer

def test_validate_answer():
    result = validate_answer()