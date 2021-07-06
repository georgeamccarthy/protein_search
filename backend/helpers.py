
from jina import DocumentArray, Document

'''
Creates a DocumentArray from a chosen column of a csv file.
'''
def da_from_csv(csv_path: str, text_loc: int=0) -> DocumentArray:
    docs = []
    from csv import reader
    with open(csv_path, 'r') as datafile:
        for row in reader(datafile):
            docs.append(Document(text=row[text_loc]))

    return DocumentArray(docs)
