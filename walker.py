#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os.path
import sys

import ProjectWalker
import Checkers

from yaml import load
from string import ljust, rjust

CHECKER_STATUS_PADDING = 40
COUNTS_PADDING = 8
DEFAULT_CONFIG_NAME = 'walker.conf'

IS_TERMINAL = sys.stdout.isatty()

def red(string):
    if IS_TERMINAL:
        return '\033[91m' + string + '\033[0m'
    else:
        return string


def green(string):
    if IS_TERMINAL:
        return '\033[92m' + string + '\033[0m'
    else:
        return string


def load_project(project):
    tree_builder = ProjectWalker.ProjectStructureTreeBuilder()
    return tree_builder.build(os.path.abspath(project))


def print_status(name, status, full_status=None):
    failed_check_count = 0
    check_count = 0
    short_status = ''
    long_status = ''

    messages = []
    for s in status:
        if not s.isSuccessful():
            failed_check_count = failed_check_count + 1
        check_count = check_count + 1

        if full_status:
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

    short_status = '{} {} [{}]'.format(ljust(str(name), CHECKER_STATUS_PADDING), rjust(counts, COUNTS_PADDING),
                                       ok_or_fail)

    print short_status
    if full_status:
        print long_status


def is_successful(status):
    return all(s.isSuccessful() for s in status)


def create_checkers(config):
    vars = config['vars']
    rules = config['rules']

    checkers = []
    for (rule_name, rule_config) in rules.iteritems():
        if type(rule_config) == dict:
            rc = [rule_config]
        elif type(rule_config) == list:
            rc = rule_config
        elif rule_config == None:
            rc = [{}]
        else:
            sys.exit('Invalid config [{}]'.format(rule_name))

        for ct in rc:
            if 'excludeFiles' in config:
                add_global_exclude(ct, config['excludeFiles'])
            c = getattr(Checkers, rule_name)
            checkers.append(c(vars, ct))

    return checkers

def add_global_exclude(config, exclude = None):
    if exclude:
        if type(exclude) != list:
            exclude = [exclude]
        if 'excludeFiles' in config:
            if type(config['excludeFiles']) == list:
                ex = config['excludeFiles']
            else:
                ex = [config['excludeFiles']]
            ex.extend(exclude)
        else:
            config['excludeFiles'] = exclude


def list_checkers():
    for c, t in Checkers.__dict__.iteritems():
        if c.endswith('Checker') and issubclass(t, ProjectWalker.Checker):
            print c


def group_status(status):
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
        path = os.path.join(os.path.abspath(projectPath), DEFAULT_CONFIG_NAME)

    with open(path, 'r') as f:
        config = load(f)

    return config


def main():
    parser = argparse.ArgumentParser(description='Checks a project with a set of rules.')
    parser.add_argument('-p', '--project', default='.', help='project directory')
    parser.add_argument('-c', '--config', help='configuration file')
    parser.add_argument('-q', '--quiet', action='store_true', help='do not print anything')
    parser.add_argument('-f', '--full-report', action='store_true', help='prints full report')
    parser.add_argument('-l', '--list-checkers', action='store_true', help='lists all checkers')
    args = parser.parse_args()

    if (args.list_checkers):
        list_checkers();
        sys.exit('')

    config = loadConfig(args.project, args.config)
    if not config:
        sys.exit('Could not find config [{}] in project directory [{}]!'.format(args.config, args.project))

    if 'vars' not in config:
        config['vars'] = {}

    config['vars']['project_path'] = os.path.abspath(args.project)
    config['vars']['project'] = os.path.basename(os.path.abspath(args.project))

    checker = ProjectWalker.ProjectCheckEvaluator(load_project(args.project))
    checkers = create_checkers(config)
    status = checker.walk(checkers)

    if not args.quiet:
        grouped = group_status(status)
        for n in sorted(grouped.iterkeys(), reverse=True):
            s = grouped[n]
            print_status(n, s, args.full_report)

    if not is_successful(status):
        sys.exit('')


if __name__ == '__main__':
    main()
