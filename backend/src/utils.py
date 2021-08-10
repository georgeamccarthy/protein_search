# %%
import os.path

import requests


def load_or_download(url, filepath):

    # If the filepath given does not exist
    if not os.path.isdir(filepath):

        # Print logging messag
        print(f"{filepath} not found, downloading from {url}")

        # `urlretrieve` prior assumes directory exists, but
        # since `data` can be ignored, we need to make sure the
        # directories that came with `filepath` do exist
        res = requests.get(url)

        directories, file_path = generate_path(filepath)

        # Create the file with the given path in binary
        # Binary formats make sure no difficulty comes with encoding formats
        # which can or sometimes changes in the future
        with open(f"{directories}/{file_path}", mode="wb") as file_handler:

            # Write the content to the file, then close
            file_handler.write(res.content)

    # Return the handle to the file
    return open(filepath, mode='r')


def generate_path(file_path: str):

    # Converts whatever OS based filepath by dealing with / or \
    # Example Linux: a/b/c/d/e/f/g.html => ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    # Example Windows: C:\Windows\System32\system.ini ['Windows', 'System32', 'system.ini']
    path: list = os.path.normpath(file_path).split(os.sep)

    # Set the directories to be everything but the last item
    directories, file_path = path[0:-1], path[-1]

    # Create a path conforming to the underlying OS path string
    directories = os.path.join(*directories)

    # If those paths do not exist ...
    if not os.path.isdir(directories):

        # ... create them!
        # This handles internally the creation of folders within folders
        os.makedirs(directories)

    return directories, file_path


def partition(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]
