"""
Script for testing purposes. Run this script to produce Read and write operations
"""

print("Type anything to be written to output.txt")
print("Type 'exit' to quit")
with open("output.txt", "w") as f:
    buf = input("Your input: ")
    while buf != "exit":
        f.write(buf+"\n")
        f.flush()
        buf = input("Your input: ")