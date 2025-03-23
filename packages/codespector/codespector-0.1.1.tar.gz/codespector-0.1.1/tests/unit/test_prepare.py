import pytest
from unittest.mock import patch
from codespector.local.prepare import CodeSpectorDataPreparer


@pytest.fixture
def preparer():
    return CodeSpectorDataPreparer(output_dir='test_output', compare_branch='develop')


def test_prepare_dir(preparer):
    with patch('os.makedirs') as mock_makedirs, patch('os.path.exists', return_value=False):
        preparer._prepare_dir()
        mock_makedirs.assert_called_once_with('test_output')


def test_prepare_data(preparer):
    with (
        patch.object(preparer, '_prepare_dir') as mock_prepare_dir,
        patch.object(preparer, '_prepare_name_only_file') as mock_prepare_name_only_file,
        patch.object(preparer, '_prepare_diff_file') as mock_prepare_diff_file,
    ):
        preparer.prepare_data()
        mock_prepare_dir.assert_called_once()
        mock_prepare_name_only_file.assert_called_once()
        mock_prepare_diff_file.assert_called_once()
