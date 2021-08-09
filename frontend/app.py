import requests
import streamlit as st
import streamlit.components.v1 as components
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from typing import List, Dict


def search(query: str, endpoint: str) -> dict:
    content = requests.post(
        endpoint,
        headers={
            "Content-Type": "application/json",
        },
        data=f'{{"data":[{{"text": "{query}"}}]}}',
    ).json()

    matches = content["data"]["docs"][0]["matches"]

    return matches


def parse_polymer(polymer: Dict):
    try:

        source_organisms = polymer["rcsb_entity_source_organism"]
        parent_scientific_names = [
            o["ncbi_parent_scientific_name"] for o in source_organisms
        ]
        scientific_names = [o["ncbi_scientific_name"] for o in source_organisms]
        organisms = [
            name + " (" + parent + ")"
            for name, parent in zip(scientific_names, parent_scientific_names)
        ]
        # In principle the JSON response contains more then 1 organisms per source entity. I believe this is not possible in theory, or anyways it is probably not useful to take the thing into account. So we're gonna return only the first organism and we're happy.
        return organisms[0]
    except TypeError:
        # If the organism information is not there.
        return ""


def parse_rcsb_response(response: Dict):
    return [parse_rcsb_entry(e) for e in response["entries"]]

def parse_rcsb_entry(entry: Dict):
    citation = entry["rcsb_primary_citation"]
    polymers = entry["polymer_entities"]
    return {
        "description": entry["struct"]["title"],
        "release_date": entry["rcsb_accession_info"]["initial_release_date"][:10],
        "doi": citation["pdbx_database_id_DOI"],
        "publication": citation["title"],
        "authors": entry["rcsb_primary_citation"]["rcsb_authors"],
        "organisms": [parse_polymer(p) for p in polymers],
    }


def rcsb_metadata(ids: List[str], endpoint="https://data.rcsb.org/graphql"):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=endpoint)

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport) #, fetch_schema_from_transport=True)

    # Provide a GraphQL query
    query = gql(
        """
    query rcsb_metadata ($ids: [String!]!)
    { 
      entries(entry_ids: $ids) {
        struct {
          title
          pdbx_descriptor
        }
        rcsb_accession_info {
          initial_release_date
        }
        rcsb_primary_citation {
          pdbx_database_id_DOI
          title
          rcsb_authors
        }
        polymer_entities {
          rcsb_entity_source_organism {
            ncbi_parent_scientific_name
            ncbi_scientific_name
          }
        }
      }
    }
    """
    )

    # Execute the query on the transport
    result = client.execute(query, variable_values={"ids": ids})

    return result

def pdb_metadata(ids: List[str]):
    response = rcsb_metadata(ids)

    return parse_rcsb_response(response)

def protein_3d(pdb_id="1YCR", width=200, height=200):
    components.html(
        f"""
      <script src="https://3Dmol.org/build/3Dmol-min.js" async></script>
      <div
        style='height: {height}px; width: {width}px; position: relative;'
        class='viewer_3Dmoljs'
        data-pdb='{pdb_id}'
        data-spin='axis:y;speed:1'
        data-backgroundcolor='0xffffff'
        data-select1='chain:A'
        data-style1='cartoon:color=spectrum'
        data-surface1='opacity:.7;color:white'
        data-select2='chain:B'
        data-style2='stick'>
      </div>
    """,
        height=height,
        width=width,
    )


endpoint = "http://localhost:8020/search"

st.title("protein_search")

query = st.text_input(
    label="Search proteins by aminoacids sequence e.g. `A E T C Z A O / AETCZAO`"
)

if st.button(label="Search") or query:
    if query:
        matches = search(query, endpoint)

        ids = [doc["id"] for doc in matches]
        scores = [doc["scores"]["cosine"]["value"] for doc in matches]
        metadata = pdb_metadata(ids)

        for id, score, meta in zip(ids, scores, metadata):
            col1, col2 = st.beta_columns([1, 2])
            with col1:
                protein_3d(pdb_id=id)

            with col2:
                st.header(id)
                st.subheader(meta["description"])
                st.markdown(
                    f"""
                *Release date*: {meta["release_date"]}\n
                """)

                organisms = ", ".join(filter(None, meta["organisms"]))
                if organisms:
                    st.markdown(f"*Organisms:* {organisms}\n")

                st.markdown(f"""
                  Similarity metric: {score:.3f}\n
                  [Explore properties](https://www.rcsb.org/structure/{id})
                """,
                )
    else:
        st.markdown("Please enter a query")
