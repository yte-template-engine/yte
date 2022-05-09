from yte.context import Context


class Subdocument:
    def __init__(self):
        self.inner = dict()

    def __getitem__(self, key):
        return self.inner[key]

    def _insert(self, key, value):
        self.inner[key] = value

    def items(self):
        return self.inner.items()

    def keys(self):
        return self.inner.keys()

    def __contains__(self, key):
        return key in self.inner

    def __eq__(self, other):
        if isinstance(other, Subdocument):
            return self.inner == other.inner
        elif isinstance(other, dict):
            return self.inner == other
        else:
            return False

    def __len__(self):
        return len(self.inner)

    def __repr__(self):
        return repr(self.inner)


class Document(Subdocument):
    def __init__(self):
        self.inner = Subdocument()

    def _insert(self, context: Context, value):
        if not context.rendered:
            # There is no key under which we could insert anything
            # This can happen with list-only or value-only
            # yaml documents, for which the doc object cannot be used
            # and will remain empty.
            return
        inner = self.inner
        for key in context.rendered[:-1]:
            if key not in inner:
                inner._insert(key, Subdocument())
            inner = inner[key]

        inner._insert(context.rendered[-1], value)
