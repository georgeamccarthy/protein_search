import jina
flow = jina.Flow(port_expose=45678, protocol='http').add(uses="jinahub://encoder").add(uses="jinahub://indexer")
with flow:
    flow.post(on="/index", inputs=jina.types.document.generators.from_csv('data/input.csv'))
    flow.block()
