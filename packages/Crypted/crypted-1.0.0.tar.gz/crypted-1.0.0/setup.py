import shutil
import os

# Define source and destination paths
source_dir = os.path.join(os.getcwd(), "src/Crypted")  # Assumes "Crypted" is in the current working directory
user_profile = os.getenv("USERPROFILE")  # Get the current user's profile directory
destination_dir = os.path.join(user_profile, "AppData", "Local", "Packages", "PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0", "LocalCache", "local-packages", "Python313", "site-packages")

def move_directory(src, dst):
    if not os.path.exists(src):
        print(f"Source directory '{src}' does not exist.")
        return
    
    # Ensure the destination directory exists
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    dest_path = os.path.join(dst, os.path.basename(src))
    
    try:
        shutil.move(src, dest_path)
        print(f"Successfully moved '{src}' to '{dest_path}'")
    except Exception as e:
        print(f"Error moving directory: {e}")

# Run the function
move_directory(source_dir, destination_dir)
