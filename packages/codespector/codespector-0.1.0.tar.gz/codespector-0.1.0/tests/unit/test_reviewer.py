import pytest
from unittest.mock import patch, mock_open
from codespector.local.reviewer import CodeSpectorReviewer
import os
import ujson
from unittest.mock import MagicMock


@pytest.fixture
def reviewer():
    return CodeSpectorReviewer(
        diff_file='diff.json',
        chat_token='test_token',
        chat_agent='codestral',
        chat_model=None,
        system_content='Test system content',
        output_dir='test_output',
    )


def test_request_to_chat_agent(reviewer):
    prompt = 'Test prompt'
    mock_response = MagicMock()
    mock_response.json.return_value = {'choices': [{'message': {'content': 'Test response'}}]}

    with (
        patch('requests.post', return_value=mock_response) as mock_post,
        patch('builtins.open', mock_open()) as mock_file,
    ):
        response = reviewer._request_to_chat_agent(prompt)

        mock_post.assert_called_once_with(
            'https://api.mistral.ai/v1/chat/completions',
            json={
                'model': 'codestral-latest',
                'messages': [{'role': 'system', 'content': 'Test system content'}, {'role': 'user', 'content': prompt}],
            },
            headers={'Authorization': 'Bearer test_token'},
            timeout=100,
        )
        mock_file.assert_called_with(os.path.join('test_output', 'request.json'), 'w', encoding='utf-8')
        assert response == mock_response


# tests/unit/test_reviewer.py
def test_send_to_review(reviewer):
    diff_data = {'diff': 'Test diff', 'original files': ['file1.py', 'file2.py']}
    mock_response = MagicMock()
    mock_response.json.return_value = {'choices': [{'message': {'content': 'Test response'}}]}

    with (
        patch('builtins.open', mock_open(read_data=ujson.dumps(diff_data))) as mock_file,
        patch.object(reviewer, '_request_to_chat_agent', return_value=mock_response) as mock_request,
        patch('ujson.dump') as _,
    ):
        reviewer.send_to_review()

        mock_file.assert_any_call(os.path.join('test_output', 'diff.json'), 'r', encoding='utf-8')
        mock_request.assert_called_once_with(
            prompt='Пожалуйста, проверь следующие изменения в коде на наличие очевидных проблем с качеством или безопасностью. '
            'Предоставь краткий отчет в формате markdown:\n\n'
            'DIFF:\n'
            'Test diff\n\n'
            'ORIGINAL FILES:\n'
            '[\n    "file1.py",\n    "file2.py"\n]'
        )
        mock_file.assert_any_call(os.path.join('test_output', 'response.json'), 'w', encoding='utf-8')
        mock_file.assert_any_call(os.path.join('test_output', 'result.txt'), 'w', encoding='utf-8')


def test_start(reviewer):
    with patch.object(reviewer, 'send_to_review') as mock_send_to_review:
        reviewer.start()
        mock_send_to_review.assert_called_once()
