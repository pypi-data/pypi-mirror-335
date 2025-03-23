from unittest.mock import call
from slack_bolt import Say
from slack_bolt_testcase.event_test_case import EventTestCase


class TestMentionExample(EventTestCase):
    USER_ID = 'U12345'

    def test_unhandled_message(self):
        @self.app.event('app_mention')
        def handle_unhandled_app_mention(say: Say):
            say('Unrecognized app_mention, please try again')

        self.trigger_event(event_type='app_mention', text='hello world', user=self.USER_ID)

        self.assertEqual(
            [call('Unrecognized app_mention, please try again')],
            self.mock_say.call_args_list
        )

    def test_handled_message(self):
        @self.app.event('app_mention')
        def handle_message_events(event: dict[str, str], say: Say):
            if event.get('text') == 'hello world':
                user_id = event.get('user')
                say(f'Hello to you <@{user_id}>, as well!')

        self.trigger_event(event_type='app_mention', text='hello world', user=self.USER_ID)

        self.assertEqual(
            [call(f'Hello to you <@{self.USER_ID}>, as well!')],
            self.mock_say.call_args_list,
        )
