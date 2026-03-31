# Open and read the entire file
f = open("demofile.txt")
print(f.read())

# Read only the first 5 characters
with open("demofile.txt") as f:
  print(f.read(5))

# Read one line
with open("demofile.txt") as f:
  print(f.readline())

# Read two lines
with open("demofile.txt") as f:
  print(f.readline())
  print(f.readline())

# Loop through the file line by line
with open("demofile.txt") as f:
  for x in f:
    print(x)

# Close file after reading
f = open("demofile.txt")
print(f.readline())
f.close()
