import unittest
import os
import shutil
from unittest.mock import patch, mock_open
import argparse
import semver
from main import (
    get_extension_data,
    find_duplicates,
    get_latest_versions,
    show_report,
    remove_duplicates,
    main,
)


class TestGetExtensionData(unittest.TestCase):
    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_valid_versions(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = [
            "my-extension-1.0.0",
            "another-extension-2.1.1",
        ]
        mock_isdir.side_effect = [True, True]
        expected_data = {
            "my-extension": [semver.VersionInfo(1, 0, 0)],
            "another-extension": [semver.VersionInfo(2, 1, 1)],
        }
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_no_versions(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ["my-extension", "another-extension"]
        mock_isdir.side_effect = [True, True]
        expected_data = {
            "my-extension": [],
            "another-extension": [],
        }
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_mixed_versions(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = [
            "my-extension-1.0.0",
            "another-extension",
            "third-extension-0.1.0",
        ]
        mock_isdir.side_effect = [True, True, True]
        expected_data = {
            "my-extension": [semver.VersionInfo(1, 0, 0)],
            "another-extension": [],
            "third-extension": [semver.VersionInfo(0, 1, 0)],
        }
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_non_extension_dirs(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ["my-extension-1.0.0", "not-an-extension", "another-extension-2.0.0"]
        mock_isdir.side_effect = [True, True, True]
        expected_data = {
            "my-extension": [semver.VersionInfo(1, 0, 0)],
            "not-an-extension": [],
            "another-extension": [semver.VersionInfo(2, 0, 0)],
        }
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_empty_path(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = []
        mock_isdir.return_value = False
        expected_data = {}
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_invalid_version_format(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ["my-extension-v1.0.0"]
        mock_isdir.side_effect = [True]
        expected_data = {"my-extension-v1.0.0": []}
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_extension_data_multiple_versions(self, mock_isdir, mock_listdir):
        mock_listdir.return_value = ["my-extension-1.0.0", "my-extension-1.1.0", "my-extension-1.2.0"]
        mock_isdir.side_effect = [True, True, True]
        expected_data = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
                semver.VersionInfo(1, 2, 0),
            ]
        }
        result = get_extension_data("extensions_path")
        self.assertEqual(result, expected_data)


class TestFindDuplicates(unittest.TestCase):
    def test_find_duplicates_with_duplicates(self):
        extension_data = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ],
            "another-extension": [semver.VersionInfo(2, 0, 0)],
        }
        expected_duplicates = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ]
        }
        result = find_duplicates(extension_data)
        self.assertEqual(result, expected_duplicates)

    def test_find_duplicates_no_duplicates(self):
        extension_data = {
            "my-extension": [semver.VersionInfo(1, 0, 0)],
            "another-extension": [semver.VersionInfo(2, 0, 0)],
        }
        expected_duplicates = {}
        result = find_duplicates(extension_data)
        self.assertEqual(result, expected_duplicates)

    def test_find_duplicates_empty_data(self):
        extension_data = {}
        expected_duplicates = {}
        result = find_duplicates(extension_data)
        self.assertEqual(result, expected_duplicates)


class TestGetLatestVersions(unittest.TestCase):
    def test_get_latest_versions_with_duplicates(self):
        duplicate_extensions = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ],
            "another-extension": [
                semver.VersionInfo(2, 0, 0),
                semver.VersionInfo(1, 9, 0),
            ],
        }
        expected_latest = {
            "my-extension": semver.VersionInfo(1, 1, 0),
            "another-extension": semver.VersionInfo(2, 0, 0),
        }
        result = get_latest_versions(duplicate_extensions)
        self.assertEqual(result, expected_latest)

    def test_get_latest_versions_no_duplicates(self):
        duplicate_extensions = {}
        expected_latest = {}
        result = get_latest_versions(duplicate_extensions)
        self.assertEqual(result, expected_latest)


class TestShowReport(unittest.TestCase):
    @patch("builtins.print")
    def test_show_report_with_duplicates(self, mock_print):
        duplicate_extensions = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ]
        }
        latest_versions = {"my-extension": semver.VersionInfo(1, 1, 0)}
        show_report(duplicate_extensions, latest_versions)
        mock_print.assert_called_with(
            "* my-extension (Latest: 1.1.0, Old: 1.0.0)"
        )

    @patch("builtins.print")
    def test_show_report_no_duplicates(self, mock_print):
        duplicate_extensions = {}
        latest_versions = {}
        show_report(duplicate_extensions, latest_versions)
        mock_print.assert_called_with("No duplicate extensions found.")

    @patch("builtins.print")
    def test_show_report_latest_only(self, mock_print):
        duplicate_extensions = {"my-extension": [semver.VersionInfo(1, 1, 0)]}
        latest_versions = {"my-extension": semver.VersionInfo(1, 1, 0)}
        show_report(duplicate_extensions, latest_versions)
        mock_print.assert_called_with("* my-extension (Latest version: 1.1.0 - no older duplicates)")


