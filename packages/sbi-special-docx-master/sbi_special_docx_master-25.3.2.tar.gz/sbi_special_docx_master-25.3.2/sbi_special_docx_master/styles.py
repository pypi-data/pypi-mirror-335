"""
MS Word document template module.
"""

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class DocEditorEmpty:
    """
    Class that contains an instance of a Word document template (python-docx)
    with predefined formatting styles.

    Defined styles:

    - `central_header` - Centered headers
    - `text_base` - Standard paragraph text
    - `text_red` - Red-colored text
    - `List Bullet` - Unordered bullet list
    - `List Bullet 2` - Second-level bullet list
    - `Table Grid` - Table cell style
    - `left_header` - Left-aligned uppercase headers
    - `first_base` - Paragraph without first-line indent
    - `List` - General-purpose list style
    - 'left_header' - Left-aligned headers

    :ivar document: Template document instance ready for content generation
    :vartype document: docx.Document

    :ivar sections: Document sections with A4 page layout settings

    :ivar styles: Defined styles available for document generation
    """

    def __init__(self):
        # Initialize a new Word document
        self.document = Document()
        """Template document instance"""

        # Retrieve the document sections and apply A4 page settings
        self.sections = self.document.sections
        """Document sections with A4 page setup"""

        for section in self.sections:
            section.page_height = Cm(29.7)
            section.page_width = Cm(21.0)
            section.top_margin = Cm(2)
            section.left_margin = Cm(3)
            section.right_margin = Cm(1)
            section.bottom_margin = Cm(2)

        # Access the document's style collection
        self.styles = self.document.styles
        """Available styles for the document"""

        # Style: Centered header with bold, red text and underline
        header_c = self.styles.add_style('central_header', WD_STYLE_TYPE.PARAGRAPH)
        header_c.font.name = 'Times New Roman'
        header_c.font.size = Pt(14)
        header_c.font.bold = True
        header_c.paragraph_format.space_before = Pt(0)
        header_c.paragraph_format.space_after = Pt(0)
        header_c.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        header_c.font.color.rgb = RGBColor(192, 0, 0)
        header_c.font.underline = True

        # Style: Standard body text, justified alignment, with indent
        text_base = self.styles.add_style('text_base', WD_STYLE_TYPE.PARAGRAPH)
        text_base.font.name = 'Times New Roman'
        text_base.font.size = Pt(14)
        text_base.paragraph_format.space_before = Pt(0)
        text_base.paragraph_format.space_after = Pt(0)
        text_base.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        text_base.paragraph_format.first_line_indent = Cm(1.25)
        text_base.paragraph_format.line_spacing = 1

        # Modify default unordered list style (List Bullet)
        list_style = self.styles['List Bullet']
        list_style.font.name = 'Times New Roman'
        list_style.font.size = Pt(14)
        list_style.paragraph_format.space_before = Pt(0)
        list_style.paragraph_format.space_after = Pt(0)
        list_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        list_style.paragraph_format.first_line_indent = Cm(1.25)
        list_style.paragraph_format.left_indent = Cm(0)
        list_style.paragraph_format.line_spacing = 1
        list_style.paragraph_format.tab_stops.clear_all()

        # Style: Dark red paragraph text
        text_red = self.styles.add_style('text_red', WD_STYLE_TYPE.PARAGRAPH)
        text_red.font.name = 'Times New Roman'
        text_red.font.size = Pt(14)
        text_red.font.color.rgb = RGBColor(255, 0, 0)

        # Modify second-level bullet list style (List Bullet 2)
        list_style = self.styles['List Bullet 2']
        list_style.font.name = 'Times New Roman'
        list_style.font.size = Pt(14)
        list_style.paragraph_format.space_before = Pt(1.25)
        list_style.paragraph_format.space_after = Pt(0)
        list_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        list_style.paragraph_format.first_line_indent = Cm(0)
        list_style.paragraph_format.left_indent = Cm(0.0)
        list_style.paragraph_format.line_spacing = 1

        # Modify table grid style for smaller font size
        tab_style = self.styles['Table Grid']
        tab_style.font.name = 'Times New Roman'
        tab_style.font.size = Pt(9)

        # Style: Left-aligned header, bold, underlined, uppercase
        left_header = self.styles.add_style('left_header', WD_STYLE_TYPE.PARAGRAPH)
        left_header.font.name = 'Times New Roman'
        left_header.font.size = Pt(14)
        left_header.font.bold = True
        left_header.font.underline = True
        left_header.paragraph_format.space_before = Pt(1.25)
        left_header.paragraph_format.space_after = Pt(0)
        left_header.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        left_header.paragraph_format.left_indent = Cm(1.25)
        left_header.font.all_caps = True

        # Style: Paragraph without first-line indent (often used for initial sections)
        first_base = self.styles.add_style('first_base', WD_STYLE_TYPE.PARAGRAPH)
        first_base.font.name = 'Times New Roman'
        first_base.font.size = Pt(14)
        first_base.paragraph_format.space_before = Pt(1.25)
        first_base.paragraph_format.space_after = Pt(0)
        first_base.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        first_base.paragraph_format.first_line_indent = Cm(0)
        first_base.paragraph_format.line_spacing = 1

        # Modify generic list style
        list_style = self.styles['List']
        list_style.font.name = 'Times New Roman'
        list_style.font.size = Pt(14)
        list_style.paragraph_format.space_before = Pt(0)
        list_style.paragraph_format.space_after = Pt(0)
        list_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        list_style.paragraph_format.first_line_indent = Cm(0.2)

    def create_document(self):
        """
        Returns the document instance for further processing or saving.

        :return: Document instance
        :rtype: docx.Document
        """
        return self.document
