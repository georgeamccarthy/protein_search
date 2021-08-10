from backend_config import print_logs
import pandas as pd
import numpy as np


def cull_duplicates(fp):
    df = pd.read_csv(fp)
    df = df.drop_duplicates(subset=["structureId"])
    df[["structureId", "sequence"]].to_csv(fp, index=False)


def download_csv(url, fp):
    import requests

    response = requests.get(url)
    with open(fp, "wb") as f:
        f.write(response.content)


def shuffle_csv(fp):
    df = pd.read_csv(fp)
    np.random.shuffle(df.values)
    df.to_csv(fp, index=False)


def log(message):
    if print_logs:
        print(message)
