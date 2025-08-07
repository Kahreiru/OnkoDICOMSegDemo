import tempfile
import shutil
import os
import fnmatch

exclude_patterns = ["rt*.dcm"]

def ignore_func(directory, contents):
    """Filters files and directories to be ignored during copy operations.

    This function checks each item in 'contents' against a list of exclude patterns
    and returns a list of items that should be ignored.
    """
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