from backend_config import print_logs

def cull_duplicates(fp):
    import pandas as pd

    df = pd.read_csv(fp)
    df = df.drop_duplicates(subset=['structureId'])
    df[['structureId', 'sequence']].to_csv(fp, index=False)

def download_csv(url, fp):
    import requests
    response = requests.get(url)
    with open(fp, "wb") as f:
        f.write(response.content)

def log(message):
    if print_logs:
        print(message)
