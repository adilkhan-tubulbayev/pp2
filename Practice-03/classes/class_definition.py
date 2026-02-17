# Create a class with a property
class MyClass:
  x = 5


# Create an object from the class
p1 = MyClass()
print(p1.x)


# Create multiple objects from the same class
p1 = MyClass()
p2 = MyClass()
p3 = MyClass()

print(p1.x)
print(p2.x)
print(p3.x)


# The pass statement - empty class definition
class Person:
  pass


# Delete an object
p1 = MyClass()
del p1
