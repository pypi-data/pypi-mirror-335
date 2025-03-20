from pathlib import Path

import pandas as pd

from chaiverse import utils
from chaiverse.cli_utils.login_cli import auto_authenticate
from chaiverse.http_client import FeedbackClient
from chaiverse.utils import print_color
from chaiverse.config import BASE_FEEDBACK_URL, FEEDBACK_ENDPOINT


class Feedback():
    def __init__(self, raw_data):
        self.raw_data = raw_data

    @property
    def df(self):
        raw_feedback = self.raw_data['feedback']
        feedback = self._extract_feedback_as_rows(raw_feedback)
        return pd.DataFrame(feedback)

    def sample(self):
        df = self.df
        print("No feedback") if df.empty else self.pprint_row(df[df.public].sample())

    def pprint_row(self, row):
        data = row.to_dict(orient='records')[0]
        print_color('### Conversation ###', 'yellow')
        print(data['conversation'])
        print_color('###', 'yellow')
        thumbs_up = "👍" if data['thumbs_up'] else "👎"
        print_color(f'Feedback {thumbs_up}: {data["feedback"]}', 'green')
        print_color(f'Conversation ID: {data["conversation_id"]}', 'blue')
        print_color(f'User ID: {data["user_id"]}', 'blue')
        print_color(f'Bot ID: {data["bot_id"]}', 'blue')

    def _extract_feedback_as_rows(self, feedback):
        rows = [self._extract_feedback_data(cid, data) for cid, data in feedback.items()]
        return rows

    def _extract_feedback_data(self, convo_id, message_data):
        convo = self._extract_conversation_from_messages(message_data['messages'])
        bot_id = self._extract_bot_id(convo_id)
        user_id = self._extract_user_id(convo_id)
        data = {
                'conversation_id': convo_id,
                'bot_id': bot_id,
                'user_id': user_id,
                'conversation': convo,
                'thumbs_up': message_data['thumbs_up'],
                'feedback': message_data['text'],
                'model_name': message_data['model_name'],
                'public': message_data.get('public', False),
        }
        return data

    def _extract_bot_id(self, convo_id):
        return '_'.join(convo_id.split('_')[:3])

    def _extract_user_id(self, convo_id):
        return convo_id.split('_')[3]

    def _extract_conversation_from_messages(self, messages):
        conversation = []
        messages = self._get_sorted_messages(messages)
        for message in messages:
            sender = self._get_sender_tag(message)
            message_content = message['content'].strip()
            conversation.append(f'{sender}: {message_content}')
        return '\n'.join(conversation)

    def _get_sorted_messages(self, messages):
        sorted_messages = sorted(messages, key=lambda x: x['sent_date'])
        return sorted_messages

    def _get_sender_tag(self, message):
        sender = message['sender']['name'].strip()
        if message['deleted']:
            sender = f'{sender} (deleted)'
        return sender


def get_feedback(submission_id: str, developer_key=None, reload=True):
    load_feedback = _get_latest_feedback if reload else _get_cached_feedback
    feedback = load_feedback(submission_id, developer_key)
    return feedback


def is_submission_updated(submission_id: str, submission_feedback_total : int) -> bool:
    filename = Path(utils.guanaco_data_dir()) / 'cache' / f'{submission_id}.pkl'
    try:
        feedback = utils._load_from_cache(filename)
        cached_feedback_total = int(feedback.raw_data.get("double_thumbs_up", 0)) + int(feedback.raw_data.get("thumbs_up", 0)) + int(feedback.raw_data.get("thumbs_down", 0))
        submission_updated = cached_feedback_total < submission_feedback_total
    except FileNotFoundError:
        submission_updated = True
    return submission_updated


def _get_latest_feedback(submission_id, developer_key):
    http_client = FeedbackClient(developer_key)
    response = http_client.get(endpoint=FEEDBACK_ENDPOINT, submission_id=submission_id)
    feedback = Feedback(response)
    filename = _get_cached_feedback_filename(submission_id)
    utils._save_to_cache(filename, feedback)
    return feedback


def _get_cached_feedback(submission_id, developer_key):
    filename = _get_cached_feedback_filename(submission_id)
    try:
        feedback = utils._load_from_cache(filename)
    except FileNotFoundError:
        feedback = _get_latest_feedback(submission_id, developer_key)
    return feedback


def _get_cached_feedback_filename(submission_id):
    return Path(utils.guanaco_data_dir()) / 'cache' / f'{submission_id}.pkl'
