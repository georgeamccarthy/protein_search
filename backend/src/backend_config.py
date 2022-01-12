# Hugging Face: https://huggingface.co/Rostlab/prot_bert
backend_model = "Rostlab/prot_bert"

# maximum docs to index (lower = faster)
max_docs = 100

# dataset link
pdb_data_url = "https://www.lri.fr/owncloud/index.php/s/eq7aCSJP3Ci0Vyq/download"

# Number of search results to show.
top_k = 10

# Protein file path relative to root.
pdb_data_path = "data/pdb_data_seq.csv"

# Embeddings file path.
embeddings_path = "embeddings/proteins.json"

# Prints logs to command line if true.
print_logs = True
