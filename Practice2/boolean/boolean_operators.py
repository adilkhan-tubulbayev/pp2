# Boolean Operators and Functions - W3Schools Examples

# Example 1: Function returning boolean
def myFunction():
    return True

print(myFunction())  # True

# Example 2: Using boolean return in conditional
def myFunction():
    return True

if myFunction():
    print("YES!")
else:
    print("NO!")

# Example 3: isinstance() function - check if object belongs to a data type
x = 200
print(isinstance(x, int))    # True
print(isinstance(x, float))  # False
print(isinstance(x, str))    # False

# Example 4: Logical operators
a = True
b = False

# and - Returns True if both statements are true
print(a and b)  # False

# or - Returns True if one of the statements is true
print(a or b)   # True

# not - Reverse the result
print(not a)    # False
print(not b)    # True
