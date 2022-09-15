"""Test WAVES

Test waves.py
"""
from unittest.mock import patch

import pytest

from waves import waves


@pytest.mark.unittest
def test_main():
    with patch('sys.argv', ['waves.py', 'docs']), \
         patch("waves.waves.docs") as mock_docs:
        waves.main()
        mock_docs.assert_called()

    target_string = 'dummy.target'
    with patch('sys.argv', ['waves.py', 'build', target_string]), \
         patch("waves.waves.build") as mock_build:
        waves.main()
        mock_build.assert_called_once()
        mock_build.call_args[0] == [target_string]

    project_directory = 'project_directory'
    with patch('sys.argv', ['waves.py', 'quickstart', project_directory]), \
         patch("waves.waves.quickstart") as mock_quickstart:
        waves.main()
        mock_quickstart.assert_called_once()
        mock_quickstart.call_args[0] == [project_directory]


@pytest.mark.unittest
def test_docs():
    with patch('webbrowser.open') as mock_webbrowser_open:
        waves.docs()
        mock_webbrowser_open.assert_called()

    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=True):
        return_code = waves.docs(print_local_path=True)
        assert return_code == 0
        mock_webbrowser_open.not_called()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=False):
        return_code = waves.docs(print_local_path=True)
        assert return_code != 0
        mock_webbrowser_open.not_called()


@pytest.mark.unittest
def test_build():
    with patch('subprocess.check_output', return_value=b"is up to date.") as mock_check_output:
        waves.build(['dummy.target'])
        mock_check_output.assert_called_once()

    with patch('subprocess.check_output', return_value=b"is up to date.") as mock_check_output:
        waves.build(['dummy.target'], git_clone_directory='dummy/clone')
        assert mock_check_output.call_count == 2


@pytest.mark.unittest
def test_quickstart():
    # Project directory does not exist. Copy the quickstart file tree.
    with patch('shutil.copytree') as mock_shutil_copytree, \
         patch('pathlib.Path.iterdir', side_effect=[['quickstart_directory']]), \
         patch('pathlib.Path.exists', side_effect=[False, True]):
        return_code = waves.quickstart()
        assert return_code == 0
        mock_shutil_copytree.assert_called_once()

    # Project directory exists and is empty. Don't copy the quickstart file tree.
    with patch('shutil.copytree') as mock_shutil_copytree, \
         patch('pathlib.Path.iterdir', side_effect=[[], ['quickstart_directory']]), \
         patch('pathlib.Path.exists', side_effect=[True, True]):
        return_code = waves.quickstart()
        assert return_code == 1
        mock_shutil_copytree.assert_not_called()

    # Project directory exists, but is not-empty. Don't copy the quickstart file tree.
    with patch('shutil.copytree') as mock_shutil_copytree, \
         patch('pathlib.Path.iterdir', side_effect=[['project_directory']]), \
         patch('pathlib.Path.exists', side_effect=[True, True]):
        return_code = waves.quickstart()
        assert return_code == 1
        mock_shutil_copytree.assert_not_called()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch('shutil.copytree') as mock_shutil_copytree, \
         patch('pathlib.Path.exists', side_effect=[False, False]):
        return_code = waves.quickstart()
        assert return_code != 0
        mock_shutil_copytree.assert_not_called()
