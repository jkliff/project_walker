#! /usr/bin/python2.7

from interpol import interpol
import unittest

class TestInterpol(unittest.TestCase):

    v = {
            'this': 'foo',
            'that': 'bar',
            'other': 'fooquux',
            'other_joo': 'FOOQUUX'
            }

    def test_stringWithOneValue(self):
        self.assertEqual('foo bar', interpol(self.v, '%this bar'))

    def test_stringWithOneValue(self):
        self.assertEqual('FOOQUUX bar', interpol(self.v, '%other_joo bar'))

    def test_stringWithTwoValues(self):
        self.assertEqual('foo bar', interpol(self.v, '%this %that'))

    def test_stringWithEmbeddedValue(self):
        self.assertEqual('foobar', interpol(self.v, '%{this}bar'))

    def test_stringWithTwoEmbeddedValues(self):
        self.assertEqual('foobar', interpol(self.v, '%{this}%{that}'))

    def test_stringSubstringFrom1(self):
        self.assertEqual('o bar', interpol(self.v, '%this:2 bar'))

    def test_stringSubstringFrom2(self):
        self.assertEqual('o bar', interpol(self.v, '%{this:2} bar'))

    def test_stringEmbeddedSubstringFrom1(self):
        self.assertEqual('obar', interpol(self.v, '%this:2bar'))

    def test_stringEmbeddedSubstringFrom2(self):
        self.assertEqual('obar', interpol(self.v, '%{this:2}bar'))

    def test_stringSubstringFromTo1(self):
        self.assertEqual('oqu bar', interpol(self.v, '%other:2:5 bar'))

    def test_stringSubstringFromTo2(self):
        self.assertEqual('oqu bar', interpol(self.v, '%{other:2:5} bar'))

    def test_stringSubstringFromTo3(self):
        self.assertEqual('oquu bar', interpol(self.v, '%{other:2:-1} bar'))

    def test_stringEmbeddedSubstringFromTo1(self):
        self.assertEqual('oqubar', interpol(self.v, '%other:2:5bar'))

    def test_stringEmbeddedSubstringFromTo2(self):
        self.assertEqual('oqubar', interpol(self.v, '%{other:2:5}bar'))

    def test_stringReplacement1(self):
        self.assertEqual('FOOquuxbar', interpol(self.v, '%{other:foo:FOO}bar'))

    def test_stringReplacement2(self):
        self.assertEqual('quuxbar', interpol(self.v, '%{other:foo:}bar'))

if __name__ == '__main__':
    unittest.main ()
