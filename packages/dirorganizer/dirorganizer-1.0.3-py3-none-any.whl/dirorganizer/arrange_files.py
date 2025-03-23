import os
import shutil
import sys

def print_separator():
    """Prints a separator line that fills the screen width dynamically."""
    try:
        terminal_width = shutil.get_terminal_size((80, 20)).columns
    except OSError:
        terminal_width = 80  # Default width if terminal size can't be determined
    print("=" * terminal_width)

def organize_files(source_path):
    """Organizes files in the given folder by their extensions."""
    source_path = os.path.abspath(source_path)

    if not os.path.exists(source_path):
        print_separator()
        print(f"\n❌ Error: Path '{source_path}' does not exist.\n")
        print_separator()
        return

    print_separator()
    print("📂 FILE ORGANIZATION STARTED 📂".center(shutil.get_terminal_size((80, 20)).columns))
    print_separator()

    new_folders = set()

    for root, _, files in os.walk(source_path):
        for file in files:
            if "." in file:
                extension = file.rsplit(".", 1)[-1]  # Extract file extension
                
                # Create folder if not already created
                folder_path = os.path.join(source_path, extension)
                if extension not in new_folders:
                    os.makedirs(folder_path, exist_ok=True)
                    new_folders.add(extension)

                # Define source and destination paths
                source_file = os.path.join(root, file)
                destination_file = os.path.join(folder_path, file)

                # Move file, checking if it already exists
                if os.path.exists(destination_file):
                    print(f" ⚠  {file} already exists in →  {destination_file}\n")
                else:
                    try:
                        shutil.move(source_file, destination_file)
                        print(f" ✔  Moved: {file.ljust(25)} → {destination_file}\n")
                    except Exception as e:
                        print(f" ✖  Error moving {file}: {e}\n")

    print_separator()
    print("✅ FILE ORGANIZATION COMPLETED ✅".center(shutil.get_terminal_size((80, 20)).columns))
    print_separator()

def main():
    """Entry point for the CLI command."""
    if len(sys.argv) < 2:
        print_separator()
        print("\n❌ Usage: arrange <folder>\n")
        print_separator()
        sys.exit(1)

    source_folder = os.path.abspath(sys.argv[1])  # Fix path handling
    organize_files(source_folder)

# This allows both direct execution and CLI execution
if __name__ == "__main__":
    main()