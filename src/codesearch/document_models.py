import attr


@attr.s
class Corpus:
    _documents = attr.ib(default=attr.Factory(dict))
    _key_to_uid = attr.ib(default=attr.Factory(dict))

    @property
    def document_count(self):
        return len(self._documents)

    def add_document(self, key, content):
        document_uid = f"document:{self.document_count}"

        self._documents[document_uid] = Document(
            uid=document_uid, key=key, content=content
        )
        self._key_to_uid[key] = document_uid

        return document_uid

    def get_document(self, uid=None, key=None):
        if key:
            uid = self._key_to_uid[key]

        return self._documents[uid]

    def collect_unprocessed_documents(self):
        return [
            uid
            for uid in self._documents
            if not self.get_document(uid=uid).is_processed
        ]

    def mark_document_as_processed(self, uid):
        self._documents[uid].mark_as_processed()


@attr.s
class Document:
    uid = attr.ib()
    key = attr.ib()
    content = attr.ib()
    _processed = attr.ib(default=False)

    @property
    def is_processed(self):
        return self._processed

    def mark_as_processed(self):
        self._processed = True
