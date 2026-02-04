# If Else Statement - W3Schools Examples
# The else keyword catches anything which isn't caught by the preceding conditions

# Example 1: Simple if-else
a = 200
b = 33
if b > a:
    print("b is greater than a")
else:
    print("b is not greater than a")

# Example 2: Even or odd number check
number = 7
if number % 2 == 0:
    print("The number is even")
else:
    print("The number is odd")

# Example 3: Input validation with else as fallback
username = "Emil"
if len(username) > 0:
    print(f"Welcome, {username}!")
else:
    print("Error: Username cannot be empty")

# Example 4: Check if number is positive or not
num = -5
if num >= 0:
    print("Number is positive or zero")
else:
    print("Number is negative")
