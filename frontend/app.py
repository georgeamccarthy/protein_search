# %%
import requests
import streamlit as st
import streamlit.components.v1 as components


def get_data(query: str, endpoint: str) -> dict:
    headers = {
        "Content-Type": "application/json",
    }

    data = '{"mode":"search","data":["' + query + '"]}'

    response = requests.post(endpoint, headers=headers, data=data)
    content = response.json()

    matches = content["data"]["docs"][0]["matches"]

    return matches

def protein_3d(pdb_id="1YCR", width=200, height=200):
    components.html(
        f"""
      <script src="https://3Dmol.org/build/3Dmol-min.js" async></script>
      <div
        style='height: {height}px; width: {width}px; position: relative;'
        class='viewer_3Dmoljs'
        data-pdb='{pdb_id}'
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

endpoint = "http://localhost:12345/search"

st.title("Proteins Search")

query = st.text_input(
    label="Search proteins by aminoacids sequence e.g. `A E T C Z A O`"
)

if st.button(label="Search") or query:
    if query:
        matches = get_data(query, endpoint)
        ids = [doc["id"] for doc in matches]

        for id in ids:
            col1, col2 = st.beta_columns([1, 2])
            with col1:
                protein_3d(pdb_id=id)

            with col2:
                st.subheader("Properties")
                st.markdown(
                    f"""
                PDB ID: {id}\n
                [Explore properties](https://www.rcsb.org/structure/{id})
              """,
                )
    else:
        st.markdown("Please enter a query")
