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

    def pre_visit (self, n):
        pass

    def visit (self, n):
        pass

    def post_visit (self, n):
        pass

    def getOutput (self):
        return None
    def getReport (self):
        return None

    def addAcceptRule (self, rules):
        if type (list) != type (rules):
            rules = [rules]
        self.accept_rules.extend (rules)

    def addDenyRule (self, rules):
        if type (list) != type (rules):
            rules = [rules]
        self.deny_rules.extend (rules)

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
        self.walkNode (self.root, visitor)

        return visitor

    def walkNode (self, node, visitor):
        if visitor.appliesTo (node):
            visitor.pre_visit (node)
            visitor.visit (node)
            visitor.post_visit (node)

        l = node.children

        if l is None:
            return

        for c in l:
            self.walkNode (c, visitor)

class ProjectCheckEvaluator (TreeWalker):
    def __init__ (self, tree):
        TreeWalker.__init__ (self, tree)
        self.context = {}

    def walk (self, checker):
        self.context ['idx'] = 0
        result = TreeWalker.walk (self, checker)

        return result

    def walkNode (self, node, checker):
        self.context ['idx'] = self.context ['idx'] + 1

        checker.current_context = self.context
        TreeWalker.walkNode (self, node, checker)
        checker.current_context = None

