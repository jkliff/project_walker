#!/usr/bin/python
# -*- coding: utf-8 -*-
import Checkers
import ProjectWalker

import unittest


class GlobMatchTest(unittest.TestCase):

    def getNode(self, path):
        node = ProjectWalker.ProjectNode(None)
        node.file_attrs['full_path'] = path
        return node

    def test_Accept1(self):
        config = {'files': '*.py'}
        checker = Checkers.FileContainsChecker({}, config)
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux/bal.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))

    def test_Accept2(self):
        config = {'files': ['*.py', '*.md', '*.txt']}
        checker = Checkers.FileContainsChecker({}, config)
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.md')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.png')))

    def test_Deny1(self):
        config = {'excludeFiles': ['*.py', '*.md', '*.txt']}
        checker = Checkers.FileContainsChecker({}, config)
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.md')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))

    def test_Deny2(self):
        config = {'excludeFiles': ['*.py', '*.md', '*.txt']}
        checker = Checkers.FileContainsChecker({}, config)
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.md')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.png')))

    def test_AcceptDeny1(self):
        '''Files which are accepted, but not denied.'''

        config = {'files': ['*.py', '*.md', '*.txt'], 'excludeFiles': ['baz', 'bal']}
        checker = Checkers.FileContainsChecker({}, config)
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/baz/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bal/quux.py')))


