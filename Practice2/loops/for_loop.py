# For Loop - W3Schools Examples
# A for loop is used for iterating over a sequence

# Example 1: Basic for loop with list
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)

# Example 2: Looping through a string
for x in "banana":
    print(x)

# Example 3: Range function - basic
for x in range(6):
    print(x)

# Example 4: Range function - with start parameter
for x in range(2, 6):
    print(x)

# Example 5: Range function - with step parameter
for x in range(2, 30, 3):
    print(x)

# Example 6: Else in for loop
for x in range(6):
    print(x)
else:
    print("Finally finished!")

# Example 7: Nested loops
adj = ["red", "big", "tasty"]
fruits = ["apple", "banana", "cherry"]

for x in adj:
    for y in fruits:
        print(x, y)

# Example 8: Pass statement - empty loop placeholder
for x in [0, 1, 2]:
    pass
