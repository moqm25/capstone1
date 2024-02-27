import os
import subprocess

# # Set the maximum file size (in bytes)
# max_size = 100 * 1024 * 1024  # 100MB

# try:
#     # Get the .gitignore file
#     with open('.gitignore', 'r') as f:
#         gitignore = [line.strip() for line in f.read().splitlines() if line.strip()]
# except Exception as e:
#     print(f"Error reading .gitignore: {e}")
#     exit(1)

# try:
#     # Walk through the repository
#     for root, dirs, files in os.walk('.', topdown=True):
#         # Modify dirs in-place to skip directories in .gitignore
#         dirs[:] = [d for d in dirs if not any(os.path.join(root, d).startswith(g) for g in gitignore)]
        
#         for name in files:
#             # Get the file path
#             file_path = os.path.join(root, name)
            
#             # Skip files in .gitignore
#             if any(file_path.startswith(g) for g in gitignore):
#                 continue
            
#             # Get the file size
#             file_size = os.path.getsize(file_path)
            
#             # If the file size is greater than the maximum size
#             if file_size > max_size:
#                 print(f'File {file_path} is larger than 100MB.')
                
#                 # Add the file to .gitignore
#                 with open('.gitignore', 'a') as f:
#                     f.write(f'\n{file_path}')
# except Exception as e:
#     print(f"Error processing files: {e}")
#     exit(1)

try:
    # Add all changes to staging
    os.system("git add .")

    # Prompt for commit message
    commit_message = input("Enter commit message: ")

    # Commit the changes
    os.system(f"git commit -m {commit_message}")

    # Push to remote repository
    os.system("git push origin master")
except Exception as e:
    print(f"Error with git operations: {e}")
    exit(1)
