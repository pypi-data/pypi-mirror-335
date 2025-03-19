# Imports
# -------

import streamlit as st
import rdkit.Chem as Chem
import base64
import warnings
import json
import os
import shutil
import time

# brute force approach to avoid decompression bomb warning by pdf2image and PIL
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
warnings.filterwarnings("ignore")
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

from molecular_interaction_rules import MoleculerDatabase

smiles_help = """  \n  If you don't know SMILES, check this out:
                https://chemicbook.com/2021/02/13/smiles-strings-explained-for-beginners-part-1.html  \n  """

loading_err = KeyError("""The app encountered a problem in initializing the data.
Try to reload the page. If the problem persists, contact sharifsuliman1@gmail.com""")

problem_mail = '  \n  If the problem persists, contact contact sharifsuliman1@gmail.com'

def render_svg(svg):
  """Renders the given svg string."""
  b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
  html = r'<img width="300px" height="300px" src="data:image/svg+xml;base64,%s"/>' % b64
  st.write(html, unsafe_allow_html=True)

def upload_setting_button():
  """Allow to upload setting"""
  st.session_state['upload_setting'] = True
  return

def updatemol():
  """Allow to upload molecule"""
  st.session_state['update_mol'] = True
  return

def cite():
  """Print a licence to cite the package with link"""
  st.markdown('''
    Molecular Interaction Rules For General Molecules!
    [cite this work]XXX:
    [![DOI]()
    ''')

if __name__ == "__main__":
  # initialize session state
  if 'color_dict' not in st.session_state:
    st.session_state['color_dict'] = mig.color_map.copy()
  if 'resize_dict' not in st.session_state:
    st.session_state['resize_dict'] = mig.atom_resize.copy()
  if 'reset_color' not in st.session_state:
    st.session_state['reset_color'] = False
  if 'reset_size' not in st.session_state:
    st.session_state['reset_size'] = False
  if 'last_atom_size_but' not in st.session_state:
    st.session_state['last_atom_size_but'] = None
  if 'last_atom_color_but' not in st.session_state:
    st.session_state['last_atom_color_but'] = None
  if 'upload_setting' not in st.session_state:
    st.session_state['upload_setting'] = False
  if 'emoji_dict' not in st.session_state:
    st.session_state['emoji_dict'] = dict()
  if 'update_mol' not in st.session_state:
    st.session_state['update_mol'] = True
  if 'molecules_but' not in st.session_state:
    st.session_state['molecules_but'] = None
  if 'use_emoji' not in st.session_state:
    st.session_state['use_emoji'] = False

  # loading the color, resize and emoji dictionary
  if 'color_dict' in st.session_state:
    new_color = st.session_state['color_dict']
  else:
    st.exception(loading_err)
    print([i for i in st.session_state])
    st.session_state['color_dict'] = mig.color_map.copy()
    new_color = st.session_state['color_dict']
  if 'resize_dict' in st.session_state:
    resize = st.session_state['resize_dict']
  else:
    st.exception(loading_err)
    print([i for i in st.session_state])
    st.session_state['resize_dict'] = mig.atom_resize.copy()
    resize = st.session_state['resize_dict']
  if 'emoji_dict' in st.session_state:
    emoji = st.session_state['emoji_dict']
  else:
    st.exception(loading_err)
    print([i for i in st.session_state])
    st.session_state['emoji_dict'] = dict()
    emoji = st.session_state['emoji_dict']

  # check if the color/resize dictionary have been reset
  if 'atom_color_select' in st.session_state and 'color_picker_but' in st.session_state and st.session_state[
    'reset_color']:
    st.session_state.color_picker_but = new_color[st.session_state.atom_color_select]
    st.session_state['last_atom_color_but'] = None
    st.session_state['reset_color'] = False
  last_atom_color = st.session_state['last_atom_color_but']
  if 'atom_size_select' in st.session_state and 'sizes_percentage_but' in st.session_state and st.session_state[
    'reset_size']:
    st.session_state['last_atom_size_but'] = None
    st.session_state['reset_size'] = False
  last_atom_size = st.session_state['last_atom_size_but']

  # setting header, description and citation
  st.set_page_config(page_title="Molecule icons")
  st.header('''
    Molecule Interaction Rules Generator!
    ''')
  st.write('''
    Retrieve Coordinates For Monomers or Dimers for a General Set of Molecules in Z-Matrix Form
    ''')
  st.markdown('''
For more options and information, check out the
[GitHub repository](https://github.com/mackerell-lab/Molecular-Interaction-Rules).\\
[DOI](https://doi.org/10.5281/zenodo.7388429): 10.5281/ZENODO.7388429.
       ''')

  # select the input type
  input_type = st.selectbox("Create your icon by",
                            ['name', 'smiles', 'load file', 'cas_number', 'stdinchi', 'stdinchikey', 'smiles list'],
                            on_change=updatemol,
                            help="""Choose the input info of your molecule. If the app is slow, use SMILES input.""" + smiles_help)

  st.markdown(html_string, unsafe_allow_html=True)
  st.write('For help or feedback, contact sharifsuliman1@gmail.com')
