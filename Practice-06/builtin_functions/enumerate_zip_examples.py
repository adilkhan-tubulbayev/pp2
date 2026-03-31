# enumerate() - loop with index
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
  print(index, fruit)

# enumerate() - start index from 1
for index, fruit in enumerate(fruits, start=1):
  print(index, fruit)

# zip() - combine two lists into pairs
names = ["Emil", "Tobias", "Linus"]
ages = [25, 22, 28]
combined = list(zip(names, ages))
print("\nZipped:", combined)

# zip() - loop through paired lists
print("\nPaired iteration:")
for name, age in zip(names, ages):
  print(f"{name} is {age} years old")

# zip() - with three lists
cities = ["Oslo", "Stockholm", "Helsinki"]
for name, age, city in zip(names, ages, cities):
  print(f"{name}, {age}, from {city}")

# sorted() - sort a list
numbers = [5, 2, 8, 1, 9, 3]
print("\nSorted:", sorted(numbers))
print("Sorted desc:", sorted(numbers, reverse=True))

# sorted() - sort strings by length
words = ["banana", "pie", "apple", "cherry"]
print("By length:", sorted(words, key=len))

# len(), sum(), min(), max()
numbers = [10, 20, 30, 40, 50]
print("\nlen:", len(numbers))
print("sum:", sum(numbers))
print("min:", min(numbers))
print("max:", max(numbers))

# Type conversion functions
print("\nint('42'):", int("42"))
print("float('3.14'):", float("3.14"))
print("str(100):", str(100))
print("list('hello'):", list("hello"))
print("bool(0):", bool(0))
print("bool(1):", bool(1))
