class Visitor:
    def __init__ (self):
        self.accept_rules = []
        self.deny_rules = []

    def appliesTo (self, n):
        for predicate in self.accept_rules:
            if not predicate (n):
                return False
        for predicate in self.deny_rules:
            if predicate (n):
                return False
        return True

    def visit (self, n):
        pass

    def getOutput (self):
        return None

class Node:
    def __init__ (self, data):
        self.children = []
        self.data = data

class Tree:
    def __init__ (self):
        self.root = None

class TreeBuilder:
    def __init__ (self):
        self.tree = Tree ()

    def build (self, root):
        self.tree.root = root
        self.tree.root.children = self.__build (self.tree.root)
        return self.tree

    def gather (self, node):
        """Must return Node() instances in a list"""
        return []

    def __build (self, node):
        children = self.gather (node)

        if children is None:
            return

        for c in children:
            c.children = self.__build (c)
            node.children.append (c)

        return node.children

class TreeWalker:
    def __init__ (self, tree):
        self.root = tree.root

    def walk (self, visitor):
        self.__walkNode (self.root, visitor)

        return visitor.getOutput ()

    def __walkNode (self, node, visitor):
        if visitor.appliesTo (node):
            visitor.visit (node)

        l = node.children

        if l is None:
            return

        for c in l:
            self.__walkNode (c, visitor)
