# %%
import streamlit as st
import streamlit.components.v1 as components

components.html(
    """
    <script src="https://3Dmol.org/build/3Dmol-min.js" async></script> 
    <div
      style="height: 400px; width: 400px;
      position: relative;"
      class='viewer_3Dmoljs'
      data-pdb='1YCR'
      data-backgroundcolor='0xffffff' 
      data-select1='chain:A'
      data-style1='cartoon:color=spectrum'
      data-surface1='opacity:.7;color:white'
      data-select2='chain:B'
      data-style2='stick'>
    </div>
  """
)
