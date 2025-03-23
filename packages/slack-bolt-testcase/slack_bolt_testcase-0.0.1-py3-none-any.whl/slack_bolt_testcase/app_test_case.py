from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.web import SlackResponse


class AppTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.app = App(
            token_verification_enabled=False,
            token='token',
            process_before_response=True,
        )

        auth_test_patcher = patch('slack_sdk.web.client.WebClient.auth_test')
        self.mock_auth_test = auth_test_patcher.start()
        self.addCleanup(auth_test_patcher.stop)
        self.mock_auth_test.side_effect = self._mock_auth_test_side_effect

        users_info_patcher = patch('slack_sdk.web.client.WebClient.users_info')
        self.mock_users_info = users_info_patcher.start()
        self.addCleanup(users_info_patcher.stop)
        self.mock_users_info.side_effect = self._mock_users_info_side_effect

        self.mock_web_client = MagicMock(WebClient)

    def _mock_auth_test_side_effect(self, **kwargs) -> SlackResponse:
        return SlackResponse(
            client=self.mock_web_client,
            http_verb='POST',
            api_url='https://slack.example.com/auth.test',
            status_code=200,
            req_args={},
            headers={},
            data={},
        )

    def _mock_users_info_side_effect(
        self, user: str, include_locale: Optional[bool] = None, **kwargs
    ) -> SlackResponse:

        avatar_path = 'https://example.com/avatar/da39a3e.jpg'

        data = {
            'ok': True,
            'user': {
                'id': user,
                'team_id': 'T012AB3C4',
                'name': 'john',
                'deleted': False,
                'color': '9f69e7',
                'real_name': 'John Doe',
                'tz': 'America/New_York',
                'tz_label': 'Eastern Daylight Time',
                'tz_offset': -14400,
                'profile': {
                    'avatar_hash': 'da39a3ee5e6b',
                    'status_text': 'Test status',
                    'status_emoji': ':boat:',
                    'real_name': 'John Doe',
                    'display_name': 'doe',
                    'real_name_normalized': 'John Doe',
                    'display_name_normalized': 'doe',
                    'email': 'john.doe@example.com',
                    'image_original': avatar_path,
                    'image_24': avatar_path,
                    'image_32': avatar_path,
                    'image_48': avatar_path,
                    'image_72': avatar_path,
                    'image_192': avatar_path,
                    'image_512': avatar_path,
                    'team': 'T0123456A',
                },
                'is_admin': True,
                'is_owner': False,
                'is_primary_owner': False,
                'is_restricted': False,
                'is_ultra_restricted': False,
                'is_bot': False,
                'updated': 1502138686,
                'is_app_user': False,
                'has_2fa': False,
            },
        }
        if include_locale:
            data['locale'] = 'en_US'

        return SlackResponse(
            client=self.mock_web_client,
            http_verb='GET',
            api_url='https://slack.example.com/users.info',
            status_code=200,
            req_args={},
            headers={},
            data=data,
        )
