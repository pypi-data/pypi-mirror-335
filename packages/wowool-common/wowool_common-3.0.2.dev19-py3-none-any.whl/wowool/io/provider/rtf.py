from .input_provider import InputProvider
from striprtf.striprtf import rtf_to_text


class RTFFileInputProvider(InputProvider):
    def __init__(self, fid, encoding="utf8"):
        InputProvider.__init__(self, str(fid))
        self.encoding = encoding

    @property
    def text(self, **kwargs):
        with open(self.id(), "r") as f:
            data = f.read()
            return rtf_to_text(data, errors="ignore", encoding=self.encoding)
