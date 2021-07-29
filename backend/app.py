from jina.types.document.generators import from_csv
from jina import DocumentArray, Flow

from my_executors import ProtBertExecutor, MyIndexer
from backend_config import pdb_data_path, embeddings_path, pdb_data_url
from helpers import cull_duplicates, download_csv, log

import os


def main():
    if not os.path.exists(pdb_data_path):
        log('Downloading data.')
        download_csv(pdb_data_url, pdb_data_path)
        log('Culling PDB ID duplicates.')
        cull_duplicates(pdb_data_path)

    log('Converting protein data to DocumentArray')
    with open(pdb_data_path) as data_file:
        docs_generator = from_csv(
            fp=data_file,
            field_resolver={
                "sequence": "text",
                "structureId": "id"
            }
        )
        proteins = DocumentArray(docs_generator)[:50]

    log('Creating flow.')
    flow = (
        Flow(port_expose=12345, protocol='http')
        .add(uses=ProtBertExecutor)
        .add(uses=MyIndexer)
    )


    log('Opening flow.')
    with flow:
        log('Indexing.')
        flow.index(proteins)
        log('Ready.')
        flow.block()


if __name__ == "__main__":
    main()

