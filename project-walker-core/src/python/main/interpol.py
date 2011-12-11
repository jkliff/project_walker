#! /usr/bin/python2.7

import re

def _interpol_str(var, string):
    keys = var.keys()
    keys.sort(key=len, reverse=True)
    for k in keys:
        v = var[k]

        # %identifier:foo:bar - replace foo to bar in string
        r = re.compile('%\{' + k + ':([a-zA-Z]+):([^}]*)\}')
        m = r.match(string)
        if m:
            nv = re.sub(m.group(1), m.group(2), v)
            string = r.sub(nv, string)

        # %identifier:2:5
        r = re.compile('%\{?' + k + ':(-?\d+):(-?\d+)\}?')
        m = r.match(string)
        if m:
            string = r.sub(v[int(m.group(1)):int(m.group(2))], string)

        # %identifier:2
        r = re.compile('%\{?' + k + ':(-?\d+)\}?')
        m = r.match(string)
        if m:
            string = r.sub(v[int(m.group(1)):], string)

        # simplest pattern
        string = re.sub('%\{?' + k + '\}?', str(v), string)

    return string

def _interpol_set(var, st):
    r = set()
    for s in st:
        r.add(interpol(var, s))
    return r

def _interpol_dct(var, dct):
    for k, v in dct.iteritems():
        dct[k] = interpol(var, v)
    return dct

def _interpol_lst(var, lst):
    for i in range(len(lst)):
        lst[i] = interpol(var, lst[i])
    return lst

def interpol(var,v):
    """Interpolates variables in ``var`` into value ``v``. The following forms are substituted:

       * %identifier
       * %{identifier} - for embedding in strings
       * %identifier:2 - from second character on
       * %identifier:2:3 - from second character two third
       * %{identifier:foo:bar} - replace foo to bar in string

       All identifiers support curly braces where the pattern is embedded in another string.
    """
    if not var or not v:
        return v

    m = { dict: _interpol_dct,
          list: _interpol_lst,
          set: _interpol_set,
          str: _interpol_str }
    if type(v) in m:
        return m[type(v)](var, v);
    else:
        return v
