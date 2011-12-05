#!/usr/bin/python

import unittest
import shutil
import os
import os.path

import ProjectWalker

class BasicTest (unittest.TestCase):

    def setUp (self):
        # copy test directory tree

        os.makedirs ('sandbox')
        dst = os.path.join ('sandbox', 'sample')
        src = os.path.join ('resources', 'sample')
        shutil.copytree (src, dst)

    def tearDown (self):
        shutil.rmtree ('sandbox')

    def test_build_all_nodes (self):
        tree_builder = ProjectStructureTreeBuilder ()
        tree = tree_builder.build ('sandbox/sample')

        print 'tree object'
        print tree

    def test_walk_all_nodes (self):
        visitor = InfoGathererVisitor ()
        tree = self.__tree ()
        walker = ProjectWalker.TreeWalker (tree)

        visitor_output = walker.walk (visitor)
        print 'All nodes:'
        print visitor_output.getOutput ()
        print visitor_output.getReport ()

    def test_apply_predicate_dirs (self):
        visitor = InfoGathererVisitor ()
        visitor.addAcceptRule (lambda node: node.file_attrs ['type'] == 'd')

        tree = self.__tree ()
        walker = ProjectWalker.TreeWalker (tree)

        visitor_output = walker.walk (visitor)
        print 'Only directories'
        print visitor_output.getOutput ()
        print visitor_output.getReport ()

    def test_apply_predicate_java_files (self):
        visitor = InfoGathererVisitor ()
        visitor.addAcceptRule (lambda node: node.file_attrs ['type'] != 'd')
        visitor.addDenyRule (lambda node: node.data.endswith ('.java'))

        tree = self.__tree ()
        walker = ProjectWalker.TreeWalker (tree)

        visitor_output = walker.walk (visitor)
        print 'Only non-java files'
        print visitor_output.getOutput ()
        print visitor_output.getReport ()

    def test_evaluate_checker (self):
        check = FileNameContainsNumberCheck ()
        tree = self.__tree ()
        checker = ProjectWalker.ProjectCheckEvaluator (tree)

        check_status = checker.walk (check)
        print check_status

    def test_evaluate_predicated_checker (self):
        check = JavaFileExistsNTimesCheck ()
        tree = self.__tree ()
        checker = ProjectWalker.ProjectCheckEvaluator (tree)

        check_status = checker.walk (check)
        print check_status.getReport ()

    def test_evaluate_parameterized_checker (self):
        #checker = FileContentContainsCharacter ('x')
        pass

    def test_conditional_check_evaluation (self):
        """here we set a check [cost directive is 100 in sql sproc?] to be evaluated only if PREDICATE [sql file contains sproc definition] is True"""
        pass

    def __tree (self):
        tree_builder = ProjectStructureTreeBuilder ()
        return tree_builder.build ('sandbox/sample')



class InfoGathererVisitor (ProjectWalker.Visitor):
    def __init__ (self):
        ProjectWalker.Visitor.__init__ (self)
        self.visited_nodes = []

    def visit (self, n):
        node_data = (n.file_attrs ['full_path'])
        self.visited_nodes.append (node_data)

    def getOutput (self):
        return '\n'.join (self.visited_nodes)

class ProjectNode (ProjectWalker.Node):
    def __init__ (self, root_path):
        ProjectWalker.Node.__init__ (self, root_path)
        self.file_attrs = {}

class ProjectStructureTreeBuilder (ProjectWalker.TreeBuilder):
    def __init__ (self):
        ProjectWalker.TreeBuilder.__init__ (self)

    def build (self, root_path):
        node = ProjectNode (root_path)
        node.file_attrs = {
            'file_name': root_path,
            'path': None,
            'full_path': node.data,
            'type': self.ResolveFileType (node.data)
        }

        return ProjectWalker.TreeBuilder.build (self, node)

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


class Checker (ProjectWalker.Visitor):
    def __init__ (self, name):
        ProjectWalker.Visitor.__init__ (self)
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

import re

class FileNameContainsNumberCheck (Checker):
    def __init__ (self):
        Checker.__init__ (self, 'FileNameContainsNumberCheck')

    def visit (self, node):
        r = re.search ('\d', node.file_attrs ['file_name'])
        if r is not None:
            self.addResult (r is not None)

import fnmatch
# could even inhert from FileNameContainsNumberCheck, but like this is funnier
class JavaFileExistsNTimesCheck (Checker):
    """violation currently fixed for 2 times"""
    def __init__ (self):
        Checker.__init__ (self, 'JavaFileNameContainsNumberCheck')
        self.addAcceptRule (lambda f: fnmatch.fnmatch(f.file_attrs ['file_name'], '*.java'))

    def visit (self, node):
        """yep, this is redundant. just for fun"""
        if fnmatch.fnmatch (node.file_attrs ['file_name'], '*.java'):
            self.check_result.append (node.file_attrs ['file_name'])

if __name__ == '__main__':
    unittest.main ()
