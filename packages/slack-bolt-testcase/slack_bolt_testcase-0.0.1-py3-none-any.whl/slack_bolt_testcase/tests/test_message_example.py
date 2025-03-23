from unittest.mock import call
from slack_bolt import Say
from slack_bolt_testcase.event_test_case import EventTestCase


class TestMessageExample(EventTestCase):
    USER_ID = 'U12345'

    def test_unhandled_message(self):
        @self.app.event('message')
        def handle_unhandled_message(say: Say):
            say('Unrecognized message, please try again')

        self.trigger_event(event_type='message', text='hello world', user=self.USER_ID)

        self.assertEqual(
            [call('Unrecognized message, please try again')],
            self.mock_say.call_args_list,
        )

    def test_handled_message(self):
        @self.app.message('hello world')
        def handle_message_events(event: dict[str, str], say: Say):
            user_id = event.get('user')
            say(f'Hello to you <@{user_id}>, as well!')

        self.trigger_event(event_type='message', text='hello world', user=self.USER_ID)

        self.assertEqual(
            [call(f'Hello to you <@{self.USER_ID}>, as well!')],
            self.mock_say.call_args_list,
        )
