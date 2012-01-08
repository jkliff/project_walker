#!/usr/bin/python
# -*- coding: utf-8 -*-

import ProjectWalker

import unittest


class SomeChecker(ProjectWalker.Checker):

    def __init__(self, config):
        ProjectWalker.Checker.__init__(self, self.__class__, {}, config)
        self.addOption('files', isList=True, default=[])
        self.addOption('excludeFiles', isList=True, default=[])
        self.parseOptions()
        self.setUpIncludesExcludes(self.files, self.excludeFiles)


class GlobMatchTest(unittest.TestCase):

    def getNode(self, path):
        node = ProjectWalker.ProjectNode(None)
        node.file_attrs['full_path'] = path
        return node

    def test_Accept1(self):
        config = {'files': '*.py'}
        checker = SomeChecker(config)
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux/bal.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))

    def test_Accept2(self):
        config = {'files': ['*.py', '*.md', '*.txt']}
        checker = SomeChecker(config)
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.md')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.png')))

    def test_Deny1(self):
        config = {'excludeFiles': ['*.py', '*.md', '*.txt']}
        checker = SomeChecker(config)
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.md')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))

    def test_Deny2(self):
        config = {'excludeFiles': ['*.py', '*.md', '*.txt']}
        checker = SomeChecker(config)
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.md')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bar/quux.txt')))
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.png')))

    def test_AcceptDeny1(self):
        '''Files which are accepted, but not denied.'''

        config = {'files': ['*.py', '*.md', '*.txt'], 'excludeFiles': ['baz', 'bal']}
        checker = SomeChecker(config)
        self.assertTrue(checker.appliesTo(self.getNode('/foo/bar/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/baz/quux.py')))
        self.assertFalse(checker.appliesTo(self.getNode('/foo/bal/quux.py')))


