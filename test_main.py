import unittest
import os
from unittest.mock import patch
import semver
from main import get_extension_data, find_duplicates, get_latest_versions, show_report, remove_duplicates


class TestGetExtensionData(unittest.TestCase):
    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_get_extension_data_valid(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ['ext1-1.0.0', 'ext2-2.1.0', 'ext3-0.1.0']
        mock_isdir.return_value = True
        expected_data = {
            'ext1': [semver.VersionInfo(1, 0, 0)],
            'ext2': [semver.VersionInfo(2, 1, 0)],
            'ext3': [semver.VersionInfo(0, 1, 0)],
        }
        self.assertEqual(get_extension_data('/path/to/extensions'), expected_data)

    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_get_extension_data_invalid_version(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ['ext1-1.0.0', 'ext2-invalid', 'ext3-0.1.0']
        mock_isdir.return_value = True
        expected_data = {
            'ext1': [semver.VersionInfo(1, 0, 0)],
            'ext3': [semver.VersionInfo(0, 1, 0)],
        }
        self.assertEqual(get_extension_data('/path/to/extensions'), expected_data)

    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_get_extension_data_no_extensions(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = []
        mock_isdir.return_value = True
        self.assertEqual(get_extension_data('/path/to/extensions'), {})

    @patch('os.listdir')
    @patch('os.path.isdir')
    def test_get_extension_data_not_a_directory(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ['ext1-1.0.0']
        mock_isdir.return_value = False
        self.assertEqual(get_extension_data('/path/to/extensions'), {})


class TestFindDuplicates(unittest.TestCase):
    def test_find_duplicates_no_duplicates(self):
        extension_data = {
            'ext1': [semver.VersionInfo(1, 0, 0)],
            'ext2': [semver.VersionInfo(2, 0, 0)],
        }
        self.assertEqual(find_duplicates(extension_data), {})

    def test_find_duplicates_single_duplicate(self):
        extension_data = {
            'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)],
            'ext2': [semver.VersionInfo(2, 0, 0)],
        }
        expected_duplicates = {'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)]}
        self.assertEqual(find_duplicates(extension_data), expected_duplicates)

    def test_find_duplicates_multiple_duplicates(self):
        extension_data = {
            'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)],
            'ext2': [semver.VersionInfo(2, 0, 0), semver.VersionInfo(2, 1, 0), semver.VersionInfo(2, 2, 0)],
        }
        expected_duplicates = {
            'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)],
            'ext2': [semver.VersionInfo(2, 0, 0), semver.VersionInfo(2, 1, 0), semver.VersionInfo(2, 2, 0)],
        }
        self.assertEqual(find_duplicates(extension_data), expected_duplicates)


class TestGetLatestVersions(unittest.TestCase):
    def test_get_latest_versions_single_duplicate(self):
        duplicate_extensions = {'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)]}
        expected_latest = {'ext1': semver.VersionInfo(1, 1, 0)}
        self.assertEqual(get_latest_versions(duplicate_extensions), expected_latest)

    def test_get_latest_versions_multiple_duplicates(self):
        duplicate_extensions = {
            'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)],
            'ext2': [semver.VersionInfo(2, 0, 0), semver.VersionInfo(2, 1, 0), semver.VersionInfo(2, 2, 0)],
        }
        expected_latest = {
            'ext1': semver.VersionInfo(1, 1, 0),
            'ext2': semver.VersionInfo(2, 2, 0),
        }
        self.assertEqual(get_latest_versions(duplicate_extensions), expected_latest)

    def test_get_latest_versions_no_duplicates(self):
        duplicate_extensions = {}
        self.assertEqual(get_latest_versions(duplicate_extensions), {})


class TestShowReport(unittest.TestCase):
    @patch('builtins.print')
    def test_show_report_no_duplicates(self, mock_print):
        duplicate_extensions = {}
        latest_versions = {}
        show_report(duplicate_extensions, latest_versions)
        mock_print.assert_called_once_with("No duplicate extensions found.")

    @patch('builtins.print')
    def test_show_report_with_duplicates(self, mock_print):
        duplicate_extensions = {'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)]}
        latest_versions = {'ext1': semver.VersionInfo(1, 1, 0)}
        show_report(duplicate_extensions, latest_versions)
        self.assertEqual(mock_print.call_count, 2)
        mock_print.assert_any_call("Duplicate extensions Report:")
        mock_print.assert_any_call("* ext1 (Latest: 1.1.0, Old: 1.0.0)")


class TestRemoveDuplicates(unittest.TestCase):
    @patch('os.makedirs')
    @patch('shutil.move')
    @patch('builtins.input')
    def test_remove_duplicates_auto_approve(self, mock_input, mock_move, mock_makedirs):
        mock_input.return_value = "yes"
        duplicate_extensions = {'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)]}
        latest_versions = {'ext1': semver.VersionInfo(1, 1, 0)}
        extensions_path = '/path/to/extensions'
        args = unittest.mock.MagicMock()
        args.auto_approve = True
        remove_duplicates(duplicate_extensions, latest_versions, extensions_path, args)
        mock_makedirs.assert_called_once_with('old_versions', exist_ok=True)
        mock_move.assert_called_once_with(os.path.join('/path/to/extensions', 'ext1-1.0.0'), os.path.join('old_versions', 'ext1-1.0.0'))

    @patch('os.makedirs')
    @patch('shutil.move')
    @patch('builtins.input')
    def test_remove_duplicates_manual_approve_yes(self, mock_input, mock_move, mock_makedirs):
        mock_input.return_value = "yes"
        duplicate_extensions = {'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)]}
        latest_versions = {'ext1': semver.VersionInfo(1, 1, 0)}
        extensions_path = '/path/to/extensions'
        args = unittest.mock.MagicMock()
        args.auto_approve = False
        remove_duplicates(duplicate_extensions, latest_versions, extensions_path, args)
        mock_makedirs.assert_called_once_with('old_versions', exist_ok=True)
        mock_move.assert_called_once_with(os.path.join('/path/to/extensions', 'ext1-1.0.0'), os.path.join('old_versions', 'ext1-1.0.0'))

    @patch('os.makedirs')
    @patch('shutil.move')
    @patch('builtins.input')
    def test_remove_duplicates_manual_approve_no(self, mock_input, mock_move, mock_makedirs):
        mock_input.return_value = "no"
        duplicate_extensions = {'ext1': [semver.VersionInfo(1, 0, 0), semver.VersionInfo(1, 1, 0)]}
        latest_versions = {'ext1': semver.VersionInfo(1, 1, 0)}
        extensions_path = '/path/to/extensions'
        args = unittest.mock.MagicMock()
        args.auto_approve = False
        remove_duplicates(duplicate_extensions, latest_versions, extensions_path, args)
        mock_makedirs.assert_not_called()
        mock_move.assert_not_called()

    @patch('os.makedirs')
    @patch('shutil.move')
    @patch('builtins.input')
    def test_remove_duplicates_no_duplicates(self, mock_input, mock_move, mock_makedirs):
        mock_input.return_value = "yes"
        duplicate_extensions = {}
        latest_versions = {}
        extensions_path = '/path/to/extensions'
        args = unittest.mock.MagicMock()
        args.auto_approve = True
        remove_duplicates(duplicate_extensions, latest_versions, extensions_path, args)
        mock_makedirs.assert_not_called()
        mock_move.assert_not_called()


if __name__ == '__main__':
    unittest.main()