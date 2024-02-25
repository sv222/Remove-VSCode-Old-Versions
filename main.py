import argparse  # Importing the argparse library for command line arguments
import os  # Importing the os library for interacting with the operating system
import semver  # Importing the semver library for parsing semantic version strings


def get_extension_data(extensions_path):
    """
    Function to retrieve extension data from a given directory.

    Args:
        extensions_path (str): Path to the directory containing extensions.

    Returns:
        dict: A dictionary containing extension names as keys and lists of semantic versions as values.
    """
    extension_data = {}
    for extension in os.listdir(extensions_path):  # Iterate through each file/directory in the extensions directory
        extension_path = os.path.join(extensions_path, extension)  # Create full path to the extension
        if os.path.isdir(extension_path):  # Check if the current item is a directory
            try:
                name, version = extension.rsplit("-",
                                                 1)  # Split the filename at the last "-" to separate name and version
                version = semver.VersionInfo.parse(version)  # Parse the version string as semantic version
                extension_data.setdefault(name, []).append(
                    version)  # Store the version in the dictionary under the extension name
            except ValueError as e:
                print(f"Error parsing version for {extension}: {e}. Skipping.")
            except AttributeError:
                print(f"Error parsing version for {extension}: Invalid format. Skipping.")
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
        duplicate_extensions (dict): A dictionary containing duplicate extension names as keys and their versions as values.
        latest_versions (dict): A dictionary containing duplicate extension names as keys and their latest versions as values.
    """
    print("Duplicate extensions (excluding latest versions):")
    for name, versions in duplicate_extensions.items():
        old_versions = [v for v in versions if v != latest_versions[name]]
        if old_versions:
            print(f"* {name} ({', '.join(str(v) for v in old_versions)})")


def remove_duplicates(duplicate_extensions, latest_versions, extensions_path):
    """
    Function to remove old duplicates of extensions.

    Args:
        duplicate_extensions (dict): A dictionary containing duplicate extension names as keys and their versions as values.
        latest_versions (dict): A dictionary containing duplicate extension names as keys and their latest versions as values.
        extensions_path (str): Path to the directory containing extensions.
    """
    action_for_duplicates = input("Remove old duplicates? (yes/no): ").lower() == "yes"
    if action_for_duplicates:
        os.makedirs("old_versions", exist_ok=True)
        for name, versions in duplicate_extensions.items():
            for version in versions:
                if version != latest_versions[name]:
                    old_extension_path = os.path.join(extensions_path, f"{name}-{version}")
                    new_extension_path = os.path.join("old_versions", f"{name}-{version}")
                    os.renames(old_extension_path, new_extension_path)
                    print(f"Moved {old_extension_path} to {new_extension_path}")
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
