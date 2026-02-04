# If Elif Else Statement - W3Schools Examples
# The elif keyword is Python's way of saying "if the previous conditions were not true, then try this condition"

# Example 1: Basic elif usage
a = 33
b = 33
if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")

# Example 2: Multiple elif statements - Grade calculator
score = 75
if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
elif score >= 60:
    print("Grade: D")

# Example 3: Age categorization
age = 25
if age < 13:
    print("You are a child")
elif age < 20:
    print("You are a teenager")
elif age < 65:
    print("You are an adult")
elif age >= 65:
    print("You are a senior")

# Example 4: Complete if-elif-else with temperature classification
temperature = 22
if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("It's warm outside")
elif temperature > 10:
    print("It's cool outside")
else:
    print("It's cold outside!")

# Example 5: If-elif-else comparing values
a = 200
b = 33
if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")
else:
    print("a is greater than b")
