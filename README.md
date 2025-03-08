# Remove old versions / duplicate extensions for VS Code

## Why the script:

When you update extensions in VS Code, older versions are not automatically deleted. These outdated versions remain in your extensions directory, consuming valuable disk space. This can become a significant issue if you have a large number of extensions, leading to increased storage usage and potentially impacting VS Code's performance. Keeping your extensions directory clean and manageable is beneficial for overall system health and responsiveness.

## What the script does:

This Python script helps you identify and manage duplicate extensions within your VS Code extensions directory. It automates the process of finding and optionally removing older versions of extensions, keeping your extensions directory tidy. The script performs the following actions:

*   **Finds duplicate extensions:** It scans your extensions directory and identifies extensions with multiple versions installed. It determines duplicates based on extension names and their semantic version numbers.
*   **Displays a report:** It generates a user-friendly report that lists duplicate extensions, excluding the latest versions. This report helps you visualize the duplicates and understand which versions are outdated.
*   **Optionally removes old duplicates:** The script provides an option to remove the older versions of the duplicate extensions. Instead of deleting the old versions, it moves them to an `old_versions` folder within the same directory as the script, providing a safety net in case you need to restore an older version.
*   **Handles errors:** The script includes error handling to gracefully manage potential issues during version parsing (e.g., `ValueError`, `AttributeError`) and file operations.

## Installation and Usage

1.  **Clone this repository:**

    ```bash
    git clone https://github.com/sv222/RemoveVSCodeOldVersions && cd RemoveVSCodeOldVersions
    ```

2.  **Create a virtual environment (recommended):**

    *   Using `conda`:

        ```bash
        conda create -n remove_vscode_ext python=3.13
        conda activate remove_vscode_ext
        ```

    *   Using `venv`:

        ```bash
        python -m venv .venv
        .\.venv\Scripts\activate  # On Windows
        # or
        source .venv/bin/activate # On Linux/macOS
        ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the script:**

    ```bash
    python main.py "C:\Users\<USERNAME>\.vscode\extensions"  # Replace <USERNAME> with your actual Windows username.
    # or
    python main.py "/Users/<USERNAME>/.vscode/extensions" # Replace <USERNAME> with your actual macOS username.
    ```

    *   Verify the path to your VS Code extensions directory. The path might vary slightly depending on your operating system and VS Code installation.
    *   Run the script periodically to keep your extensions directory clean.

5.  **Follow the prompts:** The script will display a report of duplicate extensions. You will be prompted to choose whether to remove the old duplicates.

6.  **Old versions moved:** Your old extensions will be moved to the "old\_versions" folder in the same directory as the script.

## How it Works

The script's core functionality is implemented through the following functions:

*   `get_extension_data(extensions_path)`: This function reads the contents of the extensions directory and extracts extension names and their semantic versions. It uses the `os.listdir()` function to list files and directories, and string manipulation (`rsplit()`) to separate the extension name and version.
*   `find_duplicates(extension_data)`: This function takes the extension data and identifies extensions that have more than one version.
*   `get_latest_versions(duplicate_extensions)`: This function determines the latest version for each duplicate extension using the `semver` library.
*   `show_report(duplicate_extensions, latest_versions)`: This function displays a report of the duplicate extensions and their versions, highlighting the latest versions.
*   `remove_duplicates(duplicate_extensions, latest_versions, extensions_path)`: This function handles the removal of old duplicate extensions. It prompts the user for confirmation and then moves the old extension directories to an `old_versions` folder using the `shutil.move()` function.

The script utilizes the following libraries:

*   `argparse`: For parsing command-line arguments (specifically, the extensions directory path).
*   `os`: For interacting with the operating system, such as listing files and creating directories.
*   `shutil`: For moving files and directories (used to move old extension versions).
*   `semver`: For parsing and comparing semantic version strings.

## Key Features

*   **Semantic version parsing:** Uses the `semver` library to accurately parse version strings, ensuring correct identification of the latest versions.
*   **Clear reporting:** Provides a user-friendly report of duplicate extensions and their versions, making it easy to understand the state of your extensions directory.
*   **User-defined extensions directory path:** You can easily provide the path to your extensions directory via the `extensions_path` argument.
*   **Safe removal:** Instead of deleting old extensions, the script moves them to an `old_versions` folder, allowing you to restore them if needed.
*   **Error handling:** Includes error handling to gracefully manage potential issues during version parsing and file operations.

## Contributing

Contributions are welcome! You can contribute by:

*   Reporting bugs or suggesting new features by opening an issue on the [GitHub repository](https://github.com/sv222/RemoveVSCodeOldVersions).
*   Submitting pull requests with bug fixes, improvements, or new features.
*   Improving the documentation.

## License

This project is licensed under the MIT License.

## FAQ / Troubleshooting

*   **The script throws an error.**
    *   Check the error message for clues. Common issues include incorrect file paths, missing dependencies, or invalid version strings.
    *   Ensure you have installed all dependencies using `pip install -r requirements.txt`.
    *   Verify that the path to your VS Code extensions directory is correct.
*   **Can I undo the removal of old extensions?**
    *   Yes, the script moves old extensions to an `old_versions` folder. You can manually move them back to your extensions directory to restore them.
*   **Does this script work on all operating systems?**
    *   The script should work on any operating system where Python and the required libraries are installed. The file paths in the "Installation and Usage" section provide examples for Windows and macOS.

```mermaid
graph LR
    A[Start] --> B{Get Extensions Data};
    B --> C{Find Duplicates};
    C --> D{Get Latest Versions};
    D --> E{Show Report};
    E --> F{Remove Duplicates?};
    F -- Yes --> G{Move Old Versions};
    F -- No --> H[End];
    G --> H;
