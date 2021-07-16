# %%
import streamlit as st
import streamlit.components.v1 as components

def protein_3d(pdb_id='1YCR', width=200, height=200):
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
    width=width
  )

st.title("Proteins Search")

query = st.text_input(
    label="Search proteins by aminoacids sequence e.g. `A E T C Z A O`"
)

# get data here
ids = ['1YCR', '1ZCR', '2YCR', '1BCR', '5YLT']

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
