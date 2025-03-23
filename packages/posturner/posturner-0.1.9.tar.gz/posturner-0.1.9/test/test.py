import unittest
from posturner import trans_universal_pos
class TestStringMethods(unittest.TestCase):
    def test_trans_universal_pos(self):
        result = trans_universal_pos("adjective")
        assert result == "ADJ"
        result = trans_universal_pos("unknown")
        self.assertEqual(result, "X")
        result = trans_universal_pos("det")
        self.assertEqual(result, "PRON")
        result = trans_universal_pos("onomatopoeia")
        self.assertEqual(result, "INTJ")