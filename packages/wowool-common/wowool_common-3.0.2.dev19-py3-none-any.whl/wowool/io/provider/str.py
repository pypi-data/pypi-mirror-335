from .input_provider import InputProvider
from typing import Optional


class StrInputProvider(InputProvider):
    # leave the kwargs in as we do not know which args are sent the they are created by the Factory
    def __init__(self, text: str, id: Optional[str] = None, **kwargs):
        uid = id
        if uid is None:
            uid = "stream_id_" + str(abs(hash(text)))

        InputProvider.__init__(self, uid)
        self._text = text

    @property
    def text(self) -> str:
        return self._text
