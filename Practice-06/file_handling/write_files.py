# Create a new file and write data to it
with open("demofile.txt", "w") as f:
  f.write("Hello! This is the first line.\n")
  f.write("This is the second line.\n")

# Read and print the file contents
with open("demofile.txt") as f:
  print(f.read())

# Append new content to the file
with open("demofile.txt", "a") as f:
  f.write("Now the file has more content!\n")

# Read the file after appending
with open("demofile.txt") as f:
  print(f.read())

# Overwrite existing content
with open("demofile.txt", "w") as f:
  f.write("Woops! I have deleted the content!")

# Read the file after overwriting
with open("demofile.txt") as f:
  print(f.read())

# Create a new file using "x" mode - fails if file already exists
try:
  f = open("myfile.txt", "x")
  f.write("New file created!")
  f.close()
except FileExistsError:
  print("The file already exists")
