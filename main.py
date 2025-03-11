import argparse
import os
import semver
import shutil

# Module level docstring - describes the purpose of the entire file.
"""
This script manages duplicate extensions within a specified directory.
It identifies extensions with multiple versions, reports the duplicates,
and provides an option to remove older versions, keeping only the latest.
The script uses semantic versioning to determine the latest version.
"""


def get_extension_data(extensions_path):
    """
    Retrieves extension data from a given directory by parsing directory names.

    This function scans the provided directory for subdirectories, attempting to
    identify extension names and their semantic versions based on directory naming conventions.
    It expects extension directories to be named like 'extension-name-version'.
    If a valid semantic version is found at the end of the directory name, it's parsed
    and associated with the extension name.

    Args:
        extensions_path (str): The path to the directory containing extension directories.

    Returns:
        dict: A dictionary where keys are extension names (str) and values are lists of
              semantic versions (semver.VersionInfo) found for each extension.
              If no version is found for an extension, it will still be included as a key
              with an empty list as its value.
    """
    extension_data = {}  # Initialize an empty dictionary to store extension data
    for extension_dir in os.listdir(extensions_path):  # Iterate through each item in the extensions directory
        extension_path = os.path.join(extensions_path, extension_dir) # Construct the full path to the extension directory
        if os.path.isdir(extension_path): # Check if the item is a directory
            name = extension_dir # Initially assume the entire directory name is the extension name
            versions = [] # Initialize an empty list to store versions for this extension
            version_str = None # Initialize version string to None

            # Attempt to parse version from the end of the directory name
            parts = extension_dir.split('-') # Split the directory name by hyphens
            for i in range(len(parts) - 1, 0, -1): # Iterate backwards through the parts to find a version string at the end
                version_str_candidate = '-'.join(parts[i:]) # Candidate version string (e.g., '1.2.3' or 'v1.2.3')
                name_candidate = '-'.join(parts[:i]) # Candidate extension name (e.g., 'my-extension')
                try:
                    semver.VersionInfo.parse(version_str_candidate) # Try to parse the candidate version string using semver
                    version_str = version_str_candidate # If parsing is successful, assign it as the version string
                    name = name_candidate # And update the extension name
                    break # Exit the loop as a version string is found
                except ValueError:
                    continue # If parsing fails, continue to the next iteration (shorter version candidate)

            extension_data.setdefault(name, []) # Ensure the extension name exists as a key in the dictionary, initialize with empty list if not
            if version_str: # If a version string was found
                try:
                    version = semver.VersionInfo.parse(version_str) # Parse the version string into a semver.VersionInfo object
                    versions.append(version) # Add the parsed version to the list of versions for this extension
                except ValueError as e: # Catch any ValueError during version parsing
                    print(f"ValueError parsing version for extension '{extension_dir}' with version string '{version_str}': {e}.") # Print an error message if version parsing fails
                extension_data[name].extend(versions) # Extend the list of versions for the extension with the newly found versions (could be more than one in future)
    return extension_data # Return the dictionary containing extension data


def find_duplicates(extension_data):
    """
    Identifies duplicate extensions based on the provided extension data.

    Duplicate extensions are defined as extensions having more than one version listed
    in the extension_data dictionary.

    Args:
        extension_data (dict): A dictionary where keys are extension names and values
                                are lists of semantic versions.

    Returns:
        dict: A dictionary containing only the duplicate extension names as keys and
              their corresponding lists of semantic versions as values.
              Returns an empty dictionary if no duplicates are found.
    """
    duplicate_extensions = { # Create a new dictionary to store duplicate extensions
        name: versions for name, versions in extension_data.items() if len(versions) > 1 # Dictionary comprehension: include only extensions with more than one version
    }
    return duplicate_extensions # Return the dictionary of duplicate extensions


def get_latest_versions(duplicate_extensions):
    """
    Determines the latest semantic version for each duplicate extension.

    For each extension listed in the duplicate_extensions dictionary, this function
    finds the maximum semantic version from its list of versions.

    Args:
        duplicate_extensions (dict): A dictionary of duplicate extensions where keys
                                      are extension names and values are lists of semantic versions.

    Returns:
        dict: A dictionary where keys are duplicate extension names and values are their
              latest semantic versions (semver.VersionInfo).
              Returns an empty dictionary if no duplicate extensions are provided.
    """
    latest_versions = { # Create a new dictionary to store the latest versions
        name: max(versions) for name, versions in duplicate_extensions.items() # Dictionary comprehension: find the maximum version for each extension
    }
    return latest_versions # Return the dictionary of latest versions


