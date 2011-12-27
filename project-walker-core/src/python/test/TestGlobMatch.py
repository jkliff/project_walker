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
        gb = GlobMatch.prepare('foo.py')
        self.assertTrue(gb.match('foo.py'))

    def test_AZMatch(self):
        gb = GlobMatch.prepare('[a-z]*.py')
        self.assertTrue(gb.match('foo.py'))

    def test_QuestionMarkMatch(self):
        gb = GlobMatch.prepare('???.py')
        self.assertTrue(gb.match('foo.py'))

    def test_OneSlash1(self):
        gb = GlobMatch.prepare('*/???.py')
        self.assertTrue(gb.match('bar/foo.py'))

    def test_OneSlash2(self):
        gb = GlobMatch.prepare('/*/???.py')
        self.assertTrue(gb.match('//foo.py'))

    def test_TwoSlash1(self):
        gb = GlobMatch.prepare('**/foo.py')
        self.assertTrue(gb.match('quux/bar/foo.py'))

    def test_TwoSlash2(self):
        gb = GlobMatch.prepare('**')
        self.assertTrue(gb.match('quux/bar/foo.py'))

    def test_TwoSlash3(self):
        gb = GlobMatch.prepare('**/*.py')
        self.assertTrue(gb.match('quux/bar/foo.py'))

    def test_TwoSlash4(self):
        gb = GlobMatch.prepare('**/*.txt')
        self.assertFalse(gb.match('quux/bar/foo.py'))

    def test_Alternation(self):
        gb = GlobMatch.prepare('**/*.(py|txt)')
        self.assertTrue(gb.match('quux/bar/foo.py'))
        self.assertTrue(gb.match('quux/bar/foo.txt'))

if __name__ == '__main__':
    unittest.main()
