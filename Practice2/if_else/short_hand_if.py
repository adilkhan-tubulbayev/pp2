# Short Hand If / Ternary Operator - W3Schools Examples
# If you have only one statement to execute, you can put it on the same line

# Example 1: One-line if statement
a = 5
b = 2
if a > b: print("a is greater than b")

# Example 2: One-line if/else (conditional expression / ternary operator)
a = 2
b = 330
print("A") if a > b else print("B")

# Example 3: Assigning a value with if/else
a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

# Example 4: Chaining multiple conditions
a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")

# Example 5: Finding maximum value
x = 15
y = 20
max_value = x if x > y else y
print("Maximum value:", max_value)

# Example 6: Setting default values
username = ""
display_name = username if username else "Guest"
print("Welcome,", display_name)
