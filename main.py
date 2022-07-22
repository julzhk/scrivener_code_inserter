import os
import os
import xml.etree.ElementTree as ET
import pprint
from dataclasses import dataclass, field
from github import Github, ContentFile

import requests


def get_github_file(user='PyGithub', repo='PyGithub', filepath="README.md"):
    # g = GithubUrl(github_filepath='https://github.com/julzhk/policy_explorer/blob/master/persona/models.py#L8-L15')
    g = Github(os.environ.get('GITHUB_TOKEN'))
    repo = g.get_repo(f"{user}/{repo}")
    contents = repo.get_contents(filepath)
    return contents.decoded_content.decode()


def extract_lines_and_change_returns(content, from_line, to_line):
    code = content.split('\n')[from_line:to_line]
    code = '\\\n'.join(code)
    return code


@dataclass
class GithubUrl:
    github_filepath: str
    user: str = ''
    repo: str = ''
    filepath: str = ''
    from_line: str = ''
    to_line: str = ''

    def __post_init__(self):
        if '#' in self.github_filepath[:-1]:
            url, lines = self.github_filepath.split('#')
            self.get_lines_extracted(lines)
        else:
            url = self.github_filepath
        self.user, self.repo, *fp = url.replace('https://github.com/', '').split('/')
        self.filepath = '/'.join(fp[2:])

    def get_lines_extracted(self, lines):
        # given a fragment such as #L8-L15 get the from, to lines
        lines: str = lines.replace('L', '')
        lines: list = [int(l) for l in lines.split('-')]
        self.from_line, self.to_line = lines


@dataclass
class Style:
    style_code: str
    style_name: str


def add_styles(code):
    r = f'''
\\pard\\tx720\\tx1080\\tx1440\\tx1800\\tx2160\\li720\\pardirnatural\\partightenfactor0

\\f1\\fs24 \\cf0 <$Scr_Ps::0>
\\f2\\fs22 \\
{code} \
\\pard\\tx720\\tx1080\\tx1440\\tx1800\\tx2160\\li720\\pardirnatural\\partightenfactor0
\\f1\\fs24 \\cf0 <!$Scr_Ps::0>
\\f2\\fs22
'''
    return r


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

    @property
    def contents(self):
        with open(f'{self.path}/content.rtf') as f:
            return f.read()

    def write(self, data):
        with open(f'{self.path}/content.rtf', 'wt') as f:
            f.write(data)

    def replace_code_tag(self):
        g = GithubUrl(github_filepath='https://github.com/julzhk/policy_explorer/blob/master/persona/models.py#L8-L15')
        content = get_github_file(user=g.user, repo=g.repo, filepath=g.filepath)
        code = extract_lines_and_change_returns(content=content,
                                                from_line=g.from_line,
                                                to_line=g.to_line)
        code = add_styles(code)
        data = doc.contents
        data = data.replace('<github>', code, 1)
        doc.write(data)


@dataclass
class Project:
    fn: str
    documents: list[Document] = field(default_factory=list)
    styles: list[Style] = field(default_factory=list)

    def __post_init__(self):
        self.populate_styles()
        self.get_doc_folder_names()
        self.associate_doc_style_codes_with_global_style_list()

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

    def do_replace_code_placeholder(self):
        for doc in self.documents:
            if '<github>' in doc.contents:
                doc.replace_code_tag()


if __name__ == '__main__':
    p = Project(fn='testproject.scriv')
    p.do_replace_code_placeholder()
