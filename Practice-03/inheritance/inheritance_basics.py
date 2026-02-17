# Create a parent class
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

# Use the Person class to create an object, and then execute the printname method
x = Person("John", "Doe")
x.printname()


# Create a child class that inherits from Person
class Student(Person):
  pass

# Use the Student class to create an object - it inherits __init__ and printname from Person
x = Student("Mike", "Olsen")
x.printname()
