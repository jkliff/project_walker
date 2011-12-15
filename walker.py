#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os.path
import sys

import ProjectWalker
import Checkers

import argparse

from yaml import load, dump
from string import ljust, rjust

CHECKER_STATUS_PADDING = 40
COUNTS_PADDING = 8
DEFAULT_CONFIG_NAME = 'walker.conf'


def red(string):
    return '\033[91m' + string + '\033[0m'


def green(string):
    return '\033[92m' + string + '\033[0m'


def load_project(project):
    tree_builder = ProjectWalker.ProjectStructureTreeBuilder()
    return tree_builder.build(os.path.abspath(project))


def printStatus(name, status, fullStatus=None):
    failed_check_count = 0
    check_count = 0
    short_status = ''
    long_status = ''

    for s in status:
        if not s.isSuccessful():
            failed_check_count = failed_check_count + 1
        check_count = check_count + 1

        if fullStatus:
            messages = []
            for (c, m) in s.check_result:
                messages.append('  * ' + m)
            long_status = '\n'.join(messages)

    if failed_check_count == 0:
        ok_or_fail = green('OK')
    else:
        ok_or_fail = red('FAILED')

    if check_count == 1:
        counts = ''
    else:
        counts = '{}/{}'.format(failed_check_count, check_count)

    short_status = '{} {} [{}]'.format(ljust(str(name),
            CHECKER_STATUS_PADDING), rjust(counts, COUNTS_PADDING),
            ok_or_fail)

    print short_status
    if fullStatus:
        print long_status


def isSuccessful(status):
    return all(s.isSuccessful() for s in status)


def createCheckers(rules, vars):
    checkers = []
    for rule in rules:
        for (rule_name, rule_config) in rule.iteritems():
            c = getattr(Checkers, rule_name)
            checkers.append(c(vars, rule_config))
    return checkers


def groupStatus(status):
    grouped = {}
    for s in status:
        name = s.checker_name
        if name in grouped:
            grouped[name].append(s)
        else:
            grouped[name] = [s]
    return grouped


def loadConfig(projectPath, configName):
    config = None
    if configName:
        path = configName
    else:
        path = os.path.join(os.path.abspath(projectPath),
                            DEFAULT_CONFIG_NAME)

    with open(path, 'r') as f:
        config = load(f)

    return config


def main():
    parser = \
        argparse.ArgumentParser(description='Checks a project with a set of rules.'
                                )
    parser.add_argument('-p', '--project', default='.',
                        help='project directory')
    parser.add_argument('-c', '--config', help='configuration file')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='do not print anything')
    parser.add_argument('-f', '--full-report', action='store_true',
                        help='prints full report')
    args = parser.parse_args()

    config = loadConfig(args.project, args.config)
    if not config:
        sys.exit('Could not find config [{}] in project directory [{}]!'.format(args.config,
                 args.project))

    if 'vars' not in config:
        config['vars'] = {}

    config['vars']['project_path'] = os.path.abspath(args.project)
    config['vars']['project'] = \
        os.path.basename(os.path.abspath(args.project))

    checker = \
        ProjectWalker.ProjectCheckEvaluator(load_project(args.project))
    checkers = createCheckers(config['rules'], config['vars'])
    status = checker.walk(checkers)

    if not args.quiet:
        for (n, s) in groupStatus(status).items():
            printStatus(n, s, args.full_report)

    if not isSuccessful(status):
        sys.exit('')


if __name__ == '__main__':
    main()
