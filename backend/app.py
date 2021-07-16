# %%
from jina.types.document.generators import from_csv
from jina import DocumentArray, Flow

from my_executors import ProtBertExecutor, MyIndexer
from backend_config import protein_path, embeddings_path, dataset_url
from utils import load_or_download

import os

# %%

def main():
    url = dataset_url
    pdb_data_path = protein_path

    with load_or_download(url, pdb_data_path) as data_file:
        docs_generator = from_csv(
            fp=data_file,
            field_resolver={
                "sequence": "text",
                "structureId": "id"
            }
        )
        proteins = DocumentArray(docs_generator)[0:42]

    flow = (
        Flow(port_expose=12345, protocol='http')
        .add(uses=ProtBertExecutor)
        .add(uses=MyIndexer)
    )

    with flow:
        if not os.path.exists(embeddings_path):
            flow.index(proteins)
        flow.block()


if __name__ == "__main__":
    main()