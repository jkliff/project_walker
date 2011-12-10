import fnmatch
import os.path
import re

import ProjectWalker

class FileExistsChecker (ProjectWalker.Checker):

    fileCount = {}

    def __init__ (self, vars, config):
        ProjectWalker.Checker.__init__ (self, self.__class__, vars, config)
        for f in config['requiredFiles']:
            self.fileCount[f] = 0

    def eval (self, node):
        result = []
        for f in self.fileCount.iterkeys():
            if f == node.file_attrs['full_path']:
                self.fileCount[f] = self.fileCount[f] + 1
        return None

    def walkFinished(self):
        for f, c in self.fileCount.iteritems():
            if c == 0:
                self.addResult("Could not find file [{}]".format(f))

class FileContainsChecker (ProjectWalker.Checker):
    def __init__ (self, vars, config):
        ProjectWalker.Checker.__init__ (self, self.__class__, vars, config)
        self.addAcceptRule (lambda f: fnmatch.fnmatch(f.file_attrs ['file_name'], config['matches']))

    def eval (self, node):
        current_confing = self.interpolateNode(node)
        fpath = node.file_attrs['full_path']
        contains = {}
        for c in current_confing['contains']:
            contains[c] = {}
            contains[c]['re'] = re.compile(c)
            contains[c]['found'] = False
        try:
            f = open(fpath, 'r')
            for l in f:
                for c_line, c_vals in contains.iteritems():
                    if c_vals['re'].search(l):
                        c_vals['found'] = True
                        continue
            for c_line, c_vals in contains.iteritems():
                if not c_vals['found']:
                    self.addResult("Could not find line [{}] in file [{}].".format(c_line, fpath))
        except IOError:
            return self.addResult("Could not open file [{}]".format(fpath))
