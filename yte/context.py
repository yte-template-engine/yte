class Context:
    def __init__(self, other=None):
        self.template = []
        self.rendered = []

        if other is not None:
            self.template = list(other.template)
            self.rendered = list(other.rendered)
