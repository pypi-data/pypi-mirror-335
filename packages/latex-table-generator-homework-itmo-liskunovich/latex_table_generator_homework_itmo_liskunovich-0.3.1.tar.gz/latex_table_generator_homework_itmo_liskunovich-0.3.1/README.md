# LaTeX Helper

A lightweight Python package for creating LaTeX code snippets for tables and pictures.

## Setup

```shell
pip install latex_table_gen

from latex_table_gen.latex_tools import build_table, insert_picture 

# Create LaTeX code for a table
dataset = [
    # Your data goes here
]
latex_table = build_table(dataset)

# Generate LaTeX code for a picture
picture = insert_picture('path/to/picture.jpg', description='Sample pic', marker='fig:sample')
