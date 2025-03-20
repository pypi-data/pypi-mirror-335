from pathlib import Path
from typing import Union, Optional
from wowool.document.document import Document
from os import pathconf
from wowool.utility.path import expand_path

PC_NAME_MAX = pathconf("/", "PC_NAME_MAX")


def _resolve__pass_thru(id):
    return id


def data2str(data: Union[str, bytes, None], encoding="utf-8") -> str:
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode(encoding)
    elif data == None:
        return ""
    else:
        raise RuntimeError(f"data only supports str|bytes, not {type(data)} {data}")


def _make_str(uid, data, encoding, **kwargs) -> Document:
    from wowool.io.provider.str import StrInputProvider

    _txt: str = data2str(data, encoding)
    _uid = str(uid) if isinstance(uid, Path) else uid
    return Document(StrInputProvider(_txt, id=_uid))


def _make_file(uid, data, encoding, **kwargs) -> Document:
    from wowool.io.provider.file import FileInputProvider

    return Document(FileInputProvider(fid=uid, encoding=encoding, **kwargs))


def _make_html(uid, data, encoding) -> Document:
    try:
        from wowool.io.provider.html_v2 import HTMLFileInputProvider

        return Document(HTMLFileInputProvider(uid, data))
    except Exception as ex:
        raise RuntimeError(f"install the BeautifulSoup(beautifulsoup4) library, 'pip install beautifulsoup4' {ex}")


def _make_docx(uid, data, **kwargs) -> Document:
    assert data is None, "The docx reader does not support data, only files"
    try:
        from wowool.io.provider.docx import DocxFileInputProvider

        return Document(DocxFileInputProvider(uid))
    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the python-docx library, 'pip install python-docx' {ex}")


def _make_pdf(uid, data, **kwargs) -> Document:
    assert data == None, "The pdf reader does not support data, only files"
    try:
        from wowool.io.pdf.provider import PDFFileInputProvider

        return Document(PDFFileInputProvider(uid))

    except ModuleNotFoundError as ex:
        raise ModuleNotFoundError(f"install the pdfminer.six library, 'pip install pdfminer.six' {ex}")


def _invalid_type(uid, data, **kwargs):
    raise RuntimeError("Invalid type")


creators = {
    "txt": _make_str,
    "utf8": _make_str,
    "text": _make_str,
    "file": _make_file,
    "html": _make_html,
    "pdf": _make_pdf,
    "docx": _make_docx,
    "_invalid_type": _invalid_type,
}

binary_content_types = set(["pdf", "docx"])


def read_content(fn: Path, input_provider, encoding) -> str:
    with open(fn, "rb") as fh:
        bdata = fh.read()
        if input_provider in binary_content_types:
            return bdata
        return bdata.decode(encoding)


class Factory:
    @staticmethod
    def create(
        id: Union[Path, str],
        data: Optional[Union[str, bytes]] = None,
        provider_type: str = "",
        encoding="utf8",
        **kwargs,
    ) -> Document:
        """
        Class to create a document from input data or from file.

        .. code-block :: python

            fn = "test.html"
            doc = Factory.create(fn)

        .. code-block :: python

            fn = "test.html"
            with open(fn) as fh:
                html_data = fh.read()
                doc = Factory.create(id = fn, data = html_data, provider_type = "html")

        """
        _data = data
        if id != None and _data is None:
            fn = Path(id)
            try:
                if fn.exists():
                    provider_type = fn.suffix.lower()
                    provider_type = provider_type[1:]
                    if provider_type == "txt":
                        provider_type = "file"
                else:
                    provider_type = "txt"
                    _data = id
                    id = None
            except Exception as ex:
                provider_type = "txt"
                _data = id
                id = None
        else:
            if data != None:
                fn = Path(id)
                if not provider_type:
                    if fn.exists():
                        provider_type = fn.suffix[1:] if fn.suffix.startswith(".") else "txt"
                    else:
                        provider_type = "txt"

        return creators.get(provider_type, _invalid_type)(id, _data, encoding=encoding)

    @staticmethod
    def split_path_on_wildcards(path_description: Path, pattern: str = "**/*.txt"):
        """
        Split a path description into a folder and a wildcard pattern.
        """
        parts = path_description.parts

        for index, part in enumerate(parts):
            if "*" in part or "?" in part:
                return Path(*parts[:index]), str(Path(*parts[index:]))

        return path_description, pattern

    @staticmethod
    def glob(folder: Path | str, pattern: str = "**/*.txt", provider_type: str = "", resolve=_resolve__pass_thru, **kwargs):
        folder = expand_path(folder)
        if folder.is_file():
            try:
                yield Factory.create(id=resolve(folder), provider_type=provider_type)
                return
            except Exception as ex:
                print(f"Could not create document object, {ex}: {folder}")
        folder, pattern_ = Factory.split_path_on_wildcards(folder, pattern=pattern)
        for fn in folder.glob(pattern_):
            try:
                if fn.is_file():
                    yield Factory.create(id=resolve(fn), provider_type=provider_type, **kwargs)
            except Exception as ex:
                print(f"Could not create document object, {ex}: {fn}")
