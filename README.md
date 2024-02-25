# Remove old versions / duplicate extensions for VS Code

## Why the script:

The essence of the problem is that when you update extensions in VS Code, old versions are not deleted, but remain and occupy free space. If you have a large number of extensions, it is quite problematic to delete them manually.

## What the script does:

This Python script helps you identify and manage duplicate extensions within your VS Code extensions directory. It can:

* Find duplicate extensions based on their names and semantic versions.
* Display a report of duplicate extensions, excluding the latest versions.
* Optionally remove old duplicates, moving them to a separate folder.

## Installation and Usage

1. **Clone this repository:**
    ```bash
    git clone https://github.com/sv222/RemoveVSCodeOldVersions && cd RemoveVSCodeOldVersions
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Run the script:**
    ```bash
    python main.py "C:\Users\<USERNAME>\.vscode\extensions"  # Replace with your actual path to your VS Code extensions directory.
    ```
4. **Follow the prompts to view the report and choose whether to remove duplicates.**

## Key Features

* **Semantic version parsing:** Uses the `semver` library to accurately parse version strings.
* **Clear reporting:** Provides a user-friendly report of duplicate extensions and their versions.
* **Customizable target directory:** You can easily provide the path to your extensions directory via the `extensions_path` argument.

## Contributing
Contributions are welcome! Please open an issue or pull request on the [GitHub repository](https://github.com/sv222/RemoveVSCodeOldVersions).

## License
This project is licensed under the MIT License.
