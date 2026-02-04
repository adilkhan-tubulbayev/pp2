# Boolean Introduction - W3Schools Examples
# The bool() function evaluates values and returns True or False

# Example 1: Evaluate string and number with bool()
print(bool("Hello"))  # True - non-empty string
print(bool(15))       # True - non-zero number

# Example 2: Evaluate variables
x = "Hello"
y = 15
print(bool(x))  # True
print(bool(y))  # True

# Example 3: Truthy values - these all evaluate to True
print(bool("abc"))                      # True
print(bool(123))                        # True
print(bool(["apple", "cherry", "banana"]))  # True

# Example 4: Falsy values - these all evaluate to False
print(bool(False))  # False
print(bool(None))   # False
print(bool(0))      # False
print(bool(""))     # False - empty string
print(bool(()))     # False - empty tuple
print(bool([]))     # False - empty list
print(bool({}))     # False - empty dictionary

# Example 5: Custom class with __len__ returning 0 evaluates to False
class myclass():
    def __len__(self):
        return 0

myobj = myclass()
print(bool(myobj))  # False
