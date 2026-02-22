# 1. Generator that generates squares of numbers up to N
def squares_up_to(N):
    for i in range(1, N + 1):
        yield i * i

N = 5
for val in squares_up_to(N):
    print(val)


# 2. Generator to print even numbers between 0 and n in comma separated form
def even_numbers(n):
    for i in range(0, n + 1):
        if i % 2 == 0:
            yield i

n = int(input("Enter n: "))
print(",".join(str(x) for x in even_numbers(n)))


# 3. Generator for numbers divisible by 3 and 4 between 0 and n
def divisible_by_3_and_4(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input("Enter n: "))
for val in divisible_by_3_and_4(n):
    print(val)


# 4. Generator called squares to yield square of all numbers from a to b
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

for val in squares(1, 5):
    print(val)


# 5. Generator that returns all numbers from n down to 0
def countdown(n):
    while n >= 0:
        yield n
        n -= 1

for val in countdown(5):
    print(val)
