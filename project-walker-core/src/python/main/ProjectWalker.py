import os

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

class ProjectNode (Node):
    def __init__ (self, root_path):
        Node.__init__ (self, root_path)
        self.file_attrs = {}

class ProjectStructureTreeBuilder (TreeBuilder):
    def __init__ (self):
        TreeBuilder.__init__ (self)

    def build (self, root_path):
        node = ProjectNode (root_path)
        node.file_attrs = {
            'file_name': root_path,
            'path': None,
            'full_path': node.data,
            'type': self.ResolveFileType (node.data)
        }

        return TreeBuilder.build (self, node)

    def gather (self, node):
        if node.file_attrs ['type'] != 'd':
            return

        r = node.data
        paths = os.listdir (r)
        children = []

        for p in paths:
            n = ProjectNode (os.path.join (r, p))
            n.file_attrs = {
                'file_name': p,
                'path': r,
                'full_path': n.data,
                'type': self.ResolveFileType(n.data)
            }
            children.append (n)

        return children

    def ResolveFileType (self, full_path):
        t = None
        if os.path.isdir (full_path):
            t = 'd'
        elif os.path.isfile (full_path):
            t = 'f'
        return t


class Checker (Visitor):
    def __init__ (self, name):
        Visitor.__init__ (self)
        self.name = name
        self.check_result = []
        # read-only!
        self.current_context = None

    def addResult (self, result):
        self.check_result.append ((self.current_context, result))

    def getReport (self):
        """Gives the possibility to include report-generation facilities (just call this instead of getOutput, which generally is rather raw, so to say."""
        return "It was a pleasure evaluating such a nice project with %s failures for %s evaluated nodes" % (0, len (self.check_result))

    def getOutput (self):
        return self.check_result

