import tempfile
import shutil
import os
import fnmatch

source_path = "/Users/timglasgow/Downloads/3229478DC190B24900C6F3A1C514AF18.CT.FU" # Replace with your source directory
exclude_patterns = ["rt*.dcm"]

def ignore_func(directory, contents):
    ignored_items = []
    for pattern in exclude_patterns:
        if pattern.endswith('/'):
            dir_name = pattern.rstrip('/')
            if dir_name in contents and os.path.isdir(os.path.join(directory, dir_name)):
                ignored_items.append(dir_name)
        elif '*' in pattern or '?' in pattern:
            ignored_items.extend(
                item for item in contents if fnmatch.fnmatch(item, pattern)
            )
        elif pattern in contents and os.path.isfile(os.path.join(directory, pattern)):
            ignored_items.append(pattern)
    return ignored_items

# try:
#     with tempfile.TemporaryDirectory() as temp_dir:
#         print(f"Temporary directory created at: {temp_dir}")
#         shutil.copytree(source_path, temp_dir, ignore=ignore_func, dirs_exist_ok=True)
#         print(f"Contents of '{source_path}' copied to '{temp_dir}', excluding specified patterns.")
# 
#         # You can now work with the contents of temp_dir
#         # For example, list its contents:
#         print("\nContents of temporary directory:")
#         for root, dirs, files in os.walk(temp_dir):
#             level = root.replace(temp_dir, '').count(os.sep)
#             indent = ' ' * 4 * (level)
#             print(f'{indent}{os.path.basename(root)}/')
#             subindent = ' ' * 4 * (level + 1)
#             for f in files:
#                 print(f'{subindent}{f}')
# 
# except FileNotFoundError:
#     print(f"Error: Source path '{source_path}' not found.")
# except Exception as e:
#     print(f"An error occurred: {e}")