import os
import shutil

# Create a sample file to work with
with open("demofile.txt", "w") as f:
  f.write("This is a demo file for copy and delete operations.")

# Copy a file using shutil.copy()
shutil.copy("demofile.txt", "demofile_backup.txt")
print("File copied successfully")

# Read the backup to verify
with open("demofile_backup.txt") as f:
  print(f.read())

# Check if file exists before deleting
if os.path.exists("demofile.txt"):
  os.remove("demofile.txt")
  print("demofile.txt removed")
else:
  print("The file does not exist")

# Clean up backup file
if os.path.exists("demofile_backup.txt"):
  os.remove("demofile_backup.txt")
  print("demofile_backup.txt removed")

# Clean up myfile.txt if it was created
if os.path.exists("myfile.txt"):
  os.remove("myfile.txt")
