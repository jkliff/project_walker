#!/usr/bin/python
# -*- coding: utf-8 -*-
import fnmatch
import os.path
import re

import ProjectWalker

# should handle glob expressions in paths


class FileExistsChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars,
                config)

        self.fileCount = {}
        self.requiredCount = 1

        for f in config['requiredFiles']:
            self.fileCount[self.interpolatePathExpression(f)] = 0
        if 'count' in config:
            self.requiredCount = config['count']

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
            if c != self.requiredCount:
                if self.requiredCount == 1:
                    self.addResult('Could not find file [{}]'.format(f))
                else:
                    self.addResult('Found file [{}] {} time(s), required {}.'.format(f,
                                   c, self.requiredCount))


class FileContainsChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars,
                config)
        if type(config['matches']) == list:
            matches = config['matches']
        else:
            matches = [config['matches']]
        for match in matches:
            self.addAcceptRule(lambda f: \
                               fnmatch.fnmatch(f.file_attrs['file_name'
                               ], match))

        if 'caseSensitive' not in config or config['caseSensitive'] == 'true':
            self.caseSensitive = 0
        else:
            self.caseSensitive = re.IGNORECASE

    def eval(self, node):
        current_config = self.interpolateNode(node)
        fpath = node.file_attrs['full_path']
        contains = {}

        if type(current_config['contains']) == list:
            contains_config = current_config['contains']
        else:
            contains_config = [current_config['contains']]

        for c in contains_config:
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
                    self.addResult('Could not find line [{}] in file [{}].'.format(c_line,
                                   fpath))
        except IOError:
            return self.addResult('Could not open file [{}]'.format(fpath))


