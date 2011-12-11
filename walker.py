#! /usr/bin/python2.7

import argparse
import os.path
import sys

import ProjectWalker
import Checkers

import argparse

from yaml import load, dump
from string import ljust

CHECKER_STATUS_PADDING = 40

def red(string):
    return '\033[91m' + string + '\033[0m'
def green(string):
    return '\033[92m' + string + '\033[0m'

def load_project (project):
    tree_builder = ProjectWalker.ProjectStructureTreeBuilder ()
    return tree_builder.build (os.path.abspath(project))

def printStatus (status, fullStatus = None):
    if s.isSuccessful ():
        ok_or_fail = green('OK')
    else:
        ok_or_fail = red('FAILED')
    print "{}[{}]".format(ljust(str(s.checker_name), CHECKER_STATUS_PADDING), ok_or_fail)
    if fullStatus:
        for (c, m) in s.check_result:
            print "  * " + m

def isSuccessful (status):
    return all (s.isSuccessful() for s in status)


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

checkers = []
for rule_name, rule_config in config['rules'].iteritems():
    c = getattr (Checkers, rule_name)
    checkers.append(c(config['vars'], rule_config))

checker = ProjectWalker.ProjectCheckEvaluator (load_project(args.project))
status  = checker.walk (checkers)

if not args.quiet:
    for s in status:
        printStatus (s, args.full_report)

if not isSuccessful (status):
    sys.exit("")
