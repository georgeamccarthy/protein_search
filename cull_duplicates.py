import pandas as pd

fp = 'data/pdb_data_seq.csv'
df = pd.read_csv(fp)
df = df.drop_duplicates(subset=['structureId'])
df.to_csv(fp.split('.')[0] + '_culled.csv')
