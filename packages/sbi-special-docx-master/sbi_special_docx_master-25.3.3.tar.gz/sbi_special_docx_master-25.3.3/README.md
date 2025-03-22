## About

This project was created to add additional information, specified in a certain format, to existing .docx files. 

[![Documentation](https://img.shields.io/badge/Documentation-Read%20The%20Docs-blue.svg)](https://sbi-special-docx-master.readthedocs.io/en/latest/)

## Example

![Example Image](/docs/source/_static/example.jpg) 

```python
# Import the AddDocx class from the sbi_special_docx_master module
from sbi_special_docx_master import AddDocx

# Import the Document class from the python-docx library
from docx import Document

# Specify the path to the DOCX file you want to open
add_file = "Your_file.docx"

# Load the DOCX file into a Document object
doc = Document(add_file)

# Create a dictionary with the information that will be added to the document.
# This dictionary contains a list under the key 'separate_information_relations'.
# Each item in the list is a dictionary with 'content', 'images', and 'title'.
info_dict = {
    'separate_information_relations': [
        {
            'content': 'str',  # Some text content
            'images': [        # A list of images (each is a dictionary)
                {
                    'file': '<Base64>'  # Base64-encoded image string
                }
            ],
            'title': 'str'     # Title for this section
        },
        {
            'content': 'str',  # Another text content
            'images': [
                {
                    'file': int,  # This seems unusual; normally you'd expect a Base64 string here
                }
            ],
            'title': 'str'
        }
    ]
}

# Initialize the AddDocx object with the document and the provided info dictionary
spec = AddDocx(doc, info_dict)

# Save the modified document to a new file
spec.save('my_file.docx')
