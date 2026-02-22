import math

# 1. Convert degree to radian
degree = float(input("Input degree: "))
radian = degree * (math.pi / 180)
print("Output radian:", round(radian, 6))


# 2. Calculate the area of a trapezoid
height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))
area = ((base1 + base2) / 2) * height
print("Expected Output:", area)


# 3. Calculate the area of a regular polygon
sides = int(input("Input number of sides: "))
length = float(input("Input the length of a side: "))
area = (sides * (length ** 2)) / (4 * math.tan(math.pi / sides))
print("The area of the polygon is:", round(area))


# 4. Calculate the area of a parallelogram
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))
area = base * height
print("Expected Output:", area)
