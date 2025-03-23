import time
import uuid

from typing import Optional
from unittest.mock import MagicMock

from slack_bolt import BoltRequest, BoltContext, Say, BoltResponse
from slack_bolt_testcase.app_test_case import AppTestCase

# Any of the events included in https://api.slack.com/events
EventType = str


class EventTestCase(AppTestCase):
    GENERAL_CHANNEL_ID = 'C12345678'
    WORKSPACE_TEAM_ID = 'T12345678'

    def setUp(self):
        super().setUp()
        self.mock_say = MagicMock(Say)

    def trigger_event(
        self,
        event_type: EventType,
        text: str,
        user: str,
        channel: Optional[str] = None,
        team_id: Optional[str] = None,
        event_id: Optional[str] = None,
        event_time: Optional[str] = None,
    ) -> BoltResponse:
        request = self._create_event_request(
            event_type=event_type,
            text=text,
            channel=channel,
            user=user,
            team_id=team_id,
            event_id=event_id,
            event_time=event_time,
        )
        return self.app.dispatch(req=request)

    def _create_event_request(
        self,
        event_type: EventType,
        text: str,
        user: str,
        channel: str = 'GENERAL_CHANNEL_ID',
        team_id: str = WORKSPACE_TEAM_ID,
        event_id: Optional[str] = None,
        event_time: Optional[int] = None,
    ) -> BoltRequest:
        if not event_id:
            event_id = f'Ev{uuid.uuid4().int % 10**12}'

        if not event_time:
            event_time = int(time.time())

        ts = event_time - 5

        body = {
            'event': {
                'type': event_type,
                'text': text,
                'channel': channel,
                'user': user,
                'team_id': team_id,
                'ts': ts,
            },
            'type': 'event_callback',
            'event_id': event_id,
            'event_time': event_time,
        }

        context = BoltContext({'say': self.mock_say})

        return BoltRequest(body=body, mode='socket_mode', context=context)
