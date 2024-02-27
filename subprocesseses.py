import psutil

# Get the current process
current_process = psutil.Process()

# Get the child processes
children = current_process.children(recursive=True)

# Print the PID of each child process
for child in children:
    print(f'Child pid is {child.pid}')
