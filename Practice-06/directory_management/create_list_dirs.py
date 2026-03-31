import os

# Get current working directory
print("Current directory:", os.getcwd())

# Create a single directory
os.mkdir("test_dir")
print("Created test_dir")

# Create nested directories
os.makedirs("parent_dir/child_dir/grandchild_dir")
print("Created nested directories")

# List files and folders in current directory
print("\nContents of current directory:")
for item in os.listdir("."):
  print(" ", item)

# List contents of a specific directory
print("\nContents of parent_dir:")
for item in os.listdir("parent_dir"):
  print(" ", item)

# Find files by extension
print("\nPython files in current directory:")
for item in os.listdir("."):
  if item.endswith(".py"):
    print(" ", item)

# Remove directories (must be empty)
os.rmdir("test_dir")
print("\nRemoved test_dir")

# Remove nested directories
os.removedirs("parent_dir/child_dir/grandchild_dir")
print("Removed nested directories")
