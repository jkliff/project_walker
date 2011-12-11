#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import logging

from interpol import interpol

_t = lambda m: logging.debug(m)
_d = lambda m: logging.debug(m)
_i = lambda m: logging.info(m)
_w = lambda m: logging.warn(m)
_e = lambda m: logging.error(m)


def report_debug(f):

    def w(*args, **kws):
        _d('Entering %s' % f)
        r = f(*args, **kws)
        _d('Exiting %s' % f)
        return r

    return w


def report_info(f):

    def w(*args, **kws):
        _i('Entering %s' % f)
        r = f(*args, **kws)
        _i('Exiting %s:' % f)
        return r

    return w


class Visitor:

    def __init__(self):
        self.accept_rules = []
        self.deny_rules = []

    @report_debug
    def appliesTo(self, n):
        for predicate in self.accept_rules:
            if not predicate(n):
                return False

        for predicate in self.deny_rules:
            if predicate(n):
                return False
        return True

    @report_debug
    def pre_walk(self):
        pass

    @report_debug
    def visit(self, n):
        pass

    @report_debug
    def post_visit(self, n):
        pass

    @report_debug
    def post_walk(self):
        pass

    def addAcceptRule(self, rules):
        if type(list) != type(rules):
            rules = [rules]
        self.accept_rules.extend(rules)

    def addDenyRule(self, rules):
        if type(list) != type(rules):
            rules = [rules]
        self.deny_rules.extend(rules)


class Node:

    def __init__(self, data):
        self.children = []
        self.data = data


class Tree:

    def __init__(self):
        self.root = None


class TreeBuilder:

    def __init__(self):
        self.tree = Tree()

    def build(self, root):
        self.tree.root = root
        self.tree.root.children = self.__build(self.tree.root)
        return self.tree

    def gather(self, node):
        """Must return Node() instances in a list"""

        return []

    def __build(self, node):
        children = self.gather(node)

        if children is None:
            return

        for c in children:
            c.children = self.__build(c)
            node.children.append(c)

        return node.children


class TreeWalker:

    def __init__(self, tree):
        self.root = tree.root

    def walk(self, visitors):
        for visitor in visitors:
            visitor.pre_walk()
            self.walkNode(self.root, visitor)
            visitor.post_walk()

        return visitors

    @report_debug
    def walkNode(self, node, visitor):
        if visitor.appliesTo(node):
            visitor.visit(node)

        l = node.children
        if l is None:
            return

        for c in l:
            self.walkNode(c, visitor)

        visitor.post_visit(node)


class ProjectCheckEvaluator(TreeWalker):

    def __init__(self, tree):
        TreeWalker.__init__(self, tree)
        self.context = {}

    @report_debug
    def walk(self, checkers):
        self.context['idx'] = 0

        return [c.getStatus() for c in TreeWalker.walk(self, checkers)]

    @report_debug
    def walkNode(self, node, checker):
        self.context['idx'] = self.context['idx'] + 1

        checker.current_context = self.context
        TreeWalker.walkNode(self, node, checker)
        checker.current_context = None


class ProjectNode(Node):

    def __init__(self, root_path):
        Node.__init__(self, root_path)
        self.file_attrs = {}


class ProjectStructureTreeBuilder(TreeBuilder):

    def __init__(self):
        TreeBuilder.__init__(self)

    def build(self, root_path):
        node = ProjectNode(root_path)
        node.file_attrs = {
            'file_name': root_path,
            'name': os.path.basename(os.path.splitext(root_path)[0]),
            'extension': (os.path.splitext(root_path)[-1])[1:],
            'path': None,
            'full_path': node.data,
            'type': ProjectStructureTreeBuilder.ResolveFileType(node.data),
            }

        return TreeBuilder.build(self, node)

    def gather(self, node):
        if node.file_attrs['type'] != 'd':
            return

        r = node.data
        paths = os.listdir(r)
        children = []

        for p in paths:
            n = ProjectNode(os.path.join(r, p))
            n.file_attrs = {
                'file_name': p,
                'name': os.path.basename(os.path.splitext(p)[0]),
                'extension': (os.path.splitext(p)[-1])[1:],
                'path': r,
                'full_path': n.data,
                'type': ProjectStructureTreeBuilder.ResolveFileType(n.data),
                }
            children.append(n)

        return children

    @staticmethod
    def ResolveFileType(full_path):
        t = None
        if os.path.isdir(full_path):
            t = 'd'
        elif os.path.isfile(full_path):
            t = 'f'
        return t


class CheckerStatus:

    def __init__(self, checker_name, check_result):
        self.checker_name = checker_name
        self.check_result = check_result

    def isSuccessful(self):
        return not self.check_result


class Checker(Visitor):

    """Checker parent class with life cycle methods. To actual checkers need to sub-class
this class with the actual life cycle methods implemented. At least _eval_ should be
implemented.

Life cycle methods:

* eval - called on each node

* evalOnSubTreeEnd - called when all children of current node are processed

* evalOnEnd - called when walking of the tree is finished"""

    def __init__(
        self,
        name,
        vars,
        config,
        ):
        Visitor.__init__(self)
        self.name = name
        self.check_result = []

        # read-only!

        self.vars = vars
        self.config = interpol(vars, config)
        self.current_context = None

    def eval(self, node):
        """Actual rule evaluation. Should return None if successful otherwise a meaningful
           error message. This method is called on each node."""

        return None

    def evalOnEnd(self):
        """Needed for checks which evaluate their results after all files have been walked.
           Should return None if successful otherwise a meaningful error message."""

        return None

    def evalOnSubTreeEnd(self, node):
        """This method is evaluated of all the children of the current node are processed.
           Should return None if successful otherwise a meaningful error message."""

        return None

    @report_info
    def visit(self, node):
        result = self.eval(node)
        if result:
            self.check_result.append(result)

    @report_info
    def post_walk(self):
        result = self.evalOnEnd()
        if result:
            self.check_result.append(result)

    @report_info
    def post_visit(self, node):
        result = self.evalOnSubTreeEnd(node)
        if result:
            self.check_result.append(result)

    def addResult(self, result):
        self.check_result.append((self.current_context, result))

    def getStatus(self):
        return CheckerStatus(self.name, self.check_result)

    def interpolateNode(self, node):
        return interpol(node.file_attrs, self.config)

    def interpolatePathExpression(self, path):
        if path[0:1] == '/':
            return self.vars['project_path'] + path
        else:
            return path