def show_report(duplicate_extensions, latest_versions):
    """
    Displays a report of duplicate extensions, highlighting the latest and older versions.

    This function prints a user-friendly report to the console, listing each duplicate extension
    and indicating its latest version and any older versions found. If no duplicates are found,
    it prints a message indicating that.

    Args:
        duplicate_extensions (dict): Dictionary of duplicate extensions (name: list of versions).
        latest_versions (dict): Dictionary of latest versions for duplicate extensions (name: latest version).
    """
    if not duplicate_extensions: # Check if there are any duplicate extensions
        print("No duplicate extensions found.") # Print message if no duplicates
    else:
        print("Duplicate extensions Report:") # Start of the report
        for name, versions in duplicate_extensions.items(): # Iterate through each duplicate extension
            latest_version = latest_versions[name] # Get the latest version for the current extension
            old_versions = [v for v in versions if v != latest_version] # List comprehension to filter out the latest version and get only older versions
            if old_versions: # If there are older versions
                print(
                    f"* {name} (Latest: {latest_version}, Old: {', '.join(str(v) for v in old_versions)})" # Print report line with latest and old versions
                )
            else:
                print(f"* {name} (Latest version: {latest_version} - no older duplicates)") # Print report line if no older duplicates


def remove_duplicates(duplicate_extensions, latest_versions, extensions_path, args):
    """
    Removes older versions of duplicate extensions, keeping only the latest version.

    This function prompts the user for confirmation before removing older versions of
    duplicate extensions, unless the '--auto-approve' argument is used.
    Older versions are moved to a subdirectory named 'old_versions' within the script's directory.

    Args:
        duplicate_extensions (dict): Dictionary of duplicate extensions (name: list of versions).
        latest_versions (dict): Dictionary of latest versions for duplicate extensions (name: latest version).
        extensions_path (str): Path to the extensions directory where duplicates are located.
        args (argparse.Namespace): Parsed command-line arguments, including auto_approve flag.
    """
    if duplicate_extensions: # Check if there are any duplicate extensions to remove
        action_for_duplicates = ( # Determine if action should be taken based on auto-approve or user input
            not args.auto_approve # If auto-approve is not enabled
            and input("Remove old duplicates? (yes/no): ").lower() == "yes" # Prompt user for confirmation
        )
        if args.auto_approve or action_for_duplicates: # If auto-approve is enabled or user approved
            old_versions_dir = "old_versions" # Define directory name for moving old versions
            os.makedirs(old_versions_dir, exist_ok=True) # Create the directory if it doesn't exist, no error if it does
            for name, versions in duplicate_extensions.items(): # Iterate through each duplicate extension
                latest_version = latest_versions[name] # Get the latest version for the current extension
                for version in versions: # Iterate through all versions of the current extension
                    if version != latest_version: # If the current version is not the latest version (i.e., it's an old version)
                        old_extension_path = os.path.join( # Construct the full path to the old extension directory
                            extensions_path, f"{name}-{version}"
                        )
                        new_extension_path = os.path.join( # Construct the new path in the 'old_versions' directory
                            old_versions_dir, f"{name}-{version}"
                        )
                        try:
                            shutil.move(old_extension_path, new_extension_path) # Move the old extension directory to the 'old_versions' directory
                            print(f"Moved '{old_extension_path}' to '{new_extension_path}'") # Print success message
                        except Exception as e: # Catch any exceptions during the move operation
                            print(
                                f"Error moving '{old_extension_path}' to '{new_extension_path}': {e}" # Print error message if move fails
                            )
        else:
            print("No duplicates removed.") # Print message if user declined to remove duplicates or auto-approve was not enabled
    else:
        pass # If no duplicate extensions, no action is needed


def main():
    """
    Main function to parse command line arguments and execute the extension management process.

    This function sets up the argument parser, parses command-line arguments for the extensions path
    and auto-approve option, and then orchestrates the process of finding, reporting, and removing
    duplicate extensions.
    """
    parser = argparse.ArgumentParser(description="Manage duplicate extensions.") # Create argument parser with a description
    parser.add_argument( # Add argument for extensions path
        "extensions_path", type=str, help="Path to the directory containing extensions"
    )
    parser.add_argument( # Add argument for auto-approve flag
        "--auto-approve",
        action="store_true", # Store true if the flag is present
        help="Automatically approve removal of duplicates",
    )
    args = parser.parse_args() # Parse command-line arguments

    extensions_path = args.extensions_path # Get the extensions path from arguments
    extension_data = get_extension_data(extensions_path) # Retrieve extension data from the specified path
    duplicate_extensions = find_duplicates(extension_data) # Find duplicate extensions from the data
    latest_versions = get_latest_versions(duplicate_extensions) # Get the latest versions of the duplicate extensions
    show_report(duplicate_extensions, latest_versions) # Display a report of duplicate extensions and their versions
    remove_duplicates(duplicate_extensions, latest_versions, extensions_path, args) # Remove older versions of duplicate extensions


if __name__ == "__main__":
    main() # Execute the main function when the script is run directly