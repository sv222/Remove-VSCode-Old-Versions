import argparse  # Importing the argparse library for command line arguments
import os  # Importing the os library for interacting with the operating system
import semver  # Importing the semver library for parsing semantic version strings
import shutil # Importing shutil for moving files

def get_extension_data(extensions_path):
    """
    Function to retrieve extension data from a given directory.

    Args:
        extensions_path (str): Path to the directory containing extensions.

    Returns:
        dict: A dictionary containing extension names as keys and lists of semantic versions as values.
    """
    extension_data = {}
    for extension in os.listdir(extensions_path):
        extension_path = os.path.join(extensions_path, extension)
        if os.path.isdir(extension_path):
            try:
                name, version_str = extension.rsplit("-", 1)
                version = semver.VersionInfo.parse(version_str)
                extension_data.setdefault(name, []).append(version)
            except ValueError as e:
                print(f"ValueError parsing version for extension '{extension}': {e}. Skipping.")
            except AttributeError:
                print(f"AttributeError parsing version for extension '{extension}'. Invalid format. Skipping.")
            except Exception as e:
                print(f"Unexpected error processing extension '{extension}': {e}. Skipping.")
    return extension_data


def find_duplicates(extension_data):
    """
    Function to identify duplicate extensions from the extension data.

    Args:
        extension_data (dict): A dictionary containing extension names as keys and lists of semantic versions as values.

    Returns:
        dict: A dictionary containing duplicate extension names as keys and their versions as values.
    """
    duplicate_extensions = {name: versions for name, versions in extension_data.items() if len(versions) > 1}
    return duplicate_extensions


def get_latest_versions(duplicate_extensions):
    """
    Function to retrieve the latest versions of duplicate extensions.

    Args:
        duplicate_extensions (dict): A dictionary containing duplicate extension names as keys and their versions as values.

    Returns:
        dict: A dictionary containing duplicate extension names as keys and their latest versions as values.
    """
    latest_versions = {name: max(versions) for name, versions in duplicate_extensions.items()}
    return latest_versions

def show_report(duplicate_extensions, latest_versions):
    """
    Function to display a report on duplicate extensions and their versions.

    Args:
        duplicate_extensions (dict): Dictionary of duplicate extensions.
        latest_versions (dict): Dictionary of latest versions.
    """
    print("Duplicate extensions Report:")
    for name, versions in duplicate_extensions.items():
        latest_version = latest_versions[name]
        old_versions = [v for v in versions if v != latest_version]
        if old_versions:
            print(f"* {name} (Latest: {latest_version}, Old: {', '.join(str(v) for v in old_versions)})")
        else:
            print(f"* {name} (Latest version: {latest_version} - no older duplicates)")



def remove_duplicates(duplicate_extensions, latest_versions, extensions_path):
    """
    Function to remove old duplicates of extensions.

    Args:
        duplicate_extensions (dict): Dictionary of duplicate extensions.
        latest_versions (dict): Dictionary of latest versions for duplicates.
        extensions_path (str): Path to the extensions directory.
    """
    action_for_duplicates = input("Remove old duplicates? (yes/no): ").lower() == "yes"
    if action_for_duplicates:
        old_versions_dir = "old_versions"
        os.makedirs(old_versions_dir, exist_ok=True)
        for name, versions in duplicate_extensions.items():
            latest_version = latest_versions[name]
            for version in versions:
                if version != latest_version:
                    old_extension_path = os.path.join(extensions_path, f"{name}-{version}")
                    new_extension_path = os.path.join(old_versions_dir, f"{name}-{version}")
                    try:
                        shutil.move(old_extension_path, new_extension_path)
                        print(f"Moved '{old_extension_path}' to '{new_extension_path}'")
                    except Exception as e:
                        print(f"Error moving '{old_extension_path}' to '{new_extension_path}': {e}")
    else:
        print("No duplicates removed.")


def main():
    """
    Main function to execute the extension management process.
    """
    # extensions_path = "C:\\Users\\stani\\.vscode\\extensions"
    parser = argparse.ArgumentParser(description="Manage duplicate extensions.")
    parser.add_argument("extensions_path", type=str, help="Path to the directory containing extensions")
    args = parser.parse_args()

    extensions_path = args.extensions_path  # Using the argument as the path
    extension_data = get_extension_data(extensions_path)
    duplicate_extensions = find_duplicates(extension_data)
    latest_versions = get_latest_versions(duplicate_extensions)
    show_report(duplicate_extensions, latest_versions)
    remove_duplicates(duplicate_extensions, latest_versions, extensions_path)


if __name__ == "__main__":
    main()
