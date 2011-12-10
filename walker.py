#! /usr/bin/python2.7

import argparse
import os.path

import ProjectWalker
import Checkers

import argparse

from yaml import load, dump
from string import ljust

def red(string):
    return '\033[91m' + string + '\033[0m'
def green(string):
    return '\033[92m' + string + '\033[0m'

def __load_project (project):
    tree_builder = ProjectWalker.ProjectStructureTreeBuilder ()
    return tree_builder.build (os.path.abspath(project))

parser = argparse.ArgumentParser(description='Checks a project with a set of rules.')
parser.add_argument('--config', metavar='C', help='configuration file')
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

checker = ProjectWalker.ProjectCheckEvaluator (__load_project(args.project))
for c in checkers:
    status = checker.walk(c)
    if status:
        ok_or_fail = red('FAILED')
    else:
        ok_or_fail = green('OK')
    print "{}[{}]".format(ljust(str(c.__class__), 40), ok_or_fail)
    # print status.getOutput()
