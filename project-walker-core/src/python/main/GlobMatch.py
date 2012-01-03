#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

star_re = re.compile('(?<!\*)\*{1}(?!\*)')
fname_star_re = re.compile('\*\.([^/\.]+)$')

cache = dict()


def prepare(pattern):
    m = fname_star_re.match(pattern)
    if m:
        p = '.*\.{}'.format(m.group(1))
    else:
        p = star_re.sub('[^\/]*', pattern)
        p = p.replace('.', '\.').replace('**', '.*').replace('?', '.')
        if p.find('/') < 0 or p.find('\\') < 0:
            p = '.*{}.*'.format(p)
    if p in cache:
        return cache[p]
    else:
        gb = GlobMatch(p)
        cache[p] = gb
        return gb


class GlobMatch:

    def __init__(self, p):
        self.r = re.compile('^' + p + '$')
        self.p = p

    def match(self, name):
        return self.r.match(name) != None


