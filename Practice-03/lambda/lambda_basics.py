# Lambda - add 10 to argument a, and return the result
x = lambda a : a + 10
print(x(5))


# Lambda - multiply argument a with argument b and return the result
x = lambda a, b : a * b
print(x(5, 6))


# Lambda - summarize argument a, b, and c and return the result
x = lambda a, b, c : a + b + c
print(x(5, 6, 2))


# Lambda inside a function - doubler
def myfunc(n):
  return lambda a : a * n

mydoubler = myfunc(2)

print(mydoubler(11))


# Lambda inside a function - tripler
def myfunc(n):
  return lambda a : a * n

mytripler = myfunc(3)

print(mytripler(11))


# Lambda inside a function - both doubler and tripler
def myfunc(n):
  return lambda a : a * n

mydoubler = myfunc(2)
mytripler = myfunc(3)

print(mydoubler(11))
print(mytripler(11))
