#!/usr/bin/python
# -*- coding: utf-8 -*-


def forObj(obj):
    return DictConfigParser(obj)


class DictConfigParser:

    def __init__(
        self,
        obj,
        isCaseSensitive=True,
        removeChars=None,
        isLongestTokenMatch=False,
        ):
        self.obj = obj
        self.options = []
        self.isCaseSensitive = isCaseSensitive
        self.removeChars = removeChars
        self.isLongestTokenMatch = isLongestTokenMatch

    def addOption(
        self,
        name,
        isRequired=True,
        default=None,
        description=None,
        isList=True,
        ):
        self.options.append(DictOption(name, isRequired, default, description, isList))

    def parse(self, config):
        for option in self.options:
            val = self.__getVal(option.name, config)
            if not val and option.hasDefault():
                val = option.default
            elif not val and not option.hasDefault() and option.isRequired:
                raise OptionException('option [{}] isRequired in [{}] but not present'.format(option.name, self.obj))

            if option.isList and type(val) != list:
                val = [val]

            self.obj.__dict__[option.name] = val

    def __getVal(self, name, config):
        if self.isCaseSensitive and not self.removeChars and not self.isLongestTokenMatch:
            if name in config:
                return config[name]
            else:
                return None
        else:
            val = None
            for (ckey, cval) in config.iteritems():
                key = ckey
                if not self.isCaseSensitive:
                    name = name.lower()
                    key = ckey.lower()

                if self.removeChars:
                    for c in self.removeChars:
                        key = key.replace(c, '')

                if self.isLongestTokenMatch:
                    if name.find(key) == 0:
                        val = config[ckey]
                        break
                else:
                    if key == name:
                        val = config[ckey]
                        break

            return val


class DictOption:

    def __init__(
        self,
        name,
        isRequired,
        default,
        description,
        isList,
        ):
        self.name = name
        self.isRequired = isRequired
        self.default = default
        self.description = description
        self.isList = isList

    def hasDefault(self):
        return self.default != None

    def __str__(self):
        return '{}: {} [{}]'.format(name, description, default)


class OptionException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


