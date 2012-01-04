#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

star_re = re.compile('(?<!\*)\*{1}(?!\*)')
fname_star_re = re.compile('\*\.([^/\.]+)$')

cache = dict()


def prepare(pattern):
    """Factory method for glob expression classes. This method should be used instead of the constructor, because it
    implements basic caching."""

    if pattern in cache:
        return cache[pattern]
    else:
        gb = GlobMatch(pattern)
        cache[pattern] = gb
        return gb


class GlobMatch:

    def __init__(self, pattern):
        m = fname_star_re.match(pattern)
        if m:
            p = '.*\.{}'.format(m.group(1))
        else:
            p = star_re.sub('[^\/]*', pattern)
            p = p.replace('.', '\.').replace('**', '.*').replace('?', '.')
            if p.find('/') < 0 or p.find('\\') < 0:
                p = '.*{}.*'.format(p)

        self.r = re.compile('^' + p + '$')
        self.p = p
        self.pattern = pattern

    def __str__(self):
        return self.pattern

    def __hash__(self):
        return hash(self.pattern)

    def __cmp__(self, other):
        if self.pattern < other.pattern:
            return -1
        elif self.pattern > other.pattern:
            return 1
        else:
            return 0

    def __eq__(self, other):
        return self.pattern == other.pattern

    def match(self, name):
        return self.r.match(name) != None


