import pathlib

# --- Configuration ---
PROJECT_NAME = "lexi_assignment"

# Define the project structure as a dictionary
# Keys are folder/file names. Dictionaries represent subfolders.
STRUCTURE = {
    "app": {
        "__init__.py": None,
        "main.py": None,
        "models.py": None,
        "services": {
            "__init__.py": None,
            "jagriti_scraper.py": None
        },
        "routers": {
            "__init__.py": None,
            "cases.py": None,
            "general.py": None
        }
    },
    "requirements.txt": None,
    ".gitignore": None
}

# --- Script ---
def create_project_structure(base_path, structure_dict):
    """
    Recursively creates folders and empty files based on a dictionary.
    """
    for name, content in structure_dict.items():
        current_path = base_path / name
        if content is None:  # It's a file
            print(f"  📄 Creating file: {current_path}")
            current_path.touch()
        else:  # It's a directory
            print(f"📁 Creating directory: {current_path}")
            current_path.mkdir(exist_ok=True)
            create_project_structure(current_path, content)

# Main execution
if __name__ == "__main__":
    project_path = pathlib.Path.cwd() / PROJECT_NAME
    
    if project_path.exists():
        print(f"⚠️  Project folder '{PROJECT_NAME}' already exists. Aborting.")
    else:
        print(f"🚀 Starting project setup for '{PROJECT_NAME}'...")
        project_path.mkdir()
        create_project_structure(project_path, STRUCTURE)
        print("\n✅ Project structure created successfully!")