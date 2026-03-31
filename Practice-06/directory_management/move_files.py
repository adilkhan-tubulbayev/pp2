import os
import shutil

# Create directories for demonstration
os.makedirs("source_dir", exist_ok=True)
os.makedirs("dest_dir", exist_ok=True)

# Create a sample file in source directory
with open("source_dir/sample.txt", "w") as f:
  f.write("This is a sample file.")

# Copy file to another directory
shutil.copy("source_dir/sample.txt", "dest_dir/sample.txt")
print("File copied to dest_dir")

# Verify the copy
print("Files in dest_dir:", os.listdir("dest_dir"))

# Move file to another directory
with open("source_dir/moveme.txt", "w") as f:
  f.write("This file will be moved.")

shutil.move("source_dir/moveme.txt", "dest_dir/moveme.txt")
print("File moved to dest_dir")

# Verify the move
print("Files in source_dir:", os.listdir("source_dir"))
print("Files in dest_dir:", os.listdir("dest_dir"))

# Clean up
shutil.rmtree("source_dir")
shutil.rmtree("dest_dir")
print("\nCleaned up directories")
