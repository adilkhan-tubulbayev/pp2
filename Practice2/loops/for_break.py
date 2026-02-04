# For Loop Break - W3Schools Examples
# The break statement stops the loop before it has looped through all items

# Example 1: Break after printing banana
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)
    if x == "banana":
        break

# Example 2: Break before printing banana
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        break
    print(x)

# Example 3: Else with break - else doesn't execute when break is triggered
for x in range(6):
    if x == 3:
        break
    print(x)
else:
    print("Finally finished!")  # This won't print because break was triggered

# Example 4: Search and break
numbers = [10, 20, 30, 40, 50]
search = 30
for num in numbers:
    if num == search:
        print(f"Found {search}!")
        break
    print(f"Checking {num}...")
