import os
import os
import xml.etree.ElementTree as ET
import pprint
from dataclasses import dataclass, field


@dataclass
class Style:
    style_code: str
    style_name: str


@dataclass
class Document:
    """Class for keeping track of a Scrivener Document folder."""
    folder_label: str = ''
    path: str = ''
    style_codes: list[str] = field(default_factory=list)
    styles: list[Style] = field(default_factory=list)

    def __post_init__(self):
        try:
            with open(f'{self.path}/content.styles') as f:
                self.style_codes = f.read().split(',')
        except FileNotFoundError:
            # no styles in the doc
            pass


@dataclass
class Project:
    fn:str
    documents: list[Document] = field(default_factory=list)
    styles: list[Style] = field(default_factory=list)

    def populate_styles(self):
        styles_path = f'{self.fn}/Files/styles.xml'
        tree = ET.parse(styles_path)
        root = tree.getroot()
        names_codes = [(style.attrib['Name'], style.attrib['ID']) for style in root.iter('Style')]
        for name, code in names_codes:
            self.styles.append(Style(style_name=name, style_code=code))

    def get_style_by_style_code(self, style_id):
        for style in self.styles:
            if style.style_code == style_id:
                return style
        return None

    def get_doc_folder_names(self):
        doc_folder = f'{self.fn}/Files/Data'
        with os.scandir(doc_folder) as it:
            for entry in it:
                if entry.is_dir():
                    self.documents.append(Document(folder_label=entry.name,
                                                   path=f'{doc_folder}/{entry.name}')
                                          )

    def associate_doc_style_codes_with_global_style_list(self):
        for doc in self.documents:
            for style_code in doc.style_codes:
                this_style = self.get_style_by_style_code(style_id=style_code)
                doc.styles.append(this_style)


if __name__ == '__main__':
    p = Project(fn='testproject.scriv')
    p.populate_styles()
    p.get_doc_folder_names()
    p.associate_doc_style_codes_with_global_style_list()
    pprint.pprint(p)
