import os

def print_tree(path, depth, current_depth=0):
    if current_depth > depth:
        return
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        print("  " * current_depth + "|-- " + item)
        if os.path.isdir(full_path):
            print_tree(full_path, depth, current_depth + 1)

# Укажите путь к директории и глубину
directory = r"C:\Users\HP\Desktop\test\project"
max_depth = 2
print_tree(directory, max_depth)