#!/usr/bin/python
# -*- coding: utf-8 -*-
import DictConfig

import unittest


class Person:

    pass


class TestDictConfig(unittest.TestCase):

    def setUp(self):
        self.person = Person()
        self.parser = DictConfig.forObj(self.person)

    def test_Required(self):
        config = {'name': 'John Doe'}
        self.parser.addOption('name', isList=False)
        self.parser.parse(config)

        self.assertEquals('John Doe', self.person.name)

    def test_RequiredNotSet(self):
        config = {}
        self.parser.addOption('name', isList=False)
        with self.assertRaises(DictConfig.OptionException):
            self.parser.parse(config)

    def test_RequiredWithDefault(self):
        config = {}

        self.parser.addOption('name', default='John Doe', isList=False)
        self.parser.parse(config)

        self.assertEquals('John Doe', self.person.name)

    def test_Optional(self):
        config = {'name': 'John Doe'}
        self.parser.addOption('name', isList=False)
        self.parser.addOption('age', isRequired=False, isList=False)
        self.parser.addOption('isMale', isRequired=False, default=False, isList=False)

        self.parser.parse(config)

        self.assertEquals('John Doe', self.person.name)
        self.assertIsNone(self.person.age)
        self.assertFalse(self.person.isMale)

    def test_RemoveChars(self):
        self.parser.removeChars = '-_'

        config = {'n-a__m-e': 'John Doe'}
        self.parser.addOption('name', isList=False)
        self.parser.parse(config)
        self.assertEquals('John Doe', self.person.name)

    def test_CaseInsensitive(self):
        self.parser.isCaseSensitive = False

        config = {'NaMe': 'John Doe'}
        self.parser.addOption('name', isList=False)
        self.parser.parse(config)
        self.assertEquals('John Doe', self.person.name)

    def test_LongestTokenMatch(self):
        self.parser.isLongestTokenMatch = True

        config = {'n': 'John Doe'}
        self.parser.addOption('name', isList=False)
        self.parser.parse(config)
        self.assertEquals('John Doe', self.person.name)

    def test_List1(self):
        emails = ['jd@foo.com', 'john.doe@foo.com']

        config = {'name': 'John Doe', 'emails': emails}
        self.parser.addOption('name', isList=False)
        self.parser.addOption('emails')
        self.parser.parse(config)

        self.assertEquals('John Doe', self.person.name)
        self.assertEquals(list, type(self.person.emails))
        self.assertEquals(emails, self.person.emails)

    def test_List2(self):
        config = {'name': 'John Doe', 'emails': 'jd@foo.com'}
        self.parser.addOption('name', isList=False)
        self.parser.addOption('emails')
        self.parser.parse(config)

        self.assertEquals('John Doe', self.person.name)
        self.assertEquals(list, type(self.person.emails))
        self.assertEquals(['jd@foo.com'], self.person.emails)


