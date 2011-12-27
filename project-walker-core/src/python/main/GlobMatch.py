import re

star_re = re.compile('(?<!\*)\*{1}(?!\*)')

def prepare(pattern):
    p = star_re.sub('[^\/]*', pattern)
    p = p.replace('.', '\.').replace('**', '.*').replace('?', '.')
    return GlobMatch(p)

class GlobMatch:

    def __init__(self, p):
        self.r = re.compile(p)

    def match(self, name):
        return self.r.match(name) != None
