#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import re

import ProjectWalker

# should handle glob expressions in paths


class FileExistsChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.fileCount = {}

        for f in self.getVal('requiredFiles'):
            self.fileCount[self.interpolatePathExpression(f)] = 0

        self.requiredCount = self.getVal('count', -1)[0]

    def eval(self, node):
        result = []
        for f in self.fileCount.iterkeys():

            # handle absolute and relative paths differently

            if f[0:1] == '/':
                attr = 'full_path'
            else:
                attr = 'file_name'
            if f == node.file_attrs[attr]:
                self.fileCount[f] = self.fileCount[f] + 1
        return None

    def evalOnEnd(self):
        for (f, c) in self.fileCount.iteritems():
            if c < 1 and self.requiredCount == -1:
                self.addResult('Could not find file [{}]'.format(f))
            elif c != self.requiredCount and self.requiredCount != -1:
                self.addResult('Found file [{}] {} time(s), required {}.'.format(f, c, self.requiredCount))

class FileContainsChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        if 'caseSensitive' not in config or config['caseSensitive'] == 'true':
            self.caseSensitive = 0
        else:
            self.caseSensitive = re.IGNORECASE

    def eval(self, node):
        current_config = self.interpolateNode(node)
        fpath = node.file_attrs['full_path']
        contains = {}

        for c in self.getVal('contains'):
            contains[c] = {}
            contains[c]['re'] = re.compile(c, self.caseSensitive)
            contains[c]['found'] = False
        try:
            f = open(fpath, 'r')
            for l in f:
                for (c_line, c_vals) in contains.iteritems():
                    if c_vals['re'].search(l):
                        c_vals['found'] = True
                        continue
            for (c_line, c_vals) in contains.iteritems():
                if not c_vals['found']:
                    self.addResult('Could not find line [{}] in file [{}].'.format(c_line, fpath))
        except IOError:
            return self.addResult('Could not open file [{}]'.format(fpath))


class FileNameChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.p = self.getVal('matches')[0]
        self.r = re.compile(self.p)

    def eval(self, node):
        result = []
        n = node.file_attrs['file_name']
        p = node.file_attrs['full_path']
        if not self.r.match(n):
            self.addResult('File [{}] does not match [{}]!'.format(p, self.p))


class FilePropertyChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.encoding = self.getVal('encoding', 'utf8')[0]
        self.ending = self.getVal('lineEnding', 'unix')[0]
        self.whitespace = self.getVal('whitespace', 'space')[0]
        self.trailing = self.getVal('trailingWhitespace', True)[0]
        self.lineLength = self.getVal('lineLength', 120)[0]

        if self.ending == 'unix':
            self.er = re.compile('.*[^\r]\n$')
        else:
            self.er = re.compile('.*\r\n$')
        if self.whitespace == 'space':
            self.sp = '\t'
            self.wopp = 'tab'
        else:
            self.sp = ' '
            self.wopp = 'space'

        self.trr = re.compile('\S*[ \t]+$')

        self.wrongEndingFound = False

    def eval(self, node):
        path = node.file_attrs['full_path']
        try:
            with open(path, 'r') as f:
                i = 0
                for l in f:
                    i = i + 1
                    ll = len(l)
                    if ll > 1 and not self.wrongEndingFound and not self.er.match(l):
                        self.addResult('Line ending of file [{}] is not [{}]!'.format(path, self.ending))
                        self.wrongEndingFound = True
                    chrp = l.find(self.sp)
                    if chrp > -1:
                        self.addResult('[{}] found instead of [{}] in file [{}] in line [{}] at char position [{}]!'.format(self.wopp,
                                       self.whitespace, path, i, chrp))
                    if not self.trailing and ll > 1 and self.trr.match(l):
                        self.addResult('Trailing whitespace found in file [{}] in line [{}]!'.format(path, i))
                    if ll > self.lineLength:
                        self.addResult('Line [{}] in file [{}] is longer than [{}]!'.format(i, path, self.lineLength))
        except IOError:

            self.addResult('Encoding of file [{}] is not [{}]!'.format(path, self.encoding))


