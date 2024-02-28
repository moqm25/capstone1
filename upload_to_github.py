import subprocess
import os

try:
    PATH = "/home/capstonei/CS492_Tasks"
    os.chdir(PATH)

    # Add all changes to staging
    subprocess.run(["git", "add", "."])

    # Prompt for commit message
    commit_message = input("Enter commit message: ")

    # Commit the changes
    subprocess.run(["git", "commit", "-m", commit_message])

    # Push to remote repository
    subprocess.run(["git", "push", "origin", "master"])
except Exception as e:
    print(f"Error with git operations: {e}")
    exit(1)