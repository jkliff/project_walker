#! /usr/bin/python2.7

import argparse
import os.path
import sys

import ProjectWalker
import Checkers

import argparse

from yaml import load, dump
from string import ljust
from itertools import groupby

CHECKER_STATUS_PADDING = 40

def red(string):
    return '\033[91m' + string + '\033[0m'
def green(string):
    return '\033[92m' + string + '\033[0m'

def load_project (project):
    tree_builder = ProjectWalker.ProjectStructureTreeBuilder ()
    return tree_builder.build (os.path.abspath(project))

def printStatus (name, status, fullStatus = None):
    if isSuccessful (status):
        ok_or_fail = green('OK')
    else:
        ok_or_fail = red('FAILED')
    print "{}[{}]".format(ljust(str(name), CHECKER_STATUS_PADDING), ok_or_fail)
    if fullStatus:
        for s in status:
            for (c, m) in s.check_result:
                print "  * " + m

def isSuccessful (status):
    return all (s.isSuccessful() for s in status)

def createCheckers (rules, vars):
    checkers = []
    for rule in rules:
        for rule_name, rule_config in rule.iteritems():
            c = getattr (Checkers, rule_name)
            checkers.append(c(vars, rule_config))
    return checkers

def groupStatus (status):
    grouped = {}
    for s in status:
        name = s.checker_name
        if name in grouped:
            grouped[name].append (s)
        else:
            grouped[name] = [s]
    return grouped

parser = argparse.ArgumentParser(description='Checks a project with a set of rules.')
parser.add_argument('-c', '--config', help='configuration file')
parser.add_argument('-q', '--quiet', action='store_true', help='do not print anything')
parser.add_argument('-f', '--full-report', action='store_true', help='prints full report')
parser.add_argument('project', metavar='P', help='project to check')
args = parser.parse_args()

config = load(open(args.config, 'r'))

if 'vars' not in config:
    config['vars'] = {}

config['vars']['project_path'] = os.path.abspath(args.project)
config['vars']['project'] = os.path.basename(os.path.abspath(args.project))


checker = ProjectWalker.ProjectCheckEvaluator (load_project(args.project))
checkers = createCheckers (config['rules'], config['vars'])
status  = checker.walk (checkers)

if not args.quiet:
    for n, s in groupStatus (status).iteritems():
        printStatus (n, s, args.full_report)

if not isSuccessful (status):
    sys.exit("")
