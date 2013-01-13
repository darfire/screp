


class XMLContext(object):
    def __init__(self, current, root):
        self.current = current
        self.root = root

        self._anchors = {'$': current, '@': root}


    def get_anchor(self, name):
        return self._anchors[name]


    def add_anchor(self, name, value):
        self._anchors[name] = value
