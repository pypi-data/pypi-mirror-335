class InputProvider:
    """
    :class:`InputProvider` is an interface utility to handle data input.
    """

    def __init__(self, doc_id: str):
        """
        Initialize an :class:`InputProvider` instance

        :param doc_id: Unique document identifier
        :type doc_id: ``str``

        :rtype: :class:`InputProvider`
        """
        super(InputProvider, self).__init__()
        self.doc_id = doc_id

    @property
    def id(self) -> str:
        """
        :return: Unique document identifier
        :rtype: ``str``
        """
        return self.doc_id

    @property
    def text(self) -> str:
        """
        :return: Text content of the document
        :rtype: ``str``
        """
        raise NotImplementedError()

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.text