class TestRemoveDuplicates(unittest.TestCase):
    @patch("os.makedirs")
    @patch("shutil.move")
    @patch("builtins.input")
    def test_remove_duplicates_auto_approve(
        self, mock_input, mock_move, mock_makedirs
    ):
        mock_input.return_value = "yes"
        duplicate_extensions = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ]
        }
        latest_versions = {"my-extension": semver.VersionInfo(1, 1, 0)}
        extensions_path = "extensions_path"
        args = argparse.Namespace(auto_approve=True)
        remove_duplicates(
            duplicate_extensions, latest_versions, extensions_path, args
        )
        mock_makedirs.assert_called_once_with("old_versions", exist_ok=True)
        mock_move.assert_called_once_with(
            "extensions_path\\my-extension-1.0.0", "old_versions\\my-extension-1.0.0"
        )

    @patch("os.makedirs")
    @patch("shutil.move")
    @patch("builtins.input")
    def test_remove_duplicates_user_approve(
        self, mock_input, mock_move, mock_makedirs
    ):
        mock_input.return_value = "yes"
        duplicate_extensions = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ]
        }
        latest_versions = {"my-extension": semver.VersionInfo(1, 1, 0)}
        extensions_path = "extensions_path"
        args = argparse.Namespace(auto_approve=False)
        remove_duplicates(
            duplicate_extensions, latest_versions, extensions_path, args
        )
        mock_makedirs.assert_called_once_with("old_versions", exist_ok=True)
        mock_move.assert_called_once_with(
            "extensions_path\\my-extension-1.0.0", "old_versions\\my-extension-1.0.0"
        )

    @patch("os.makedirs")
    @patch("shutil.move")
    @patch("builtins.input")
    def test_remove_duplicates_user_decline(
        self, mock_input, mock_move, mock_makedirs
    ):
        mock_input.return_value = "no"
        duplicate_extensions = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ]
        }
        latest_versions = {"my-extension": semver.VersionInfo(1, 1, 0)}
        extensions_path = "extensions_path"
        args = argparse.Namespace(auto_approve=False)
        remove_duplicates(
            duplicate_extensions, latest_versions, extensions_path, args
        )
        mock_makedirs.assert_not_called()
        mock_move.assert_not_called()

    @patch("os.makedirs")
    @patch("shutil.move")
    @patch("builtins.input")
    def test_remove_duplicates_no_duplicates(
        self, mock_input, mock_move, mock_makedirs
    ):
        duplicate_extensions = {}
        latest_versions = {}
        extensions_path = "extensions_path"
        args = argparse.Namespace(auto_approve=False)
        remove_duplicates(
            duplicate_extensions, latest_versions, extensions_path, args
        )
        mock_makedirs.assert_not_called()
        mock_move.assert_not_called()

    @patch("os.makedirs")
    @patch("shutil.move")
    @patch("builtins.input")
    def test_remove_duplicates_move_error(
        self, mock_input, mock_move, mock_makedirs
    ):
        mock_input.return_value = "yes"
        mock_move.side_effect = Exception("Move failed")
        duplicate_extensions = {
            "my-extension": [
                semver.VersionInfo(1, 0, 0),
                semver.VersionInfo(1, 1, 0),
            ]
        }
        latest_versions = {"my-extension": semver.VersionInfo(1, 1, 0)}
        extensions_path = "extensions_path"
        args = argparse.Namespace(auto_approve=True)
        remove_duplicates(
            duplicate_extensions, latest_versions, extensions_path, args
        )
        mock_makedirs.assert_called_once_with("old_versions", exist_ok=True)
        mock_move.assert_called_once_with(
            "extensions_path\\my-extension-1.0.0", "old_versions\\my-extension-1.0.0"
        )


class TestMain(unittest.TestCase):
    @patch("main.get_extension_data")
    @patch("main.find_duplicates")
    @patch("main.get_latest_versions")
    @patch("main.show_report")
    @patch("main.remove_duplicates")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_function_calls(
        self,
        mock_parse_args,
        mock_remove_duplicates,
        mock_show_report,
        mock_get_latest_versions,
        mock_find_duplicates,
        mock_get_extension_data,
    ):
        mock_parse_args.return_value = argparse.Namespace(
            extensions_path="extensions_path", auto_approve=True
        )
        main()
        mock_get_extension_data.assert_called_once_with("extensions_path")
        mock_find_duplicates.assert_called_once()
        mock_get_latest_versions.assert_called_once()
        mock_show_report.assert_called_once()
        mock_remove_duplicates.assert_called_once()

    @patch("main.get_extension_data")
    @patch("main.find_duplicates")
    @patch("main.get_latest_versions")
    @patch("main.show_report")
    @patch("main.remove_duplicates")
    @patch("argparse.ArgumentParser.parse_args")
    def test_main_function_calls_with_auto_approve_false(
        self,
        mock_parse_args,
        mock_remove_duplicates,
        mock_show_report,
        mock_get_latest_versions,
        mock_find_duplicates,
        mock_get_extension_data,
    ):
        mock_parse_args.return_value = argparse.Namespace(
            extensions_path="extensions_path", auto_approve=False
        )
        main()
        mock_get_extension_data.assert_called_once_with("extensions_path")
        mock_find_duplicates.assert_called_once()
        mock_get_latest_versions.assert_called_once()
        mock_show_report.assert_called_once()
        mock_remove_duplicates.assert_called_once()


if __name__ == "__main__":
    unittest.main()