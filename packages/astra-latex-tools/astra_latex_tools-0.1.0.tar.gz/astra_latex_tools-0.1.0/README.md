# Deep_Python
Углубленный Python, весна 2025, ИТМО



# HW2 🔮

A Python library for generating LaTeX documents with tables and images.

## Installation

```bash
pip install astra_latex_tools
```

## Usage

```python
from latex_generator import list_to_LaTex_table, add_image_to_latex

data = [
    ["Name", "Age", "City"],
    ["Alice", 24, "New York"],
    ["Bob", 30, "Los Angeles"],
    ["Charlie", 22, "Chicago"]
]
# Add Table
list_to_LaTex_table(data)

# Add image
add_image_to_latex("image.png")
```
