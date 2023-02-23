
import os

with open("another_test.py",'w') as f:
    print("""
a=4
print(f"{a+2}")
""",file=f)
