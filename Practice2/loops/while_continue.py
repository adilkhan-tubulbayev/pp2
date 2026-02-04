# While Loop Continue - W3Schools Examples
# The continue statement stops the current iteration and continues with the next

# Example 1: Skip when i equals 3
i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)

# Example 2: Print only even numbers
i = 0
while i < 10:
    i += 1
    if i % 2 != 0:  # Skip odd numbers
        continue
    print(i)

# Example 3: Skip specific values
count = 0
while count < 10:
    count += 1
    if count == 3 or count == 7:
        continue
    print(f"Count is: {count}")
