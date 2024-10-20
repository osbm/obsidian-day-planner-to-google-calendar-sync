import unittest

from main import parse_line, get_event_json_from_parsed_line

class TestMain(unittest.TestCase):
    def test_parse_line(self):
        test_cases = [
            {
                'input': '- 9:00 - 11:00 Meeting with John',
                'expected': ['T09:00:00', 'T11:00:00', 'Meeting with John']
            },
            {
                'input': '- [ ] 10:00 - 11:00   Meeting with John and Jane ',
                'expected': ['T10:00:00', 'T11:00:00', 'Meeting with John and Jane']
            },
            {
                'input': '- [x] 10:00 - 11:00 Meeting with John and Jane \n',
                'expected': ['T10:00:00', 'T11:00:00', 'Meeting with John and Jane']
            },
            {
                'input': 'this is not a valid line for parsing',
                'expected': False
            },
            {
                'input': '- 23:00 - 00:00 Meeting with John',
                'expected': ['T23:00:00', 'T23:59:59', 'Meeting with John']
            },
            {
                'input': '',
                'expected': False
            },
            {
                'input': '  ',
                'expected': False
            },
            {
                'input': '\n',
                'expected': False
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = parse_line(test_case['input'])
                self.assertEqual(result, test_case['expected'])

    def test_get_event_json_from_parsed_line(self):

        test_cases = [
            {
                'inputs': {
                    'date': '2021-07-01',
                    'parsed_line': ['T09:00:00', 'T11:00:00', 'Meeting with John'],
                    'time_zone': 'Europe/Istanbul',
                    'custom_description': 'Created by planner'
                },
                'expected': {
                    'summary': 'Meeting with John',
                    'start': {
                        'dateTime': '2021-07-01T09:00:00',
                        'timeZone': 'Europe/Istanbul'
                    },
                    'end': {
                        'dateTime': '2021-07-01T11:00:00',
                        'timeZone': 'Europe/Istanbul'
                    },
                    'description': 'Created by planner'
                }
            },
            {
                'inputs': {
                    'date': '2021-07-01',
                    'parsed_line': ['T10:00:00', 'T11:00:00', 'Meeting with John and Jane'],
                    'time_zone': 'Europe/Istanbul',
                    'custom_description': 'Created by planner'
                },
                'expected': {
                    'summary': 'Meeting with John and Jane',
                    'start': {
                        'dateTime': '2021-07-01T10:00:00',
                        'timeZone': 'Europe/Istanbul'
                    },
                    'end': {
                        'dateTime': '2021-07-01T11:00:00',
                        'timeZone': 'Europe/Istanbul'
                    },
                    'description': 'Created by planner'
                }
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                result = get_event_json_from_parsed_line(**test_case['inputs'])
                self.assertEqual(result, test_case['expected'])