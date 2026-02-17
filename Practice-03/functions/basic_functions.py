# Creating and calling a function
def my_function():
  print("Hello from a function")

my_function()


# Calling a function multiple times
def my_function():
  print("Hello from a function")

my_function()
my_function()
my_function()


# Without functions - repetitive code
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)


# With functions - reusable code
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))


# Return value from a function
def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)


# Using return value directly
def get_greeting():
  return "Hello from a function"

print(get_greeting())


# The pass statement - empty function definition
def my_function():
  pass
