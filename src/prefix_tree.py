import attr


@attr.s
class PrefixTree:
    root = attr.ib()

    @staticmethod
    def initialize():
        root = PrefixTreeNode(value=None)
        return PrefixTree(root=root)

    def insert(self, value, key, current=None):
        if current is None:
            current = self.root

        if not value:
            current.mappings.append(key)
            return
        top = value[0]
        rest = value[1:]

        next_child = current.children.get(top)

        if next_child:
            self.insert(rest, key, next_child)
        else:
            new_node = PrefixTreeNode(value=top)
            current.children[top] = new_node
            self.insert(rest, key, new_node)

    def get(self, value, current=None):
        if not current:
            current = self.root
        if not value:
            return current.mappings

        top = value[0]
        rest = value[1:]

        next_child = current.children.get(top)

        if next_child:
            return self.get(rest, next_child)


@attr.s
class PrefixTreeNode:
    value = attr.ib()
    mappings = attr.ib(default=attr.Factory(list))
    children = attr.ib(default=attr.Factory(dict))
