from yte.context import Context
from dpath import get as dpath_get
from dpath import search as dpath_search


class Subdocument:
    def __init__(self):
        self.inner = dict()

    def __getitem__(self, key):
        try:
            return self.inner[key]
        except KeyError as e:
            try:
                return self.dpath_get(key)
            except KeyError:
                raise e

    def __setitem__(self, key, value):
        self.inner[key] = value

    def items(self):
        return self.inner.items()

    def keys(self):
        return self.inner.keys()

    def dpath_get(self, glob, separator="/"):
        return dpath_get(self.inner, glob, separator=separator)

    def dpath_search(self, glob, yielded=False):
        return dpath_search(self.inner, glob, yielded=yielded)

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
            if isinstance(inner, list):
                assert key <= len(inner), "bug: cannot insert at index > len(list)"
                if key == len(inner):
                    inner.append(Subdocument())
            else:
                if key not in inner:
                    inner[key] = Subdocument()
            inner = inner[key]

        if isinstance(inner, list):
            i = context.rendered[-1]
            assert isinstance(i, int) and i == len(inner)
            inner.append(value)
        else:
            inner[context.rendered[-1]] = value
