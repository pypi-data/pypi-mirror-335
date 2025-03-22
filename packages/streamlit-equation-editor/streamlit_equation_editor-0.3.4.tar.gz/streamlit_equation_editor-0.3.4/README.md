# Streamlit-Equation-Editor

A WYSIWYG math expression editor for Streamlit using Mathlive math field and on-screen keyboard.
This package is a modified version of [Streamlit-Mathlive-Editor](https://github.com/sinagolchi/Streamlit-Mathlive-Editor) by Sina Golchi.

## Installation instructions

```sh
pip install streamlit-equation-editor
```

## Usage instructions

```python
import streamlit as st
from st_equation_editor import mathfield

Tex, MathML = mathfield(value=r"\frac{1}{2} \times 5")

st.latex(Tex)
st.write(MathML)
```

## Features
- WYSIWYG math equation editor with virtual keyboard
- Direct "Copy Equation" button for LaTeX output
- Returns both LaTeX and MathML representations
