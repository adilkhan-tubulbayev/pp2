# For Loop Continue - W3Schools Examples
# The continue statement stops the current iteration and continues with the next

# Example 1: Skip banana
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        continue
    print(x)

# Example 2: Skip even numbers
for x in range(10):
    if x % 2 == 0:
        continue
    print(x)

# Example 3: Skip specific indices
colors = ["red", "green", "blue", "yellow", "purple"]
for i in range(len(colors)):
    if i == 1 or i == 3:
        continue
    print(f"Index {i}: {colors[i]}")

# Example 4: Process only positive numbers
numbers = [1, -2, 3, -4, 5, -6]
for num in numbers:
    if num < 0:
        continue
    print(f"Processing positive number: {num}")
