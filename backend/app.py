# %%
from jina.types.document.generators import from_csv
from jina import DocumentArray, Flow

from my_executors import ProtBertExecutor, MyIndexer
from backend_config import protein_path, embeddings_path
from utils import load_or_download

import os

# %%

def main():
    # TODO: load the following from config file
    url = "http://www.lri.fr/owncloud/index.php/s/fxIqHWvg1Zsq0JW/download"
    pdb_data_path = protein_path #"../data/pdb_data_seq.csv"

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