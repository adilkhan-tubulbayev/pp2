# While Loop Break - W3Schools Examples
# The break statement stops the loop even if the while condition is true

# Example 1: Break when i equals 3
i = 1
while i < 6:
    print(i)
    if i == 3:
        break
    i += 1

# Example 2: Search for a value and break when found
numbers = [1, 5, 8, 3, 9, 2]
target = 8
index = 0
while index < len(numbers):
    if numbers[index] == target:
        print(f"Found {target} at index {index}")
        break
    index += 1

# Example 3: Break on user condition simulation
count = 0
while True:  # Infinite loop
    count += 1
    print(f"Iteration {count}")
    if count >= 5:
        print("Breaking out of loop")
        break
