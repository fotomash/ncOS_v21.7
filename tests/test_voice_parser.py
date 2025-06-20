import sys
from unittest.mock import MagicMock
import unittest

# Ensure parser module can be imported without heavy dependencies
sys.modules['spacy'] = MagicMock()
sys.path.append('_21.7.2_verify')
import voice_tag_parser

class TestVoiceTagParser(unittest.TestCase):
    def setUp(self):
        self.parser = voice_tag_parser.VoiceTagParser()

    def test_mark_phrase_parsing(self):
        tag = self.parser.parse('Mark gold bullish on 4hour swept lows at 2358')
        self.assertEqual(tag.symbol, 'XAUUSD')
        self.assertEqual(tag.timeframe, 'H4')
        self.assertEqual(tag.bias, 'bullish')
        self.assertEqual(tag.notes, 'swept lows 2358')

    def test_log_phrase_parsing(self):
        tag = self.parser.parse('Log euro bearish 1min after NFP')
        self.assertEqual(tag.symbol, 'EURUSD')
        self.assertEqual(tag.timeframe, 'M1')
        self.assertEqual(tag.bias, 'bearish')
        self.assertEqual(tag.notes, 'after nfp')

if __name__ == '__main__':
    unittest.main()
