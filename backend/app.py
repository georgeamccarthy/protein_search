from jina.types.document.generators import from_csv
from jina import DocumentArray

proteins = DocumentArray(
    from_csv(open("../data/Train_HHblits_1column.csv"), {"Protein sequences": "text"})
)
