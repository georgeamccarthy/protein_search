# %%
import os.path

import requests

def load_or_download(url, filename):

  # If the filename given does not exist
  if not os.path.isfile(filename):

    # Print logging messag
    print(f"{filename} not found, downloading from {url}")
   
    # `urlretrieve` prior assumes directory exists, but
    # since `data` can be ignored, we need to make sure the
    # directories that came with `filename` do exist
    res = requests.get(url)

    # Converts whatever OS based filepath by dealing with / or \ 
    # Example Linux: a/b/c/d/e/f/g.html => ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    # Example Windows: C:\Windows\System32\system.ini ['Windows', 'System32', 'system.ini']
    path: list = os.path.normpath(filename).split(os.sep)

    # Set the directories to be everything but the last item
    directories, file_path = path[0:-1], path[-1]

    # Create a path conforming to the underlying OS path string
    directories = os.path.join(*directories)

    # If those paths do not exist ... 
    if not os.path.isdir(directories):

      # ... create them!
      # This handles internally the creation of folders within folders
      os.makedirs(directories)

    # Create the file with the given path in binary
    # Binary formats make sure no difficulty comes with encoding formats
    # which can or sometimes changes in the future
    with open(f'{directories}/{file_path}', mode='wb') as file_handler:
        
        # Write the content to the file, then close
        file_handler.write(res.content)

  # Return the handle to the file
  return open(filename)

def partition(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]