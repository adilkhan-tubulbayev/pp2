from functools import reduce

# map() - apply a function to each item in a list
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print("Squared:", squared)

# map() - convert list of strings to uppercase
words = ["hello", "world", "python"]
upper_words = list(map(str.upper, words))
print("Uppercase:", upper_words)

# filter() - keep only even numbers
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", even)

# filter() - keep strings longer than 3 characters
words = ["hi", "hello", "hey", "python", "go"]
long_words = list(filter(lambda x: len(x) > 3, words))
print("Long words:", long_words)

# reduce() - sum all numbers
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda x, y: x + y, numbers)
print("Sum:", total)

# reduce() - find the maximum value
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
maximum = reduce(lambda x, y: x if x > y else y, numbers)
print("Max:", maximum)

# Combining map and filter
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))
print("Squares of even numbers:", result)
