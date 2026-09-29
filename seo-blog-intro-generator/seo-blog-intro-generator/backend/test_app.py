import json
import unittest

from app import parse_model_json


class ParseModelJsonTests(unittest.TestCase):
    def test_valid_json(self):
        payload = {
            "hook": "A strong hook",
            "headers": ["One", "Two"],
            "introduction": "Intro paragraph",
            "tips": ["Tip one", "Tip two"]
        }
        self.assertEqual(parse_model_json(json.dumps(payload)), payload)

    def test_json_in_markdown_fence(self):
        content = '''```json
{"hook": "A strong hook", "headers": ["One", "Two"], "introduction": "Intro paragraph", "tips": ["Tip one", "Tip two"]}
```'''
        payload = {
            "hook": "A strong hook",
            "headers": ["One", "Two"],
            "introduction": "Intro paragraph",
            "tips": ["Tip one", "Tip two"]
        }
        self.assertEqual(parse_model_json(content), payload)

    def test_json_with_explanatory_prefix(self):
        content = 'Here is the JSON: {"hook": "A strong hook", "headers": ["One"], "introduction": "Intro paragraph", "tips": ["Tip one"]}'
        payload = {
            "hook": "A strong hook",
            "headers": ["One"],
            "introduction": "Intro paragraph",
            "tips": ["Tip one"]
        }
        self.assertEqual(parse_model_json(content), payload)

    def test_empty_response_fails_cleanly(self):
        with self.assertRaisesRegex(ValueError, 'empty|malformed'):
            parse_model_json("   ")


if __name__ == "__main__":
    unittest.main()
