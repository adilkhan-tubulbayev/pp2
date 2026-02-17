# Parent class
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)


# Child class using parent class name to call __init__
class Student(Person):
  def __init__(self, fname, lname):
    Person.__init__(self, fname, lname)


# Child class using super() to call parent __init__ - no need to use parent class name
class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)


# Add a property to the child class
class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)
    self.graduationyear = 2019


# Add a year parameter to the child class
class Student(Person):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

x = Student("Mike", "Olsen", 2019)
print(x.graduationyear)
