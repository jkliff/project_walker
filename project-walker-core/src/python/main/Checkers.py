#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import re
import subprocess

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except:
        import elementtree.ElementTree as etree

import ProjectWalker
import GlobMatch
from interpol import interpol


class MavenPomChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.addOption('mavenVersion', default=2)
        self.addOption('useParent', default=False)
        self.addOption('usePackaging', default=False)
        self.addOption('versionInDependencies', default=True)
        self.addOption('dependencyVersions', default=[])

        self.addAcceptRule(lambda f: f.file_attrs['file_name'] == 'pom.xml')

    def eval(self, node):
        ns = {'p': 'http://maven.apache.org/POM/4.0.0'}
        path = node.file_attrs['full_path']
        with open(path) as f:
            doc = etree.parse(f)
            if self.useParent:
                parent = doc.getroot().xpath('/p:project/p:parent', namespaces=ns)
                if parent == []:
                    self.addResult('No parent pom defined in [{}]!'.format(path))
            if self.usePackaging:
                packaging = doc.getroot().xpath('/p:project/p:packaging', namespaces=ns)
                if packaging == []:
                    self.addResult('No packaging defined in [{}]!'.format(path))
            if self.dependencyVersions and not self.dependencyVersions['versionsAllowed']:
                ex_res = []
                for d in doc.getroot().xpath('/p:project/p:dependencies/p:dependency', namespaces=ns):
                    artifact = d.xpath('p:artifactId', namespaces=ns)[0].text

                    if self.__isExcluded(artifact):
                        continue

                    if d.xpath('p:version', namespaces=ns):
                        self.addResult('Version used in [{}] for artifact [{}]!'.format(path, artifact))

    def __isExcluded(self, artifact):
        if 'excludeArtifact' not in self.dependencyVersions:
            return False

        if 'excludeRegexes' in self.dependencyVersions:
            res = self.dependencyVersions['excludeRegexes']
        else:
            res = []
            patterns = []
            ea = self.dependencyVersions['excludeArtifact']
            if type(ea) == list:
                patterns = ea
            else:
                patterns.append(ea)

            for p in patterns:
                res.append(re.compile('^{}$'.format(p)))
            self.dependencyVersions['excludeRegexes'] = res

        for r in res:
            if r.match(artifact):
                return True

        return False


class ExternalChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.addOption('files', isList=True, default=[])
        self.addOption('excludeFiles', isList=True, default=[])
        self.addOption('command', isList=True)
        self.parseOptions()
        self.setUpIncludesExcludes(self.files, self.excludeFiles)

        self.cmds = []
        for tcmd in self.command:
            self.cmds.append(interpol(vars, tcmd))

    def eval(self, node):
        for cmd in self.cmds:
            self.addResult(self.callCommand(interpol(node.file_attrs, cmd)))

    def callCommand(self, cmd):
        try:
            subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
            return None
        except subprocess.CalledProcessError, e:
            return e.output
        except:
            return 'Unknown error occured on calling [{}]'.format(cmd)


class FileExistsChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.fileCount = {}

        self.addOption('requiredFiles', isList=True)
        self.addOption('count', default=-1)
        self.parseOptions()

        for f in self.requiredFiles:
            self.fileCount[GlobMatch.prepare(self.interpolatePathExpression(f))] = 0

    def eval(self, node):
        result = []
        for gb in self.fileCount.iterkeys():

            # handle absolute and relative paths differently

            if gb.match(node.file_attrs['full_path']):
                self.fileCount[gb] = self.fileCount[gb] + 1
        return None

    def evalOnEnd(self):
        for (f, c) in self.fileCount.iteritems():
            if c < 1 and self.count == -1:
                self.addResult('Could not find file [{}]'.format(f))
            elif c != self.count and self.count != -1:
                self.addResult('Found file [{}] {} time(s), required {}.'.format(f, c, self.count))


class FileContainsChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.addOption('files', isList=True, default=[])
        self.addOption('excludeFiles', isList=True, default=[])
        self.addOption('caseSensitive', default=True)
        self.parseOptions()
        self.setUpIncludesExcludes(self.files, self.excludeFiles)

        if self.caseSensitive:
            self.reOption = 0
        else:
            self.reOption = re.IGNORECASE

    def eval(self, node):
        current_config = self.interpolateNode(node)
        fpath = node.file_attrs['full_path']
        contains = {}

        for c in current_config['contains']:
            contains[c] = {}
            contains[c]['re'] = re.compile(c, self.reOption)
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

        self.addOption('files', isList=True, default=[])
        self.addOption('excludeFiles', isList=True, default=[])
        self.addOption('matches')
        self.parseOptions()
        self.setUpIncludesExcludes(self.files, self.excludeFiles)

        self.r = re.compile(self.matches)

    def eval(self, node):
        result = []
        n = node.file_attrs['file_name']
        p = node.file_attrs['full_path']
        if not self.r.match(n):
            self.addResult('File [{}] does not match [{}]!'.format(p, self.matches))


class FilePropertyChecker(ProjectWalker.Checker):

    def __init__(self, vars, config):
        ProjectWalker.Checker.__init__(self, self.__class__, vars, config)

        self.addOption('files', isList=True, default=[])
        self.addOption('excludeFiles', isList=True, default=[])
        self.addOption('encoding', default='utf8')
        self.addOption('lineEnding', default='unix')
        self.addOption('whitespace', default='space')
        self.addOption('trailingWhitespace', default=True)
        self.addOption('lineLength', default=120)
        self.parseOptions()
        self.setUpIncludesExcludes(self.files, self.excludeFiles)

        if self.lineEnding == 'unix':
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

        self.addDenyRule(lambda f: f.file_attrs['type'] == 'd')

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
                    if not self.trailingWhitespace and ll > 1 and self.trr.match(l):
                        self.addResult('Trailing whitespace found in file [{}] in line [{}]!'.format(path, i))
                    if ll > self.lineLength:
                        self.addResult('Line [{}] in file [{}] is longer than [{}]!'.format(i, path, self.lineLength))
        except IOError:

            self.addResult('Encoding of file [{}] is not [{}]!'.format(path, self.encoding))


