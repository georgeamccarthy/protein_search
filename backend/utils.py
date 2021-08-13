import os.path

from urllib.request import urlretrieve

def load_or_download(url, filename):
  if not os.path.isfile(filename):
    print(f"{filename} not found, downloading from {url}")
    r = urlretrieve(url, filename)
  
  return open(filename)

def partition(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]
