# While Loop - W3Schools Examples
# With the while loop we can execute a set of statements as long as a condition is true

# Example 1: Basic while loop
i = 1
while i < 6:
    print(i)
    i += 1

# Example 2: While loop with else statement
# The else block executes once when the condition becomes false
i = 1
while i < 6:
    print(i)
    i += 1
else:
    print("i is no longer less than 6")

# Example 3: Counting down
count = 5
while count > 0:
    print(count)
    count -= 1
print("Blast off!")

# Example 4: Sum numbers using while loop
total = 0
number = 1
while number <= 10:
    total += number
    number += 1
print("Sum of 1 to 10:", total)
