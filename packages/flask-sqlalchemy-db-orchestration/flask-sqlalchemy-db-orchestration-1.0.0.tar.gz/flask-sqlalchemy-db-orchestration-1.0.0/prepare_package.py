import os
import shutil

def copy_files_to_package():
    """
    Copy all necessary files to the package directory
    """
    source_dir = os.getcwd()
    package_dir = os.path.join(source_dir, "flask_sqlalchemy_db_orchestration")
    
    # Directories to copy
    dirs_to_copy = ["Logix", "Models", "Utils"]
    
    # Files to copy
    files_to_copy = ["DbCreate.py", "DbInit.py", "DbMigrade.py", "Requirements.txt", "README.md", "CHANGELOG.md", "LICENSE"]
    
    # Copy directories
    for dir_name in dirs_to_copy:
        src_path = os.path.join(source_dir, dir_name)
        dst_path = os.path.join(package_dir, dir_name)
        
        if os.path.exists(src_path):
            print(f"Copying directory: {dir_name}")
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
    
    # Copy files
    for file_name in files_to_copy:
        src_path = os.path.join(source_dir, file_name)
        dst_path = os.path.join(package_dir, file_name)
        
        if os.path.exists(src_path):
            print(f"Copying file: {file_name}")
            shutil.copy2(src_path, dst_path)

if __name__ == "__main__":
    copy_files_to_package()
    print("Package preparation completed!")
