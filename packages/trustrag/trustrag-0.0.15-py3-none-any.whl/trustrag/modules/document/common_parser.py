import re

import loguru

from trustrag.modules.document.chunk import TextChunker
from trustrag.modules.document.docx_parser import DocxParser
from trustrag.modules.document.excel_parser import ExcelParser
from trustrag.modules.document.html_parser import HtmlParser
from trustrag.modules.document.pdf_parser_fast import PdfSimParser
from trustrag.modules.document.ppt_parser import PptParser
from trustrag.modules.document.txt_parser import TextParser
from trustrag.modules.document.markdown_parser import MarkdownParser

class CommonParser():
    def __init__(self):
        self.tc = TextChunker()

    def parse(self, file_path):
        # 读取文件内容
        filename = file_path
        with open(file_path, 'rb') as f:
            content = f.read()
        # bytes_io = BytesIO(content)
        # 检测文件类型
        # mime = magic.Magic(mime=True)
        # file_type = mime.from_buffer(content)
        # loguru.logger.info(filename, file_type, mime)
        loguru.logger.info(filename)
        if re.search(r"\.docx$", filename, re.IGNORECASE):
            parser = DocxParser()
        elif re.search(r"\.pdf$", filename, re.IGNORECASE):
            parser = PdfSimParser()
        elif re.search(r"\.xlsx?$", filename, re.IGNORECASE):
            parser = ExcelParser()
        elif re.search(r"\.pptx$", filename, re.IGNORECASE):
            parser = PptParser()
        elif re.search(r"\.(txt|py|js|java|c|cpp|h|php|go|ts|sh|cs|kt)$", filename, re.IGNORECASE):
            parser = TextParser()
        elif re.search(r"\.(htm|html)$", filename, re.IGNORECASE):
            parser = HtmlParser()
        elif re.search(r"\.doc$", filename, re.IGNORECASE):
            parser = DocxParser()
        elif re.search(r"\.md$", filename, re.IGNORECASE):
            parser = MarkdownParser()
        else:
            raise NotImplementedError(
                "file type not supported yet(pdf, xlsx, doc, docx, txt supported)")
        contents = parser.parse(content)
        # loguru.logger.info(contents)
        # contents = self.tc.chunk_sentences(contents, chunk_size=512)
        return contents
