#!/usr/bin/python
# -*- coding: utf-8 -*-

import GlobMatch
import unittest


class GlobMatchTest(unittest.TestCase):

    def test_matchAll(self):
        gb = GlobMatch.prepare('*')
        self.assertTrue(gb.match('foo.py'))

    def test_matchExtension(self):
        gb = GlobMatch.prepare('*.py')
        self.assertTrue(gb.match('foo.py'))

    def test_matchFail(self):
        gb = GlobMatch.prepare('*.txt')
        self.assertFalse(gb.match('foo.py'))

    def test_exactMatch(self):
        gb = GlobMatch.prepare('/foo/bar.py')
        self.assertTrue(gb.match('/foo/bar.py'))

    def test_matchWithoutSlashMatchesStringEverywhere1(self):
        gb = GlobMatch.prepare('bar.py')
        self.assertTrue(gb.match('/foo/bar.py'))

    def test_matchWithoutSlashMatchesStringEverywhere2(self):
        gb = GlobMatch.prepare('bar.py')
        self.assertTrue(gb.match('bar.py'))

    def test_matchWithoutSlashMatchesStringEverywhere3(self):
        gb = GlobMatch.prepare('.git')
        self.assertTrue(gb.match('/home/pele/dev/project_walker/.git/logs/refs/heads/walk'))

    def test_matchWithoutSlashMatchesStringEverywhere4(self):
        gb = GlobMatch.prepare('*.pyc')
        self.assertTrue(gb.match('/home/pele/dev/project_walker/project-walker-core/src/python/test/TestGlobMatch.pyc'))

    def test_AZMatch(self):
        gb = GlobMatch.prepare('[a-z]*.py')
        self.assertTrue(gb.match('foo.py'))

    def test_QuestionMarkMatch(self):
        gb = GlobMatch.prepare('???.py')
        self.assertTrue(gb.match('foo.py'))

    def test_OneStar1(self):
        gb = GlobMatch.prepare('*/???.py')
        self.assertTrue(gb.match('bar/foo.py'))

    def test_OneStar2(self):
        gb = GlobMatch.prepare('/*/???.py')
        self.assertTrue(gb.match('//foo.py'))

    def test_TwoStars1(self):
        gb = GlobMatch.prepare('**/foo.py')
        self.assertTrue(gb.match('quux/bar/foo.py'))

    def test_TwoStars2(self):
        gb = GlobMatch.prepare('**')
        self.assertTrue(gb.match('quux/bar/foo.py'))

    def test_TwoStars3(self):
        gb = GlobMatch.prepare('**/*.py')
        self.assertTrue(gb.match('quux/bar/foo.py'))

    def test_TwoStars4(self):
        gb = GlobMatch.prepare('**/*.txt')
        self.assertFalse(gb.match('quux/bar/foo.py'))

    def test_TwoStars5(self):
        gb = GlobMatch.prepare('**/.git/**')
        self.assertTrue(gb.match('/home/pele/dev/project_walker/.git/objects/18/f545826e02129f7a729e95a2f9ea37c9779c7a'
                        ))

    def test_TwoStars6(self):
        gb = GlobMatch.prepare('**/.git')
        self.assertFalse(gb.match('/home/pele/dev/project_walker/.git/objects/18/f545826e02129f7a729e95a2f9ea37c9779c7a'
                         ))

    def test_Alternation(self):
        gb = GlobMatch.prepare('**/*.(py|txt)')
        self.assertTrue(gb.match('quux/bar/foo.py'))
        self.assertTrue(gb.match('quux/bar/foo.txt'))


if __name__ == '__main__':
    unittest.main()
