import re

# 1. Match a string that has an 'a' followed by zero or more 'b's
def exercise1(text):
    pattern = "ab*"
    if re.search(pattern, text):
        return "Found a match!"
    else:
        return "Not matched!"

print("Exercise 1:")
print(exercise1("ac"))
print(exercise1("abc"))
print(exercise1("abbc"))


# 2. Match a string that has an 'a' followed by two to three 'b'
def exercise2(text):
    pattern = "ab{2,3}"
    if re.search(pattern, text):
        return "Found a match!"
    else:
        return "Not matched!"

print("\nExercise 2:")
print(exercise2("ab"))
print(exercise2("abb"))
print(exercise2("abbb"))


# 3. Find sequences of lowercase letters joined with an underscore
def exercise3(text):
    pattern = "[a-z]+_[a-z]+"
    return re.findall(pattern, text)

print("\nExercise 3:")
print(exercise3("aab_cbbbc"))
print(exercise3("aab_Abbbc"))
print(exercise3("Aaab_Abbbc"))


# 4. Find sequences of one upper case letter followed by lower case letters
def exercise4(text):
    pattern = "[A-Z][a-z]+"
    return re.findall(pattern, text)

print("\nExercise 4:")
print(exercise4("AaBbGg"))
print(exercise4("Python"))
print(exercise4("HELLO"))


# 5. Match a string that has an 'a' followed by anything, ending in 'b'
def exercise5(text):
    pattern = "a.*b$"
    if re.search(pattern, text):
        return "Found a match!"
    else:
        return "Not matched!"

print("\nExercise 5:")
print(exercise5("aabbbb"))
print(exercise5("aabAbbbc"))
print(exercise5("accddbbjjjb"))


# 6. Replace all occurrences of space, comma, or dot with a colon
def exercise6(text):
    pattern = "[ ,.]"
    return re.sub(pattern, ":", text)

print("\nExercise 6:")
print(exercise6("Python Exercises, PHP exercises."))


# 7. Convert snake case string to camel case string
def exercise7(text):
    components = text.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

print("\nExercise 7:")
print(exercise7("python_program"))
print(exercise7("hello_world_test"))


# 8. Split a string at uppercase letters
def exercise8(text):
    return re.findall("[A-Z][^A-Z]*", text)

print("\nExercise 8:")
print(exercise8("PythonProgramLanguage"))
print(exercise8("HelloWorldTest"))


# 9. Insert spaces between words starting with capital letters
def exercise9(text):
    return re.sub(r"([A-Z])", r" \1", text).strip()

print("\nExercise 9:")
print(exercise9("PythonProgramLanguage"))
print(exercise9("HelloWorldTest"))


# 10. Convert a given camel case string to snake case
def exercise10(text):
    result = re.sub(r"([A-Z])", r"_\1", text).lower()
    if result.startswith("_"):
        result = result[1:]
    return result

print("\nExercise 10:")
print(exercise10("PythonProgram"))
print(exercise10("camelCaseString"))
