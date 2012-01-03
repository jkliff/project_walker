import re

star_re = re.compile('(?<!\*)\*{1}(?!\*)')

cache = dict()

def prepare(pattern):
    p = star_re.sub('[^\/]*', pattern)
    p = p.replace('.', '\.').replace('**', '.*').replace('?', '.')
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
