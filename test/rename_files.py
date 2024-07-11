import os
import re

def sanitize_filename(filename):
    # 将非法字符（例如空格）替换成下划线
    return re.sub(r'[\s]', '_', filename)

def rename_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            sanitized_filename = sanitize_filename(filename)
            if sanitized_filename != filename:
                original_path = os.path.join(root, filename)
                new_path = os.path.join(root, sanitized_filename)
                print(f'Renaming: {original_path} -> {new_path}')
                os.rename(original_path, new_path)
        for dirname in dirs:
            sanitized_dirname = sanitize_filename(dirname)
            if sanitized_dirname != dirname:
                original_path = os.path.join(root, dirname)
                new_path = os.path.join(root, sanitized_dirname)
                print(f'Renaming: {original_path} -> {new_path}')
                os.rename(original_path, new_path)

if __name__ == "__main__":
    directory = input("请输入目录路径: ")
    if os.path.isdir(directory):
        rename_files_in_directory(directory)
    else:
        print("输入的路径不是一个有效的目录。")
