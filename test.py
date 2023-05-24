a= 'apple + banana * carrot + watermelon % 2'
b = '4.5'

print((b.isdigit()))
# check if b is a float
try:
    float(b)
    print("float")
except ValueError:
    print("not float")
