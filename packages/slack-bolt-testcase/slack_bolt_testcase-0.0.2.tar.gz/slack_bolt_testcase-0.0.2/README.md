# slack-bolt-testcase

![test](https://github.com/diegojromerolopez/slack-bolt-testcase/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/diegojromerolopez/slack-bolt-testcase/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/slack-bolt-testcase.svg)](https://pypi.python.org/pypi/slack-bolt-testcase/)
[![PyPI version slack-bolt-testcase](https://badge.fury.io/py/slack-bolt-testcase.svg)](https://pypi.python.org/pypi/slack-bolt-testcase/)
[![PyPI status](https://img.shields.io/pypi/status/slack-bolt-testcase.svg)](https://pypi.python.org/pypi/slack-bolt-testcase/)
[![PyPI download month](https://img.shields.io/pypi/dm/slack-bolt-testcase.svg)](https://pypi.python.org/pypi/slack-bolt-testcase/)

A simple unittest TestCase class to use it in your Slack Bolt App unittest tests

## Introduction

The [Slack bolt library](https://github.com/slackapi/bolt-python) and the
[Slack SDK](https://github.com/slackapi/python-slack-sdk) for Python are the best and official ways of implementing
Slack bots in Python. However, there is a small piece missing there: no official documentation about how to do
tests with the standard unittest library that allow developers to test that they have registered their handlers correctly.
slack-bolt-testcase fixes that.

## Requirements

- Python >= 3.9
- slack_bolt~=1.23.0
- slack_sdk~=3.35.0

## Use

To use this TestCase, you just need to inherit from [EventTestCase](/slack_bolt_testcase/event_test_case.py)
and make sure you have registered your event handlers
in the [AppTestCase.app](/slack_bolt_testcase/app_test_case.py).

```python
from unittest.mock import call

from slack_bolt import Say

from slack_bolt_testcase.event_test_case import EventTestCase

# Inherit from the EventTestCase
class TestEventExample(EventTestCase):
    def test_handled_event(self):
        # Make sure you have registered your events in a way with the self.app mocked Slack App object
        # you can do it here or pass the self.app object to a register function.
        @self.app.event('app_mention')
        def handle_message_events(event: dict[str, str], say: Say):
            # Ensure we are receiving the right text
            if event.get('text') == 'hello':
                event_type = event.get('type')
                say(f'Hello the handler handled a(n) {event_type}!')

        # Trigger the event
        self.trigger_event(event_type='app_mention', text='hello', user='U12345')

        # Check the assertions
        self.assertEqual(
            [call(f'Hello the handler handled a(n) app_mention!')],
            self.mock_say.call_args_list,
        )
```

More examples in the [tests folder](/slack_bolt_testcase/tests).

## License

[MIT](/LICENSE)

## Disclaimer

Slack is a trademark of Slack Technologies, LLC. This project is not affiliated with, endorsed by, or sponsored by
Slack Technologies, LLC. The use of the name "Slack" in this repository is solely for descriptive purposes and does
not imply any association or intent to infringe on any trademarks.
