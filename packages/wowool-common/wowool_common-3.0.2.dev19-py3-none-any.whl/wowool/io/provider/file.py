from pathlib import Path
from .input_provider import InputProvider
import errno
from logging import getLogger

global filemagic
filemagic = None

logger = getLogger("wowool.input_providers")


def _strip_upper_ascii(s):
    assert isinstance(s, bytes)
    return bytes([i for i in s if 31 < i < 127 or i == 0xD or i == 0xA]).decode("utf8")


class FileInputProvider(InputProvider):
    def __init__(self, fid, encoding="utf8", cleanup=None, **kwargs):
        InputProvider.__init__(self, str(fid))
        self.data = None
        self.encoding = encoding
        self.cleanup = cleanup

    def cache_it(self, s):
        if self.cache_fn and self.encoding != "utf8":
            with open(self.cache_fn, "w") as fh:
                fh.write(s)
        return s

    @property
    def text(self, **kwargs):
        fn = Path(self.id)
        self.cache_fn = Path(fn.parent, ".utf8_cache_" + fn.name)

        try:
            Path(self.cache_fn).exists()
        except OSError as exc:

            if exc.errno == errno.ENAMETOOLONG:
                self.cache_fn = None

        if self.cache_fn and self.cache_fn.exists():
            with open(self.cache_fn, "r", encoding="utf8") as f:
                logger.debug(f"Reading Cache file {self.id()}")
                return f.read()

        if "encoding" in kwargs:
            self.encoding = kwargs["encoding"]
        if self.encoding == "auto":
            global filemagic
            if filemagic is None:
                try:
                    import magic
                except:
                    raise RuntimeError("install the chardet library, 'on macos: brew install libmagic ; pip3 install filemagic'")
            import magic

            filemagic = magic.Magic(flags=magic.MAGIC_MIME_ENCODING)
            self.encoding = filemagic.id_filename(self.id())
            if self.encoding == "binary":
                # print(f"self.cleanup.................{self.cleanup}")
                if self.cleanup is None:
                    raise RuntimeError(f"Warning: Cannot process binary file: {self.id}")
        try:
            if self.encoding == "unknown-8bit":
                print(f"Warning: unkown encoding using ascii : {self.id}")
                with open(self.id(), "rb") as f:
                    r = f.read()
                    if self.cleanup:
                        return self.cache_it(self.cleanup(r))
                    else:
                        return self.cache_it(_strip_upper_ascii(r))
            with open(self.id, "r", encoding=self.encoding) as f:
                r = f.read()
                if self.cleanup:
                    return self.cache_it(self.cleanup(r))
                else:
                    return r
        except Exception as ex:
            if self.cleanup:
                with open(self.id, "rb") as f:
                    r = f.read()
                    return self.cache_it(self.cleanup(r))
            else:
                raise ex
