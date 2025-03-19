from .input_provider import InputProvider
import docx


def get_headding_markup_level(paragraph):
    if paragraph.style.style_id and paragraph.style.style_id.startswith("Heading"):
        print(paragraph.style.style_id)
        return int(paragraph.style.style_id[7])
    return None


class DocxFileInputProvider(InputProvider):
    def __init__(self, fid):
        InputProvider.__init__(self, fid)

    @property
    def text(self, **kwargs):
        doc = docx.Document(self.id)
        text = ""
        for paragraph in doc.paragraphs:
            if markup_level := get_headding_markup_level(paragraph):
                text += f"{'#' * markup_level} {paragraph.text}\n\n"
            else:
                text += paragraph.text + "\n\n"

        return text
