# Parent class
class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)


# Child class with added method - overrides inherited behavior by adding welcome()
class Student(Person):
  def __init__(self, fname, lname, year):
    super().__init__(fname, lname)
    self.graduationyear = year

  def welcome(self):
    print("Welcome", self.firstname, self.lastname, "to the class of", self.graduationyear)

x = Student("Mike", "Olsen", 2019)
x.welcome()


# Polymorphism with inheritance - child classes override parent's move() method
class Vehicle:
  def __init__(self, brand, model):
    self.brand = brand
    self.model = model

  def move(self):
    print("Move!")

class Car(Vehicle):
  pass

class Boat(Vehicle):
  def move(self):
    print("Sail!")

class Plane(Vehicle):
  def move(self):
    print("Fly!")

car1 = Car("Ford", "Mustang")       # Car does not override move()
boat1 = Boat("Ibiza", "Touring 20") # Boat overrides move() to print "Sail!"
plane1 = Plane("Boeing", "747")     # Plane overrides move() to print "Fly!"

for x in (car1, boat1, plane1):
  print(x.brand)
  print(x.model)
  x.move()
